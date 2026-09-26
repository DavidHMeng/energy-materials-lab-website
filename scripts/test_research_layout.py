#!/usr/bin/env python3
"""Source-level regression checks for the Research scientific image canvas."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "_styles" / "custom.scss").read_text(encoding="utf-8")
THEME = (ROOT / "_styles" / "-theme.scss").read_text(encoding="utf-8")
RESEARCH_EN = (ROOT / "research" / "index.md").read_text(encoding="utf-8")
RESEARCH_ZH = (ROOT / "zh" / "research" / "index.md").read_text(encoding="utf-8")


def css_rule(selector: str) -> str:
    match = re.search(rf"(?m)^{re.escape(selector)}\s*\{{(.*?)\}}", CSS, re.S)
    if match is None:
        raise AssertionError(f"Missing CSS rule: {selector}")
    return match.group(1)


class ResearchLayoutTests(unittest.TestCase):
    def test_research_container_owns_the_fixed_scientific_canvas(self):
        container = css_rule(".research-image")
        self.assertRegex(container, r"aspect-ratio:\s*var\(--research-image-ratio\)")
        self.assertIn("width: 100%", container)
        self.assertIn("overflow: hidden", container)
        self.assertIn("place-items: center", container)
        self.assertIn("--research-image-ratio: 1.4 / 1", THEME)

    def test_research_images_are_contained_and_never_cropped(self):
        image = css_rule(".research-image img")
        self.assertIn("object-fit: contain", image)
        self.assertIn("object-position: center", image)
        self.assertNotIn("object-fit: cover", image)
        self.assertNotIn("aspect-ratio", image)
        self.assertIn("height: 100%", image)
        self.assertIn("max-width: 100%", image)
        self.assertIn("max-height: 100%", image)

        research_styles = CSS[CSS.index(".research-image"):CSS.index(".related-publications")]
        self.assertNotIn("object-fit: cover", research_styles)

    def test_bilingual_pages_use_the_shared_research_image_wrapper(self):
        expected = '<div class="research-image"><img'
        self.assertIn(expected, RESEARCH_EN)
        self.assertIn(expected, RESEARCH_ZH)

    def test_single_column_mobile_layout_is_preserved(self):
        mobile = re.search(
            r"@media\s*\(max-width:\s*900px\)\s*\{(.*?)(?=\n@media|\Z)",
            CSS,
            re.S,
        )
        self.assertIsNotNone(mobile)
        self.assertRegex(mobile.group(1), r"\.research-feature\s*\{[^}]*grid-template-columns:\s*1fr")


if __name__ == "__main__":
    unittest.main()
