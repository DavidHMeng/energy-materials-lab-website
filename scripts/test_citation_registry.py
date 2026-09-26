#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from citation_registry import CitationRegistryError, normalize_doi, synchronize


class CitationRegistryTests(unittest.TestCase):
    def test_normalizes_supported_editor_inputs(self):
        expected = "10.1021/jacs.5c22628"
        for value in (
            expected,
            "  https://doi.org/10.1021/JACS.5C22628  ",
            "http://doi.org/10.1021/jacs.5c22628",
            "DOI:10.1021/JACS.5C22628",
            "DOI：10.1021/JACS.5C22628",
            "doi:doi:10.1021/jacs.5c22628",
        ):
            with self.subTest(value=value):
                self.assertEqual(normalize_doi(value), expected)

    def test_rejects_invalid_doi(self):
        for value in ("", "jacs.5c22628", "10.1021", "https://example.com/paper"):
            with self.subTest(value=value):
                with self.assertRaises(CitationRegistryError):
                    normalize_doi(value)

    def test_collects_all_references_once(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for folder in ("_data", "_members", "_research"):
                (root / folder).mkdir()
            (root / "_data" / "sources.yaml").write_text(
                "- id: doi:10.1002/adma.202102415\n  type: paper\n", encoding="utf-8"
            )
            (root / "_data" / "homepage.yaml").write_text(
                "introduction:\n  slides:\n  - related_doi: https://doi.org/10.1021/jacs.5c22628\n",
                encoding="utf-8",
            )
            (root / "_members" / "member.md").write_text(
                "---\nrepresentative_dois:\n- https://doi.org/10.1021/jacs.5c22628\n- DOI:10.1021/JACS.5C22628\n---\n",
                encoding="utf-8",
            )
            (root / "_research" / "area.md").write_text(
                "---\ndoi_list:\n- doi:10.1021/jacs.5c22628\n---\n",
                encoding="utf-8",
            )

            changes = synchronize(root, write=True)
            self.assertTrue(changes)
            sources = yaml.safe_load((root / "_data" / "sources.yaml").read_text(encoding="utf-8"))
            ids = [entry["id"] for entry in sources]
            self.assertEqual(ids.count("doi:10.1021/jacs.5c22628"), 1)
            profile_source = next(entry for entry in sources if entry["id"] == "doi:10.1021/jacs.5c22628")
            self.assertFalse(profile_source["publication_visible"])
            self.assertEqual(synchronize(root, write=False), [])

    def test_explicit_publication_visibility_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for folder in ("_data", "_members", "_research"):
                (root / folder).mkdir()
            (root / "_data" / "sources.yaml").write_text(
                "- id: doi:10.1021/jacs.5c22628\n"
                "  type: paper\n"
                "  publication_visible: true\n",
                encoding="utf-8",
            )
            (root / "_data" / "homepage.yaml").write_text("introduction: {}\n", encoding="utf-8")
            (root / "_members" / "member.md").write_text(
                "---\nrepresentative_dois:\n- 10.1021/jacs.5c22628\n---\n", encoding="utf-8"
            )
            synchronize(root, write=True)
            sources = yaml.safe_load((root / "_data" / "sources.yaml").read_text(encoding="utf-8"))
            self.assertTrue(sources[0]["publication_visible"])


if __name__ == "__main__":
    unittest.main()
