#!/usr/bin/env python3
"""Regression checks for CMS-managed secondary page content and SEO metadata."""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PAGES = yaml.safe_load((ROOT / "_data" / "pages.yaml").read_text(encoding="utf-8"))
PAGE_INTRO = (ROOT / "_includes" / "custom" / "page-intro.html").read_text(encoding="utf-8")
META = (ROOT / "_includes" / "meta.html").read_text(encoding="utf-8")
FALLBACK = (ROOT / "_plugins" / "custom_translation_fallback.rb").read_text(encoding="utf-8")
REGISTRY = yaml.safe_load((ROOT / "_translation" / "registry.yml").read_text(encoding="utf-8"))

PAGE_FILES = {
    "research": (ROOT / "research" / "index.md", ROOT / "zh" / "research" / "index.md"),
    "publications": (ROOT / "publications" / "index.md", ROOT / "zh" / "publications" / "index.md"),
    "team": (ROOT / "team" / "index.md", ROOT / "zh" / "team" / "index.md"),
    "opportunities": (ROOT / "opportunities" / "index.md", ROOT / "zh" / "opportunities" / "index.md"),
}

OLD_INTROS = (
    "We study materials, interfaces, and electrochemical processes that shape next-generation energy storage.",
    "Bibliographic metadata is resolved from DOI records and retained in its original language.",
    "Current members are grouped by role. Empty groups are hidden automatically.",
    "Open positions appear below while active. Categories without current openings are hidden.",
    "我们研究面向下一代储能体系的材料、界面与电化学过程。",
    "书目信息由 DOI 自动解析并保留原文，仅课题组自定义说明提供双语版本。",
    "现有成员按岗位分类展示；无内容的分类会自动隐藏。",
    "以下为当前有效岗位；无有效内容的类别会自动隐藏。",
)


class PageContentTests(unittest.TestCase):
    def test_page_settings_file_and_required_chinese_fields_exist(self):
        self.assertIsInstance(PAGES, dict)
        self.assertEqual(set(PAGE_FILES), {"research", "publications", "team", "opportunities"})
        for page_key, settings in PAGES.items():
            with self.subTest(page_key=page_key):
                self.assertIsInstance(settings, dict)
                for field in ("title_zh", "intro_zh", "description_zh"):
                    self.assertIsInstance(settings.get(field), str)
                    self.assertTrue(settings[field].strip())
                for field in ("title_en", "intro_en", "description_en"):
                    self.assertTrue(field not in settings or isinstance(settings[field], str))

    def test_all_eight_pages_use_the_shared_page_key_and_intro_include(self):
        for page_key, paths in PAGE_FILES.items():
            for path in paths:
                text = path.read_text(encoding="utf-8")
                with self.subTest(path=path):
                    self.assertIn(f"page_key: {page_key}", text)
                    self.assertIn(f'{{% include custom/page-intro.html page_key="{page_key}" %}}', text)
                    self.assertFalse(any(old_intro in text for old_intro in OLD_INTROS))

    def test_shared_intro_include_has_bilingual_fallback_and_escaping(self):
        self.assertIn("site.data.pages[include.page_key]", PAGE_INTRO)
        self.assertIn("page_content.title_en | default: page_content.title_zh", PAGE_INTRO)
        self.assertIn("page_content.title_zh | default: page_content.title_en", PAGE_INTRO)
        self.assertIn("page_content.intro_en | default: page_content.intro_zh", PAGE_INTRO)
        self.assertIn("page_content.intro_zh | default: page_content.intro_en", PAGE_INTRO)
        self.assertIn("page_title | escape", PAGE_INTRO)
        self.assertIn("page_intro | escape", PAGE_INTRO)

    def test_meta_resolver_covers_title_description_and_social_metadata(self):
        self.assertIn("site.data.pages[page.page_key]", META)
        self.assertIn("page_content.title_en | default: page_content.title_zh", META)
        self.assertIn("page_content.title_zh | default: page_content.title_en", META)
        self.assertIn("page_content.description_en | default: page_content.description_zh", META)
        self.assertIn("page_content.description_zh | default: page_content.description_en", META)
        self.assertIn('meta name="description" content="{{ description }}"', META)
        self.assertIn('meta property="og:description" content="{{ description }}"', META)
        self.assertIn('meta name="twitter:description" content="{{ description }}"', META)
        self.assertIn('"description": "{{ description }}"', META)

    def test_empty_english_page_fields_use_existing_data_fallback(self):
        self.assertIn('if pattern.start_with?("_data/")', FALLBACK)
        self.assertIn("fill_pairs(site.data[key], pattern, allowed)", FALLBACK)
        self.assertIn("value[en_key] = deep_copy(value[zh_key])", FALLBACK)

    def test_existing_page_body_loops_remain_intact(self):
        markers = {
            "research": "site.research",
            "publications": "site.data.citations",
            "team": "site.data.team_roles",
            "opportunities": "custom/opportunity-group.html",
        }
        for page_key, paths in PAGE_FILES.items():
            for path in paths:
                with self.subTest(path=path):
                    self.assertIn(markers[page_key], path.read_text(encoding="utf-8"))

    def test_translation_registry_includes_pages_without_publication_metadata(self):
        resources = {resource["id"]: resource for resource in REGISTRY["resources"]}
        pages = resources["pages"]
        self.assertEqual(pages["pattern"], "_data/pages.yaml")
        self.assertEqual(set(pages["auto_fields"]), {"title", "intro", "description"})
        self.assertEqual(pages["manual_fields"], [])
        self.assertTrue(resources["publications"]["exclude_all"])


if __name__ == "__main__":
    unittest.main()
