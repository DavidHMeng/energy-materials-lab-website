#!/usr/bin/env python3
"""Ensure publication presentation images cannot leak through shared citations."""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


class PublicationImageIsolationTests(unittest.TestCase):
    def test_publications_are_the_only_image_source(self):
        publications = yaml.safe_load((ROOT / "_data" / "publications.yaml").read_text(encoding="utf-8"))
        self.assertTrue(any(entry.get("image") for entry in publications))
        for entry in yaml.safe_load((ROOT / "_data" / "sources.yaml").read_text(encoding="utf-8")):
            self.assertNotIn("image", entry)
        for entry in yaml.safe_load((ROOT / "_data" / "citations.yaml").read_text(encoding="utf-8")):
            self.assertNotIn("image", entry)

    def test_templates_use_explicit_image_opt_in(self):
        citation = (ROOT / "_includes" / "citation.html").read_text(encoding="utf-8")
        self.assertIn("citation_image = include.image", citation)
        self.assertNotIn("citation.image", citation)
        self.assertIn("image=publication.image", (ROOT / "publications" / "index.md").read_text(encoding="utf-8"))
        self.assertIn("image=publication.image", (ROOT / "zh" / "publications" / "index.md").read_text(encoding="utf-8"))
        for relative in ("_includes/custom/representative-publication.html", "_includes/custom/compact-publication.html"):
            self.assertNotIn("image=", (ROOT / relative).read_text(encoding="utf-8"))

    def test_generated_site_has_isolated_image_counts_when_available(self):
        site = ROOT / "_site"
        if not site.is_dir():
            self.skipTest("generated site is produced by the build stage")
        publication_html = (site / "publications" / "index.html").read_text(encoding="utf-8")
        zh_publication_html = (site / "zh" / "publications" / "index.html").read_text(encoding="utf-8")
        self.assertGreater(publication_html.count('class="citation-image"'), 0)
        self.assertGreater(zh_publication_html.count('class="citation-image"'), 0)
        for html_path in list((site / "team").glob("*/index.html")) + list((site / "zh" / "team").glob("*/index.html")):
            self.assertEqual(html_path.read_text(encoding="utf-8").count('class="citation-image"'), 0, html_path)
        for html_path in (site / "research" / "index.html", site / "zh" / "research" / "index.html"):
            if html_path.exists():
                self.assertEqual(html_path.read_text(encoding="utf-8").count('class="citation-image"'), 0, html_path)


if __name__ == "__main__":
    unittest.main()
