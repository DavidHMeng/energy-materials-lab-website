#!/usr/bin/env python3
"""Regression checks for the Publications CMS data source and DOI identity."""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml

from citation_registry import normalize_doi

ROOT = Path(__file__).resolve().parents[1]


class PublicationCmsTests(unittest.TestCase):
    def test_publications_file_is_the_only_archive_source(self):
        cms = yaml.safe_load((ROOT / ".pages.yml").read_text(encoding="utf-8"))
        entry = next(item for item in cms["content"] if item["name"] == "publications")
        self.assertEqual(entry["path"], "_data/publications.yaml")
        fields = {field["name"] for field in entry["fields"]}
        self.assertEqual(fields, {"doi", "type", "image", "description_zh", "description_en", "tags", "member_ids", "display"})
        self.assertNotIn("publication_visible", fields)

    def test_add_research_or_profile_doi_does_not_duplicate_registry_identity(self):
        publications = yaml.safe_load((ROOT / "_data" / "publications.yaml").read_text(encoding="utf-8"))
        sources = yaml.safe_load((ROOT / "_data" / "sources.yaml").read_text(encoding="utf-8"))
        pub_ids = {normalize_doi(item["doi"]) for item in publications}
        source_ids = [normalize_doi(item["id"]) for item in sources]
        self.assertEqual(len(source_ids), len(set(source_ids)))
        self.assertTrue(pub_ids.issubset(set(source_ids)))

    def test_display_false_controls_only_publications_page_data(self):
        for entry in yaml.safe_load((ROOT / "_data" / "publications.yaml").read_text(encoding="utf-8")):
            self.assertIsInstance(entry.get("display"), bool)
        publication_page = (ROOT / "publications" / "index.md").read_text(encoding="utf-8")
        self.assertIn("publication.display != false", publication_page)


if __name__ == "__main__":
    unittest.main()
