#!/usr/bin/env python3
"""Regression checks for the header logo's proportional, state-based layout."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "_styles" / "custom.scss").read_text(encoding="utf-8")
HEADER = (ROOT / "_includes" / "header.html").read_text(encoding="utf-8")
SITE = (ROOT / "_data" / "site.yaml").read_text(encoding="utf-8")


def css_rule(selector: str) -> str:
    match = re.search(rf"(?m)^{re.escape(selector)}\s*\{{(.*?)\}}", CSS, re.S)
    if match is None:
        raise AssertionError(f"Missing CSS rule: {selector}")
    return match.group(1)


class HeaderLogoLayoutTests(unittest.TestCase):
    def test_logo_images_are_intrinsic_and_contained(self):
        image = css_rule("header .home .logo img,\nheader .home .logo svg")
        for declaration in (
            "width: auto",
            "height: auto",
            "max-width: 100%",
            "max-height: 100%",
            "object-fit: contain",
            "object-position: center",
            "aspect-ratio: auto",
        ):
            self.assertIn(declaration, image)
        self.assertNotIn("object-fit: cover", image)

    def test_each_header_state_sizes_the_container(self):
        self.assertIn("--logo-hero-box: clamp(88px, 8vw, 100px)", CSS)
        self.assertIn("--logo-nav-box: clamp(58px, 5vw, 66px)", CSS)
        self.assertIn("--logo-nav-box-scrolled: clamp(52px, 4.4vw, 58px)", CSS)
        self.assertIn("--logo-mobile-box: clamp(42px, 12vw, 48px)", CSS)
        self.assertRegex(
            CSS,
            r"header\.background\[data-big\] \.home \.logo\s*\{[^}]*width:\s*var\(--logo-hero-box\)[^}]*height:\s*var\(--logo-hero-box\)",
        )
        self.assertRegex(
            CSS,
            r"header\.background:not\(\[data-big\]\)\.is-scrolled \.home \.logo\s*\{[^}]*width:\s*var\(--logo-nav-box-scrolled\)[^}]*height:\s*var\(--logo-nav-box-scrolled\)",
        )
        self.assertRegex(
            CSS,
            re.compile(
                r"@media\s*\(max-width:\s*700px\).*?header\.background:not\(\[data-big\]\) \.home \.logo\s*\{[^}]*width:\s*var\(--logo-mobile-box\)[^}]*height:\s*var\(--logo-mobile-box\)",
                re.S,
            ),
        )

    def test_header_uses_optional_trimmed_logo_with_fallback(self):
        self.assertIn("site.data.site.lab_logo_header | default: site.data.site.lab_logo", HEADER)
        match = re.search(r"lab_logo_header:\s*(\S+)", SITE)
        self.assertIsNotNone(match)
        self.assertTrue((ROOT / match.group(1).lstrip("/")).is_file())

    def test_logo_selectors_do_not_reintroduce_fixed_image_dimensions(self):
        # The shared img/svg rule may only constrain images by max dimensions.
        self.assertNotRegex(
            CSS,
            r"header[^\{]*\.logo\s+(?:img|svg)[^{]*\{[^}]*\bwidth:\s*\d+px[^}]*\bheight:\s*\d+px",
        )


if __name__ == "__main__":
    unittest.main()
