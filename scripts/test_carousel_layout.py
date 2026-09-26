#!/usr/bin/env python3
"""Lightweight source-level regression checks for the scientific carousel canvas."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "_styles" / "custom.scss").read_text(encoding="utf-8")
INCLUDE = (ROOT / "_includes" / "custom" / "homepage-introduction.html").read_text(encoding="utf-8")
HOME = (ROOT / "_data" / "homepage.yaml").read_text(encoding="utf-8")


class CarouselLayoutTests(unittest.TestCase):
    def test_fixed_canvas_and_contained_images(self):
        self.assertIn("--scientific-canvas-height: clamp(560px, 69vw, 780px)", CSS)
        self.assertIn("aspect-ratio: 1.4 / 1", CSS)
        self.assertRegex(CSS, r"\.visual-slide-image\s*\{[^}]*height:\s*var\(--scientific-canvas-height\)")
        image_rule = re.search(r"\.visual-slide img\s*\{(.*?)\}", CSS, re.S)
        self.assertIsNotNone(image_rule)
        self.assertIn("object-fit: contain", image_rule.group(1))
        self.assertIn("object-position: center", image_rule.group(1))
        self.assertNotIn("object-fit: cover", image_rule.group(1))

    def test_caption_is_always_present_and_height_stable(self):
        self.assertIn('<figcaption class="visual-slide-caption">', INCLUDE)
        self.assertIn('class="visual-slide-title"', INCLUDE)
        self.assertIn('class="visual-slide-meta"', INCLUDE)
        self.assertIn("grid-template-rows: var(--scientific-canvas-height) 6.25rem", CSS)
        self.assertIn("-webkit-line-clamp: 2", CSS)

    def test_responsive_canvas_ranges_and_reduced_motion_remain(self):
        self.assertIn("--scientific-canvas-height: clamp(420px, 60vw, 540px)", CSS)
        self.assertIn("--scientific-canvas-height: clamp(280px, 88vw, 380px)", CSS)
        self.assertIn("@media (prefers-reduced-motion: reduce)", CSS)
        self.assertIn("reducedMotion.matches", (ROOT / "_scripts" / "custom.js").read_text(encoding="utf-8"))

    def test_current_tall_medium_and_wide_samples_share_one_canvas(self):
        # The three CMS-managed real GA files cover tall (1.16:1), medium (1.33:1)
        # and wide (1.72:1) source proportions without altering or cropping pixels.
        self.assertIn("/images/uploads/4156020251853fig1.jpg", HOME)
        self.assertIn("/images/uploads/anie73531-fig-0001-m.jpg", HOME)
        self.assertIn("/images/uploads/anie74845-fig-0001-m.jpg", HOME)
        canvas_width, canvas_height = 1120, 780
        for ratio in (1602 / 1381, 1640 / 1233, 1640 / 954):
            rendered_width = min(canvas_width, canvas_height * ratio)
            rendered_height = min(canvas_height, canvas_width / ratio)
            self.assertLessEqual(rendered_width, canvas_width)
            self.assertLessEqual(rendered_height, canvas_height)


if __name__ == "__main__":
    unittest.main()
