#!/usr/bin/env python3
"""Regression test that production validation never depends on demo records."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COLLECTIONS = ("_research", "_news", "_events", "_members", "_opportunities")


def ignore_transient(_directory: str, names: list[str]) -> set[str]:
    ignored = {".git", ".codex-tmp", "_site", "vendor", "node_modules", ".sass-cache", "__pycache__"}
    return set(names) & ignored


class CmsRecordIndependenceTests(unittest.TestCase):
    def test_all_collection_records_can_be_removed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            copy_root = Path(temp_dir) / "site"
            shutil.copytree(ROOT, copy_root, ignore=ignore_transient)
            for collection in COLLECTIONS:
                for path in (copy_root / collection).glob("*.md"):
                    path.unlink()

            completed = subprocess.run(
                [sys.executable, "scripts/validate_content.py"],
                cwd=copy_root,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(
                completed.returncode,
                0,
                f"validator must accept empty CMS collections\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}",
            )


if __name__ == "__main__":
    unittest.main()
