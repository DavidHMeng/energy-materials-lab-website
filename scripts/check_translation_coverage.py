#!/usr/bin/env python3
"""Audit Pages CMS bilingual fields against the central translation registry."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

import yaml

ROOT = Path(__file__).resolve().parents[1]


def nested_fields(fields: Iterable[dict[str, Any]]) -> Iterable[dict[str, Any]]:
    for field in fields:
        yield field
        yield from nested_fields(field.get("fields", []) or [])


def load_coverage() -> tuple[list[dict[str, Any]], list[str]]:
    cms = yaml.safe_load((ROOT / ".pages.yml").read_text(encoding="utf-8")) or {}
    registry = yaml.safe_load((ROOT / "_translation" / "registry.yml").read_text(encoding="utf-8")) or {}
    resources = {item["cms"]: item for item in registry.get("resources", [])}
    rows: list[dict[str, Any]] = []
    warnings: list[str] = []

    for collection in cms.get("content", []):
        collection_name = str(collection.get("name", ""))
        resource = resources.get(collection_name)
        if resource is None:
            warnings.append(f"{collection_name}: no translation registry resource")
            continue
        fields = {str(field.get("name")): field for field in nested_fields(collection.get("fields", [])) if field.get("name")}
        auto = set(resource.get("auto_fields", []))
        manual = set(resource.get("manual_fields", []))
        overlap = auto & manual
        if overlap:
            warnings.append(f"{collection_name}: fields registered as both auto and manual: {sorted(overlap)}")

        for name, field in sorted(fields.items()):
            if not name.endswith("_zh"):
                continue
            stem = name[:-3]
            en_name = f"{stem}_en"
            en_field = fields.get(en_name)
            if resource.get("exclude_all"):
                status = "TRANSLATION EXCLUDED"
                reason = resource.get("excluded_reason", "Collection excluded by policy")
            elif stem in auto:
                status = "TRANSLATABLE"
                reason = ""
            elif stem in manual:
                status = "MANUAL EN ONLY"
                reason = "Official wording or personal name must be supplied by an editor"
            else:
                status = "UNREGISTERED"
                reason = "No central registry decision"
                warnings.append(f"{collection_name}.{name}: unregistered Chinese field")

            if en_field is None:
                warnings.append(f"{collection_name}.{name}: missing {en_name}")
            elif en_field.get("required") is True:
                warnings.append(f"{collection_name}.{en_name}: English field must remain optional")

            rows.append(
                {
                    "collection": collection_name,
                    "zh_field": name,
                    "en_field": en_name if en_field else "",
                    "status": status,
                    "fallback": bool(en_field),
                    "manual_override": bool(en_field),
                    "reason": reason,
                }
            )

    return rows, warnings


def main() -> int:
    rows, warnings = load_coverage()
    for warning in warnings:
        print(f"::warning::{warning}")
    print(json.dumps({"classified_pairs": len(rows), "warnings": len(warnings)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
