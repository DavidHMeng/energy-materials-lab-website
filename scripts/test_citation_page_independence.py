#!/usr/bin/env python3
"""Regression fixtures for independent Research/Profile/Publications membership."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from citation_registry import synchronize


DOI = "10.1021/jacs.5c22628"


class CitationPageIndependenceTests(unittest.TestCase):
    def make_root(self):
        root = Path(tempfile.mkdtemp())
        for folder in ("_data", "_members", "_research"):
            (root / folder).mkdir()
        (root / "_data" / "publications.yaml").write_text(
            f"- doi: {DOI}\n  type: paper\n  image: /images/ga.jpg\n  display: true\n", encoding="utf-8"
        )
        (root / "_data" / "sources.yaml").write_text("[]\n", encoding="utf-8")
        (root / "_data" / "homepage.yaml").write_text("introduction: {}\n", encoding="utf-8")
        (root / "_members" / "member.md").write_text(
            f"---\nrepresentative_dois:\n- {DOI}\n---\n", encoding="utf-8"
        )
        (root / "_research" / "area.md").write_text(f"---\ndoi_list:\n- {DOI}\n---\n", encoding="utf-8")
        synchronize(root, write=True)
        return root

    def source_ids(self, root):
        return {entry["id"] for entry in yaml.safe_load((root / "_data" / "sources.yaml").read_text(encoding="utf-8"))}

    def test_delete_publication_keeps_research_and_profile_registry_membership(self):
        root = self.make_root()
        (root / "_data" / "publications.yaml").write_text("[]\n", encoding="utf-8")
        synchronize(root, write=True)
        self.assertIn(f"doi:{DOI}", self.source_ids(root))

    def test_delete_research_keeps_publication_and_profile_registry_membership(self):
        root = self.make_root()
        (root / "_research" / "area.md").write_text("---\ndoi_list: []\n---\n", encoding="utf-8")
        synchronize(root, write=True)
        self.assertIn(f"doi:{DOI}", self.source_ids(root))
        self.assertEqual(yaml.safe_load((root / "_data" / "publications.yaml").read_text(encoding="utf-8"))[0]["display"], True)

    def test_delete_profile_keeps_publication_and_research_registry_membership(self):
        root = self.make_root()
        (root / "_members" / "member.md").write_text("---\nrepresentative_dois: []\n---\n", encoding="utf-8")
        synchronize(root, write=True)
        self.assertIn(f"doi:{DOI}", self.source_ids(root))

    def test_remove_all_memberships_removes_registry_entry(self):
        root = self.make_root()
        (root / "_data" / "publications.yaml").write_text("[]\n", encoding="utf-8")
        (root / "_members" / "member.md").write_text("---\nrepresentative_dois: []\n---\n", encoding="utf-8")
        (root / "_research" / "area.md").write_text("---\ndoi_list: []\n---\n", encoding="utf-8")
        synchronize(root, write=True)
        self.assertNotIn(f"doi:{DOI}", self.source_ids(root))


if __name__ == "__main__":
    unittest.main()
