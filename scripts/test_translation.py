#!/usr/bin/env python3
"""State-machine regression tests for the bilingual translation workflow."""

from __future__ import annotations

import unittest

from translate_content import TranslationResult, digest, process_pair


class TranslationStateTests(unittest.TestCase):
    def test_missing_english_is_generated(self):
        record = {"title_zh": "中文", "title_en": ""}
        state = {}
        result = TranslationResult()
        process_pair(record, "title_zh", "title_en", state, lambda value: f"EN:{value}", result)
        self.assertEqual(record["title_en"], "EN:中文")
        self.assertEqual(state["status"], "auto")

    def test_manual_english_is_never_overwritten(self):
        record = {"title_zh": "新版中文", "title_en": "Official English"}
        state = {"status": "manual", "source_hash": digest("旧版中文"), "english_hash": digest("Official English")}
        result = TranslationResult()
        process_pair(record, "title_zh", "title_en", state, lambda _: "Replacement", result)
        self.assertEqual(record["title_en"], "Official English")
        self.assertEqual(state["status"], "needs-review")

    def test_auto_english_refreshes_after_chinese_change(self):
        record = {"title_zh": "新版中文", "title_en": "Old automatic English"}
        state = {"status": "auto", "source_hash": digest("旧版中文"), "generated_hash": digest("Old automatic English")}
        result = TranslationResult()
        process_pair(record, "title_zh", "title_en", state, lambda _: "New automatic English", result)
        self.assertEqual(record["title_en"], "New automatic English")
        self.assertEqual(result.refreshed, 1)

    def test_manual_edit_of_generated_english_is_detected(self):
        record = {"title_zh": "中文", "title_en": "Human revision"}
        state = {"status": "auto", "source_hash": digest("中文"), "generated_hash": digest("Automatic")}
        result = TranslationResult()
        process_pair(record, "title_zh", "title_en", state, lambda _: "Ignored", result)
        self.assertEqual(record["title_en"], "Human revision")
        self.assertEqual(state["status"], "manual")


if __name__ == "__main__":
    unittest.main()
