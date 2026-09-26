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
            (root / "_data" / "publications.yaml").write_text(
                "- doi: DOI:10.1002/JACS.5C22628\n  type: paper\n  image: /images/a.png\n  tags: [one]\n  member_ids: []\n  display: true\n",
                encoding="utf-8",
            )
            (root / "_data" / "sources.yaml").write_text(
                "- id: doi:10.1002/adma.202102415\n  type: paper\n  image: /images/old.png\n  publication_visible: true\n",
                encoding="utf-8",
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
            self.assertEqual(ids.count("doi:10.1002/adma.202102415"), 0)
            self.assertTrue(all(set(entry) == {"id", "type"} for entry in sources))
            publication = yaml.safe_load((root / "_data" / "publications.yaml").read_text(encoding="utf-8"))[0]
            self.assertEqual(publication["doi"], "10.1002/jacs.5c22628")
            self.assertEqual(synchronize(root, write=False), [])

    def test_publication_delete_does_not_remove_other_membership(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for folder in ("_data", "_members", "_research"):
                (root / folder).mkdir()
            (root / "_data" / "publications.yaml").write_text(
                "- doi: 10.1021/jacs.5c22628\n  type: paper\n  display: true\n", encoding="utf-8"
            )
            (root / "_data" / "sources.yaml").write_text("[]\n", encoding="utf-8")
            (root / "_data" / "homepage.yaml").write_text("introduction: {}\n", encoding="utf-8")
            (root / "_members" / "member.md").write_text(
                "---\nrepresentative_dois:\n- 10.1021/jacs.5c22628\n---\n", encoding="utf-8"
            )
            synchronize(root, write=True)
            sources = yaml.safe_load((root / "_data" / "sources.yaml").read_text(encoding="utf-8"))
            self.assertEqual(sources[0], {"id": "doi:10.1021/jacs.5c22628", "type": "paper"})
            (root / "_data" / "publications.yaml").write_text("[]\n", encoding="utf-8")
            synchronize(root, write=True)
            sources = yaml.safe_load((root / "_data" / "sources.yaml").read_text(encoding="utf-8"))
            self.assertEqual(sources[0]["id"], "doi:10.1021/jacs.5c22628")

    def test_duplicate_publication_conflict_is_not_silent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for folder in ("_data", "_members", "_research"):
                (root / folder).mkdir()
            (root / "_data" / "publications.yaml").write_text(
                "- doi: 10.1021/jacs.5c22628\n  type: paper\n  display: true\n"
                "- doi: https://doi.org/10.1021/JACS.5C22628\n  type: review\n  display: true\n",
                encoding="utf-8",
            )
            (root / "_data" / "sources.yaml").write_text("[]\n", encoding="utf-8")
            (root / "_data" / "homepage.yaml").write_text("introduction: {}\n", encoding="utf-8")
            with self.assertRaisesRegex(CitationRegistryError, "conflicting 'type'"):
                synchronize(root, write=True)


if __name__ == "__main__":
    unittest.main()
