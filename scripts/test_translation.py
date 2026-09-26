#!/usr/bin/env python3
"""State-machine regression tests for the bilingual translation workflow."""

from __future__ import annotations

import unittest
from io import BytesIO
from unittest.mock import patch

from translate_content import DeepLTranslator, TranslationResult, configured_translator, digest, process_pair, prune_deleted_entries, translation_rules, walk_pairs


class TranslationStateTests(unittest.TestCase):
    def test_missing_english_key_is_discovered(self):
        record = {"title_zh": "中文"}
        pairs = list(walk_pairs(record, {"title"}))
        self.assertEqual(len(pairs), 1)
        container, zh_key, en_key, field_path = pairs[0]
        self.assertIs(container, record)
        self.assertEqual((zh_key, en_key, field_path), ("title_zh", "title_en", "title"))

    def test_page_settings_are_registered_as_auto_translatable_yaml_fields(self):
        rules = dict(translation_rules())
        self.assertEqual(rules["_data/pages.yaml"], {"title", "intro", "description"})

    def test_missing_english_key_becomes_pending_without_provider(self):
        record = {"title_zh": "中文"}
        state = {}
        result = TranslationResult()
        process_pair(record, "title_zh", "title_en", state, None, result)
        self.assertNotIn("title_en", record)
        self.assertEqual(state["status"], "pending")
        self.assertEqual(result.pending, 1)

    def test_missing_english_is_generated(self):
        record = {"title_zh": "中文", "title_en": ""}
        state = {}
        result = TranslationResult()
        process_pair(record, "title_zh", "title_en", state, lambda value: f"EN:{value}", result)
        self.assertEqual(record["title_en"], "EN:中文")
        self.assertEqual(state["status"], "auto")

    def test_provider_failure_does_not_raise_or_break_fallback(self):
        record = {"title_zh": "中文", "title_en": ""}
        state = {}
        result = TranslationResult()

        def unavailable(_: str) -> str:
            raise RuntimeError("simulated outage")

        process_pair(record, "title_zh", "title_en", state, unavailable, result)
        self.assertEqual(record["title_en"], "")
        self.assertEqual(state["status"], "pending")
        self.assertEqual(result.failed, 1)

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

    def test_deleted_content_prunes_only_stale_state(self):
        entries = {
            "_members/current.md": {"position": {"status": "manual"}},
            "_members/deleted-placeholder.md": {"position": {"status": "pending"}},
        }
        result = TranslationResult()
        prune_deleted_entries(entries, {"_members/current.md"}, result)
        self.assertEqual(set(entries), {"_members/current.md"})
        self.assertEqual(result.pruned, 1)
        self.assertTrue(result.changed_state)

    @patch.dict("os.environ", {"TRANSLATION_PROVIDER": "deepl", "TRANSLATION_API_KEY": "test-key:fx"}, clear=True)
    def test_deepl_provider_does_not_require_model(self):
        translator = configured_translator("deepl")
        self.assertIsInstance(translator, DeepLTranslator)
        self.assertEqual(translator.api_base, "https://api-free.deepl.com")

    @patch.dict("os.environ", {"TRANSLATION_API_KEY": "test-key", "TRANSLATION_API_BASE": "https://api.deepl.test"}, clear=True)
    @patch("urllib.request.urlopen")
    def test_deepl_request_and_response(self, urlopen):
        response = BytesIO(b'{"translations":[{"detected_source_language":"ZH","text":"Academic English"}]}')
        response.__enter__ = lambda value: value
        response.__exit__ = lambda *args: None
        urlopen.return_value = response

        translated = DeepLTranslator()("中文内容")

        self.assertEqual(translated, "Academic English")
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.deepl.test/v2/translate")
        self.assertEqual(request.headers["Authorization"], "DeepL-Auth-Key test-key")
        payload = __import__("json").loads(request.data)
        self.assertEqual(payload["source_lang"], "ZH")
        self.assertEqual(payload["target_lang"], "EN-US")
        self.assertTrue(payload["preserve_formatting"])


if __name__ == "__main__":
    unittest.main()
