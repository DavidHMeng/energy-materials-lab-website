#!/usr/bin/env python3
"""Regression checks for the Pages CMS editorial contract."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CMS = yaml.safe_load((ROOT / ".pages.yml").read_text(encoding="utf-8"))
ENTRIES = {entry["name"]: entry for entry in CMS["content"]}


def fields(entry):
    return {field["name"]: field for field in entry.get("fields", [])}


class PagesCmsSchemaTests(unittest.TestCase):
    def test_all_primary_editor_modules_exist(self):
        self.assertEqual(
            set(ENTRIES),
            {"homepage", "news", "events", "research", "publications", "team", "team-roles", "opportunities", "site"},
        )

    def test_media_preserves_uploaded_logo_formats(self):
        media = CMS["media"][0]
        self.assertEqual(media["input"], "images/uploads")
        self.assertEqual(media["output"], "/images/uploads")
        self.assertEqual(media["categories"], ["image"])
        self.assertNotIn("transform", media)

    def test_shared_doi_inputs_accept_editor_forms(self):
        homepage_fields = fields(ENTRIES["homepage"])
        intro_fields = fields(homepage_fields["introduction"])
        slide_fields = fields(intro_fields["slides"])
        doi_fields = [
            slide_fields["related_doi"],
            fields(ENTRIES["research"])["doi_list"],
            fields(ENTRIES["publications"])["id"],
            fields(ENTRIES["team"])["representative_dois"],
        ]
        for field in doi_fields:
            pattern = field.get("pattern", {}).get("regex", "")
            self.assertTrue(re.fullmatch(pattern, "10.1021/jacs.5c22628"))
            self.assertTrue(re.fullmatch(pattern, " https://doi.org/10.1021/jacs.5c22628 "))
            self.assertTrue(re.fullmatch(pattern, "DOI:10.1021/JACS.5C22628"))
            self.assertTrue(re.fullmatch(pattern, "DOI：10.1021/JACS.5C22628"))
            self.assertFalse(re.fullmatch(pattern, "not-a-doi"))
        self.assertTrue(re.fullmatch(slide_fields["related_doi"]["pattern"]["regex"], ""))
        self.assertFalse(re.fullmatch(fields(ENTRIES["publications"])["id"]["pattern"]["regex"], ""))
        self.assertTrue(fields(ENTRIES["research"])["doi_list"]["list"])
        self.assertTrue(fields(ENTRIES["team"])["representative_dois"]["list"])

    def test_visibility_order_bilingual_and_image_controls(self):
        expected = {
            "homepage": {"highlights_heading_zh", "highlights_heading_en", "news_limit", "events_limit"},
            "news": {"title_zh", "title_en", "display", "image"},
            "events": {"title_zh", "title_en", "display", "cover_image"},
            "research": {"title_zh", "title_en", "display", "order", "graphical_abstract"},
            "team": {"name_zh", "name_en", "display", "order", "portrait"},
            "opportunities": {"title_zh", "title_en", "display", "display_order", "links"},
            "site": {"lab_name_zh", "lab_name_en", "lab_logo", "school_logo", "typography"},
        }
        for name, required in expected.items():
            self.assertTrue(required.issubset(fields(ENTRIES[name])), name)

        for entry_name, image_name in (
            ("news", "image"),
            ("events", "cover_image"),
            ("research", "graphical_abstract"),
            ("team", "portrait"),
            ("site", "lab_logo"),
            ("site", "school_logo"),
        ):
            self.assertEqual(fields(ENTRIES[entry_name])[image_name]["options"]["media"], "images")

    def test_profile_publications_have_independent_archive_visibility(self):
        publication = fields(ENTRIES["publications"])["publication_visible"]
        self.assertEqual(publication["type"], "boolean")
        self.assertTrue(publication["default"])
        self.assertIn("global Publications archive", publication["description"])
        for path in (ROOT / "publications" / "index.md", ROOT / "zh" / "publications" / "index.md"):
            self.assertIn("publication_visible != false", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
