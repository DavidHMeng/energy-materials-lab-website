#!/usr/bin/env python3
"""Regression checks for the data-driven homepage Events section."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOME_EVENTS = (ROOT / "_includes" / "custom" / "home-events.html").read_text(encoding="utf-8")


class HomepageEventsTests(unittest.TestCase):
    def test_homepage_delegates_events_to_conditional_include(self):
        for path in (ROOT / "index.md", ROOT / "zh" / "index.md"):
            source = path.read_text(encoding="utf-8")
            self.assertIn("{% include custom/home-events.html", source)
            self.assertNotIn('<section aria-labelledby="events-heading"', source)

    def test_empty_or_placeholder_events_are_not_rendered(self):
        self.assertIn("visible_event_count", HOME_EVENTS)
        self.assertIn("item.display != true", HOME_EVENTS)
        self.assertIn("item.published == false", HOME_EVENTS)
        self.assertIn("item.hidden == true", HOME_EVENTS)
        self.assertIn("item.placeholder == true", HOME_EVENTS)
        for marker in ("placeholder", "demo", "sample", "draft", "unpublished", "占位"):
            self.assertIn(f'contains "{marker}"', HOME_EVENTS)
        self.assertIn("{% if visible_event_count > 0 %}", HOME_EVENTS)

    def test_events_functionality_and_placeholder_records_are_separate(self):
        for path in (ROOT / "events" / "index.md", ROOT / "zh" / "events" / "index.md"):
            self.assertTrue(path.exists())
            self.assertIn("site.events", path.read_text(encoding="utf-8"))
        self.assertFalse(list((ROOT / "_events").glob("*placeholder*")))


if __name__ == "__main__":
    unittest.main()
