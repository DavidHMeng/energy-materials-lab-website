#!/usr/bin/env python3
"""Coverage and all-English-empty QA for Chinese-primary authoring."""

from __future__ import annotations

import unittest

from check_translation_coverage import load_coverage
from prepare_empty_english_fixture import remove_registered_english
from translate_content import TranslationResult, load_registry, process_pair, translation_rules, walk_pairs


class TranslationCoverageTests(unittest.TestCase):
    def test_every_cms_chinese_field_has_a_registry_decision(self):
        rows, warnings = load_coverage()
        self.assertGreater(len(rows), 0)
        self.assertEqual(warnings, [])
        self.assertNotIn("UNREGISTERED", {row["status"] for row in rows})

    def test_all_english_empty_auto_fields_generate_or_degrade_to_pending(self):
        for resource in load_registry()["resources"]:
            for stem in resource.get("auto_fields", []):
                with self.subTest(resource=resource["id"], stem=stem):
                    record = {f"{stem}_zh": f"中文 QA {resource['id']} {stem}"}
                    pair = list(walk_pairs(record, {stem}))[0]

                    unavailable_state = {}
                    unavailable_result = TranslationResult()
                    process_pair(*pair[:3], unavailable_state, None, unavailable_result)
                    self.assertNotIn(f"{stem}_en", record)
                    self.assertEqual(unavailable_state["status"], "pending")

                    generated_state = {}
                    generated_result = TranslationResult()
                    process_pair(*pair[:3], generated_state, lambda value: f"Academic EN: {value}", generated_result)
                    self.assertTrue(record[f"{stem}_en"].startswith("Academic EN:"))
                    self.assertEqual(generated_state["status"], "auto")

    def test_provider_errors_are_non_blocking(self):
        def fail(_: str) -> str:
            raise TimeoutError("simulated provider timeout")

        record = {"title_zh": "中文标题"}
        state = {}
        result = TranslationResult()
        process_pair(record, "title_zh", "title_en", state, fail, result)
        self.assertNotIn("title_en", record)
        self.assertEqual(state["status"], "pending")
        self.assertEqual(state["last_error"], "provider-unavailable")
        self.assertEqual(result.failed, 1)

    def test_empty_english_fixture_removes_nested_optional_values(self):
        record = {
            "title_zh": "中文",
            "title_en": "English",
            "slides": [{"caption_zh": "说明", "caption_en": "Caption"}],
            "doi": "10.1000/example",
        }
        removed = remove_registered_english(record, {"title", "caption"})
        self.assertEqual(removed, 2)
        self.assertNotIn("title_en", record)
        self.assertNotIn("caption_en", record["slides"][0])
        self.assertEqual(record["doi"], "10.1000/example")

    def test_manual_only_fields_and_publications_never_enter_machine_rules(self):
        machine_fields = {pattern: fields for pattern, fields in translation_rules()}
        self.assertNotIn("_data/sources.yaml", machine_fields)
        self.assertNotIn("name", machine_fields["_members/*.md"])
        self.assertNotIn("label", machine_fields.get("_data/team_roles.yaml", set()))
        self.assertNotIn("lab_name", machine_fields["_data/site.yaml"])


if __name__ == "__main__":
    unittest.main()
