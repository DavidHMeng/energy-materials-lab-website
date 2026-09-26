#!/usr/bin/env python3
"""Normalize DOI inputs and synchronize the shared citation source registry.

Editors may paste a bare DOI, doi: identifier, or doi.org URL. The canonical form in
content references is a lowercase bare DOI; the Greene citation source adapter alone
stores the required ``doi:`` prefix.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import OrderedDict
from pathlib import Path
from urllib.parse import unquote

import yaml


DOI_PATTERN = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)
DOI_URL_PATTERN = re.compile(r"^https?://(?:dx\.)?doi\.org/", re.IGNORECASE)
DOI_PREFIX_PATTERN = re.compile(r"^doi\s*[:：]\s*", re.IGNORECASE)
FRONTMATTER_PATTERN = re.compile(r"\A---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|\Z)(.*)\Z", re.DOTALL)


class CitationRegistryError(ValueError):
    """Raised when an editor-supplied citation reference is invalid or ambiguous."""


def normalize_doi(value: object) -> str:
    """Return the canonical lowercase bare DOI or raise a clear validation error."""

    candidate = unquote(str(value or "")).strip()
    if not candidate:
        raise CitationRegistryError("DOI is empty")

    # Accept nested/duplicated editor prefixes defensively without ever emitting them.
    previous = None
    while candidate != previous:
        previous = candidate
        candidate = DOI_URL_PATTERN.sub("", candidate).strip()
        candidate = DOI_PREFIX_PATTERN.sub("", candidate).strip()

    if any(character.isspace() for character in candidate) or not DOI_PATTERN.fullmatch(candidate):
        raise CitationRegistryError(
            f"invalid DOI {value!r}; use 10.xxxx/xxxxx or https://doi.org/10.xxxx/xxxxx"
        )
    return candidate.lower()


def source_id(value: object) -> str:
    return f"doi:{normalize_doi(value)}"


def _read_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _write_yaml(path: Path, data) -> None:
    path.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=1000),
        encoding="utf-8",
    )


def _read_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_PATTERN.match(text)
    if not match:
        raise CitationRegistryError(f"{path}: missing YAML front matter")
    return yaml.safe_load(match.group(1)) or {}, match.group(2)


def _write_frontmatter(path: Path, data: dict, body: str) -> None:
    frontmatter = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=1000).rstrip()
    path.write_text(f"---\n{frontmatter}\n---\n{body}", encoding="utf-8")


def _normalize_list(values: object, label: str) -> list[str]:
    if values in (None, ""):
        return []
    if not isinstance(values, list):
        raise CitationRegistryError(f"{label}: expected a list of DOI values")
    normalized: list[str] = []
    for index, value in enumerate(values, start=1):
        try:
            doi = normalize_doi(value)
        except CitationRegistryError as exc:
            raise CitationRegistryError(f"{label}[{index}]: {exc}") from exc
        if doi not in normalized:
            normalized.append(doi)
    return normalized


def _merge_publication(target: dict, incoming: dict, doi: str) -> None:
    """Merge duplicate user records without silently choosing conflicting values."""

    for key, value in incoming.items():
        if key == "doi" or value in (None, "", []):
            continue
        if key in {"tags", "member_ids"}:
            merged = list(target.get(key) or [])
            for item in value if isinstance(value, list) else [value]:
                if item not in merged:
                    merged.append(item)
            target[key] = merged
        elif target.get(key) in (None, "", []):
            target[key] = value
        elif target[key] != value:
            raise CitationRegistryError(
                f"duplicate publication {doi} has conflicting {key!r} values; merge it manually"
            )


def synchronize(root: Path, write: bool = False) -> list[str]:
    """Build the generated DOI registry from independent page memberships.

    ``_data/publications.yaml`` is the only user-owned Publications membership file.
    ``_data/sources.yaml`` is rebuilt from the union of Publications, Research,
    Profile, and Homepage DOI references and intentionally contains only provider
    identity/type data. No existing source presentation fields are carried forward.
    """

    root = root.resolve()
    changes: list[str] = []
    referenced: list[str] = []
    publication_types: dict[str, str] = {}
    pending_frontmatter: list[tuple[Path, dict, str]] = []

    def track_reference(doi: str) -> None:
        if doi not in referenced:
            referenced.append(doi)

    publications_path = root / "_data" / "publications.yaml"
    publications = _read_yaml(publications_path) or []
    if not isinstance(publications, list) or not all(isinstance(entry, dict) for entry in publications):
        raise CitationRegistryError("_data/publications.yaml must contain a list of mappings")

    normalized_publications: list[dict] = []
    publication_by_doi: OrderedDict[str, dict] = OrderedDict()
    for index, entry in enumerate(publications, start=1):
        try:
            doi = normalize_doi(entry.get("doi"))
        except CitationRegistryError as exc:
            raise CitationRegistryError(f"_data/publications.yaml[{index}]: {exc}") from exc
        normalized_entry = dict(entry)
        normalized_entry["doi"] = doi
        if doi in publication_by_doi:
            _merge_publication(publication_by_doi[doi], normalized_entry, doi)
            changes.append(f"deduplicate _data/publications.yaml:{doi}")
        else:
            publication_by_doi[doi] = normalized_entry
        if entry.get("doi") != doi:
            changes.append(f"normalize _data/publications.yaml:{doi}")

    normalized_publications = list(publication_by_doi.values())
    publications_changed = normalized_publications != publications
    for entry in normalized_publications:
        doi = entry["doi"]
        publication_types[doi] = str(entry.get("type") or "paper")
        track_reference(doi)

    for folder, field in (("_members", "representative_dois"), ("_research", "doi_list")):
        for path in sorted((root / folder).glob("*.md")):
            data, body = _read_frontmatter(path)
            before = data.get(field, []) or []
            after = _normalize_list(before, f"{path.relative_to(root)}:{field}")
            for doi in after:
                track_reference(doi)
            if before != after:
                data[field] = after
                pending_frontmatter.append((path, data, body))
                changes.append(f"normalize {path.relative_to(root)}:{field}")

    homepage_path = root / "_data" / "homepage.yaml"
    homepage = _read_yaml(homepage_path) or {}
    homepage_changed = False
    slides = ((homepage.get("introduction") or {}).get("slides") or [])
    for index, slide in enumerate(slides, start=1):
        value = slide.get("related_doi")
        if not value:
            continue
        try:
            normalized = normalize_doi(value)
        except CitationRegistryError as exc:
            raise CitationRegistryError(f"_data/homepage.yaml:slides[{index}]: {exc}") from exc
        track_reference(normalized)
        if value != normalized:
            slide["related_doi"] = normalized
            homepage_changed = True
            changes.append(f"normalize _data/homepage.yaml:slides[{index}].related_doi")

    sources_path = root / "_data" / "sources.yaml"
    sources = _read_yaml(sources_path) or []
    if not isinstance(sources, list) or not all(isinstance(entry, dict) for entry in sources):
        raise CitationRegistryError("_data/sources.yaml must contain a list of mappings")

    normalized_sources = [
        {"id": f"doi:{doi}", "type": publication_types.get(doi, "paper")}
        for doi in referenced
    ]

    sources_changed = normalized_sources != sources
    if sources_changed:
        changes.append("rebuild generated _data/sources.yaml")

    if write:
        for path, data, body in pending_frontmatter:
            _write_frontmatter(path, data, body)
        if homepage_changed:
            _write_yaml(homepage_path, homepage)
        if publications_changed:
            _write_yaml(publications_path, normalized_publications)
        if sources_changed:
            _write_yaml(sources_path, normalized_sources)

    return changes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="normalize files and update the registry")
    mode.add_argument("--check", action="store_true", help="fail when synchronization would change files")
    args = parser.parse_args()

    try:
        changes = synchronize(args.root, write=args.write)
    except CitationRegistryError as exc:
        print(f"Citation registry error: {exc}", file=sys.stderr)
        return 1

    if changes:
        action = "Applied" if args.write else "Required"
        print(f"{action} citation registry changes:")
        for change in changes:
            print(f"- {change}")
        if args.check:
            return 1
    else:
        print("Citation registry is normalized and synchronized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
