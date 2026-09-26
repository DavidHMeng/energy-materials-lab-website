#!/usr/bin/env python3
"""Remove registered English fields in an ephemeral CI checkout.

This script is intentionally used only after the normal production test has passed.
The runner checkout is disposable; publication data and repository history are never
modified. The resulting second Jekyll build proves that every English route survives
when Pages CMS omits all optional English fields.
"""

from __future__ import annotations

from typing import Any

from translate_content import ROOT, load_content, load_registry, save_content


def remove_registered_english(value: Any, stems: set[str]) -> int:
    removed = 0
    if isinstance(value, dict):
        for key in list(value):
            if isinstance(key, str) and key.endswith("_zh") and key[:-3] in stems:
                removed += int(value.pop(f"{key[:-3]}_en", None) is not None)
        for child in value.values():
            removed += remove_registered_english(child, stems)
    elif isinstance(value, list):
        for child in value:
            removed += remove_registered_english(child, stems)
    return removed


def main() -> int:
    removed = 0
    for resource in load_registry()["resources"]:
        if resource.get("exclude_all"):
            continue
        stems = set(resource.get("auto_fields", [])) | set(resource.get("manual_fields", []))
        for path in sorted(ROOT.glob(str(resource["pattern"]))):
            data, body = load_content(path)
            count = remove_registered_english(data, stems)
            if count:
                save_content(path, data, body)
                removed += count
    print(f"Prepared all-English-empty fixture: removed {removed} optional field value(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
