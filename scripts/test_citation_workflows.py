#!/usr/bin/env python3
"""Regression checks for build-local citation preparation."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CitationWorkflowTests(unittest.TestCase):
    def test_production_prepares_citations_inside_build_job(self):
        workflow = (ROOT / ".github" / "workflows" / "publish-production.yml").read_text(encoding="utf-8")
        self.assertIn("needs: [translation, content]", workflow)
        self.assertIn("Prepare citation workspace from current content", workflow)
        self.assertIn("python scripts/citation_registry.py --write", workflow)
        self.assertIn("python _cite/cite.py", workflow)
        self.assertIn("python scripts/citation_registry.py --check", workflow)
        self.assertNotIn("check_citation_freshness.py", workflow)
        self.assertNotIn("needs: [citations, translation, content]", workflow)

    def test_pages_builds_prepare_their_own_citation_workspace(self):
        for filename in ("deploy-pages.yml", "pages-staging.yml"):
            workflow = (ROOT / ".github" / "workflows" / filename).read_text(encoding="utf-8")
            self.assertIn("Prepare citation workspace from current content", workflow)
            self.assertIn("python scripts/citation_registry.py --write", workflow)
            self.assertIn("python _cite/cite.py", workflow)
            self.assertIn("python scripts/citation_registry.py --check", workflow)

    def test_citation_sync_is_serialized_per_ref(self):
        workflow = (ROOT / ".github" / "workflows" / "citation-schedule.yml").read_text(encoding="utf-8")
        self.assertIn("group: citation-sync-${{ github.ref }}", workflow)
        self.assertIn("cancel-in-progress: false", workflow)

    def test_citation_sync_tracks_publications_source(self):
        schedule = (ROOT / ".github" / "workflows" / "citation-schedule.yml").read_text(encoding="utf-8")
        update = (ROOT / ".github" / "workflows" / "update-citations.yaml").read_text(encoding="utf-8")
        self.assertIn('"_data/publications.yaml"', schedule)
        self.assertIn("_data/publications.yaml", update)


if __name__ == "__main__":
    unittest.main()
