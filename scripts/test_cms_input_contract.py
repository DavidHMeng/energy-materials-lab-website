#!/usr/bin/env python3
"""Regression tests for the Pages CMS input contract and deploy-safe formats."""

from __future__ import annotations

import re
import unittest
from datetime import date
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CMS = yaml.safe_load((ROOT / ".pages.yml").read_text(encoding="utf-8"))
ENTRIES = {entry["name"]: entry for entry in CMS["content"]}


def walk_fields(fields, prefix=""):
    for field in fields or []:
        name = field["name"]
        path = f"{prefix}.{name}" if prefix else name
        yield path, field
        yield from walk_fields(field.get("fields"), path)


def field_map(entry_name):
    return dict(walk_fields(ENTRIES[entry_name].get("fields")))


class PagesCmsInputContractTests(unittest.TestCase):
    def test_all_editor_modules_and_field_inventory(self):
        self.assertEqual(
            set(ENTRIES),
            {"homepage", "pages", "news", "events", "research", "publications", "team", "team-roles", "opportunities", "site"},
        )
        # Current contract inventory. The count includes nested object/list fields.
        self.assertEqual(sum(len(field_map(name)) for name in ENTRIES), 176)

    def test_no_malformed_flow_mapping_fields(self):
        allowed = {"name", "label", "type", "required", "pattern", "description", "options", "default", "list", "fields"}
        for entry in ENTRIES.values():
            for path, field in walk_fields(entry.get("fields")):
                self.assertTrue(set(field) <= allowed, f"unexpected schema key in {path}: {set(field) - allowed}")

    def test_editorial_collections_do_not_disable_content_operations(self):
        for entry_name in ("news", "events", "research", "team", "opportunities"):
            operations = ENTRIES[entry_name].get("operations", {})
            for operation in ("create", "rename", "delete"):
                self.assertIsNot(
                    operations.get(operation),
                    False,
                    f"{entry_name} must not disable the {operation} operation",
                )

    def test_member_slug_is_a_stable_filename_safe_id(self):
        field = field_map("team")["slug"]
        pattern = re.compile(field["pattern"])
        for value in ("jianwen-liang", "doctoral-researcher-08", "visitor-2026"):
            self.assertIsNotNone(pattern.fullmatch(value), value)
        for value in ("Jianwen Liang", "梁剑文", "member_id", "member/one", ""):
            self.assertIsNone(pattern.fullmatch(value), value)
        self.assertIn("filename", field["description"])

    def test_fixed_select_values_are_explicit(self):
        self.assertEqual(ENTRIES["events"]["fields"][0]["options"]["values"], ["Academic", "Group"])
        self.assertIn("graphical-abstract", {item["name"] for item in ENTRIES["homepage"]["fields"][0]["fields"][7]["fields"][3]["options"]["values"]})
        self.assertIn("force_hide", ENTRIES["opportunities"]["fields"][6]["options"]["values"][2]["name"])

    def test_date_and_doi_examples_match_contract(self):
        self.assertEqual(date.fromisoformat("2026-09-25").isoformat(), "2026-09-25")
        with self.assertRaises(ValueError):
            date.fromisoformat("25-09-2026")
        doi_pattern = re.compile(ENTRIES["publications"]["fields"][0]["pattern"]["regex"])
        for value in (
            "10.1021/jacs.5c22628",
            " https://doi.org/10.1021/jacs.5c22628 ",
            "DOI:10.1021/JACS.5C22628",
            "DOI：10.1021/JACS.5C22628",
        ):
            self.assertIsNotNone(doi_pattern.fullmatch(value), value)
        self.assertIsNone(doi_pattern.fullmatch("not-a-doi"))

    def test_publication_display_is_an_explicit_boolean_control(self):
        field = field_map("publications")["display"]
        self.assertEqual(field["type"], "boolean")
        self.assertTrue(field["default"])

    def test_page_settings_keep_english_optional(self):
        for page_key in ("research", "publications", "team", "opportunities"):
            fields = field_map("pages")
            for field_name in ("title_zh", "intro_zh", "description_zh"):
                self.assertTrue(fields[f"{page_key}.{field_name}"]["required"])
            for field_name in ("title_en", "intro_en", "description_en"):
                self.assertIsNot(fields[f"{page_key}.{field_name}"].get("required"), True)

    def test_media_and_rich_text_boundaries_are_intentional(self):
        for entry_name, path in (
            ("homepage", "introduction.slides.image"),
            ("research", "graphical_abstract"),
            ("team", "portrait"),
            ("site", "lab_logo"),
            ("site", "lab_logo_header"),
            ("site", "school_logo"),
        ):
            self.assertEqual(field_map(entry_name)[path]["options"]["media"], "images")
        for entry_name, path in (("publications", "description_en"), ("events", "description_zh"), ("team", "education_zh")):
            self.assertFalse(field_map(entry_name)[path]["options"]["media"])

    def test_header_logo_field_preserves_fallback_and_replacement_warning(self):
        field = field_map("site")["lab_logo_header"]
        self.assertEqual(field["type"], "image")
        self.assertIsNot(field.get("required"), True)
        self.assertEqual(field["options"]["media"], "images")
        description = field["description"].lower()
        for keyword in ("leave blank", "lab logo", "replace", "clear"):
            self.assertIn(keyword, description)


if __name__ == "__main__":
    unittest.main()
