#!/usr/bin/env python3
"""Generate optional English editorial fields without overwriting manual English.

The state sidecar distinguishes generated English from manual content. Publication
sources and resolved citation metadata are intentionally absent from FILE_RULES.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable

import yaml

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "_translation" / "state.yml"
STYLE_PATH = ROOT / "TRANSLATION_STYLE.md"

# Only these editorial field stems can be translated. Names, official site identity,
# identifiers, URLs, chemical formulae and all publication records are excluded.
FILE_RULES: tuple[tuple[str, set[str]], ...] = (
    ("_data/homepage.yaml", {"eyebrow", "title", "text", "alt", "caption", "highlights_heading", "events_heading"}),
    ("_data/site.yaml", {"address", "copyright", "description"}),
    ("_news/*.md", {"title", "summary", "alt"}),
    ("_events/*.md", {"title", "location", "description", "alt"}),
    ("_research/*.md", {"title", "alt", "short_intro"}),
    ("_members/*.md", {"position", "portrait_alt", "research_summary", "affiliation", "address", "profile_summary", "research_interests", "education", "personal_note"}),
    ("_opportunities/*.md", {"title", "content", "label"}),
)


def digest(value: str) -> str:
    return hashlib.sha256(value.strip().encode("utf-8")).hexdigest()


def is_blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def load_content(path: Path) -> tuple[dict[str, Any], str | None]:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".md":
        match = re.match(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)(.*)\Z", text, re.S)
        if not match:
            raise ValueError(f"{path.relative_to(ROOT)} has no YAML front matter")
        return yaml.safe_load(match.group(1)) or {}, match.group(2)
    return yaml.safe_load(text) or {}, None


def save_content(path: Path, data: dict[str, Any], body: str | None) -> None:
    rendered = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=1000)
    if body is None:
        path.write_text(rendered, encoding="utf-8")
    else:
        path.write_text(f"---\n{rendered}---\n{body}", encoding="utf-8")


def walk_pairs(value: Any, allowed: set[str], prefix: str = "") -> Iterable[tuple[dict[str, Any], str, str, str]]:
    if isinstance(value, dict):
        for key in list(value):
            if not isinstance(key, str) or not key.endswith("_zh"):
                continue
            stem = key[:-3]
            en_key = f"{stem}_en"
            # Pages CMS omits optional blank fields from YAML instead of saving
            # them as an empty string. A Chinese field is therefore a valid
            # translation candidate even when its English sibling is absent.
            if stem in allowed and not is_blank(value.get(key)):
                path = f"{prefix}.{stem}" if prefix else stem
                yield value, key, en_key, path
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            yield from walk_pairs(child, allowed, path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_pairs(child, allowed, f"{prefix}[{index}]")


@dataclass
class TranslationResult:
    changed_content: bool = False
    changed_state: bool = False
    generated: int = 0
    refreshed: int = 0
    manual: int = 0
    needs_review: int = 0
    pending: int = 0
    pruned: int = 0


def prune_deleted_entries(
    entries: dict[str, Any],
    active_paths: set[str],
    result: TranslationResult,
) -> None:
    """Remove translation state for CMS records that no longer exist."""
    stale_paths = sorted(set(entries) - active_paths)
    for relative in stale_paths:
        del entries[relative]
    if stale_paths:
        result.pruned += len(stale_paths)
        result.changed_state = True


def process_pair(
    container: dict[str, Any],
    zh_key: str,
    en_key: str,
    field_state: dict[str, Any],
    translator: Callable[[str], str] | None,
    result: TranslationResult,
) -> None:
    source = str(container[zh_key]).strip()
    english = "" if is_blank(container.get(en_key)) else str(container[en_key]).strip()
    source_hash = digest(source)
    english_hash = digest(english) if english else ""
    status = str(field_state.get("status", ""))
    previous_source_hash = str(field_state.get("source_hash", ""))
    generated_hash = str(field_state.get("generated_hash", ""))

    if not english:
        if translator is None:
            field_state.update({"status": "pending", "source_hash": source_hash})
            result.pending += 1
            result.changed_state = True
            return
        translated = translator(source).strip()
        if not translated:
            raise RuntimeError(f"translator returned empty text for {en_key}")
        container[en_key] = translated
        field_state.update({"status": "auto", "source_hash": source_hash, "generated_hash": digest(translated)})
        result.changed_content = result.changed_state = True
        result.generated += 1
        return

    if not status:
        field_state.update({"status": "manual", "source_hash": source_hash, "english_hash": english_hash})
        result.manual += 1
        result.changed_state = True
        return

    if status in {"auto", "auto-stale", "pending"}:
        if generated_hash and english_hash != generated_hash:
            next_status = "needs-review" if previous_source_hash and previous_source_hash != source_hash else "manual"
            field_state.clear()
            field_state.update({"status": next_status, "source_hash": source_hash, "english_hash": english_hash})
            result.needs_review += int(next_status == "needs-review")
            result.manual += int(next_status == "manual")
            result.changed_state = True
            return
        if previous_source_hash != source_hash:
            if translator is None:
                field_state["status"] = "auto-stale"
                result.pending += 1
                result.changed_state = True
                return
            translated = translator(source).strip()
            container[en_key] = translated
            field_state.update({"status": "auto", "source_hash": source_hash, "generated_hash": digest(translated)})
            result.changed_content = result.changed_state = True
            result.refreshed += 1
        return

    # Manual English is immutable. A later Chinese edit only marks it for review.
    if status in {"manual", "needs-review"}:
        stored_english_hash = str(field_state.get("english_hash", ""))
        if stored_english_hash and stored_english_hash != english_hash:
            field_state.update({"status": "manual", "source_hash": source_hash, "english_hash": english_hash})
            result.manual += 1
            result.changed_state = True
        elif previous_source_hash != source_hash:
            field_state.update({"status": "needs-review", "source_hash": source_hash, "english_hash": english_hash})
            result.needs_review += 1
            result.changed_state = True


class OpenAICompatibleTranslator:
    def __init__(self) -> None:
        self.api_key = os.environ["TRANSLATION_API_KEY"]
        self.model = os.environ["TRANSLATION_MODEL"]
        self.api_base = os.environ.get("TRANSLATION_API_BASE", "https://api.openai.com/v1").rstrip("/")
        self.style = STYLE_PATH.read_text(encoding="utf-8")

    def __call__(self, source: str) -> str:
        payload = {
            "model": self.model,
            "temperature": 0.1,
            "messages": [
                {"role": "system", "content": self.style},
                {"role": "user", "content": source},
            ],
        }
        request = urllib.request.Request(
            f"{self.api_base}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                data = json.load(response)
        except (urllib.error.URLError, TimeoutError, KeyError, ValueError) as exc:
            raise RuntimeError(f"translation provider request failed: {exc}") from exc
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("translation provider returned an unsupported response") from exc


def selected_files() -> Iterable[tuple[Path, set[str]]]:
    for pattern, allowed in FILE_RULES:
        for path in sorted(ROOT.glob(pattern)):
            yield path, allowed


def run(write: bool, translator: Callable[[str], str] | None) -> TranslationResult:
    state = yaml.safe_load(STATE_PATH.read_text(encoding="utf-8")) or {"version": 1, "entries": {}}
    entries = state.setdefault("entries", {})
    result = TranslationResult()
    files = list(selected_files())
    active_paths = {path.relative_to(ROOT).as_posix() for path, _ in files}
    prune_deleted_entries(entries, active_paths, result)

    for path, allowed in files:
        data, body = load_content(path)
        relative = path.relative_to(ROOT).as_posix()
        file_state = entries.setdefault(relative, {})
        before = yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
        for container, zh_key, en_key, field_path in walk_pairs(data, allowed):
            pair_state = file_state.setdefault(field_path, {})
            process_pair(container, zh_key, en_key, pair_state, translator, result)
        after = yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
        if write and before != after:
            save_content(path, data, body)

    if write and result.changed_state:
        STATE_PATH.write_text(yaml.safe_dump(state, allow_unicode=True, sort_keys=True, width=1000), encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write generated English and state")
    parser.add_argument("--dry-run", action="store_true", help="report state without changing files")
    args = parser.parse_args()
    if args.write == args.dry_run:
        parser.error("choose exactly one of --write or --dry-run")

    provider = os.environ.get("TRANSLATION_PROVIDER", "openai-compatible")
    translator: Callable[[str], str] | None = None
    if args.write:
        if provider != "openai-compatible":
            raise SystemExit(f"unsupported TRANSLATION_PROVIDER: {provider}")
        if os.environ.get("TRANSLATION_API_KEY") and os.environ.get("TRANSLATION_MODEL"):
            translator = OpenAICompatibleTranslator()
        else:
            print("::warning::Translation credentials are absent; English fallback remains active.")

    result = run(args.write, translator)
    print(json.dumps(result.__dict__, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
