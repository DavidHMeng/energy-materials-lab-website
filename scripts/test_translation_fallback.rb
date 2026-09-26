# frozen_string_literal: true

require "jekyll"
require_relative "../_plugins/custom_translation_fallback"

generator = LabWebsite::TranslationFallbackGenerator.new
record = {
  "title_zh" => "中文标题",
  "title_en" => "",
  "name_zh" => "梁剑文",
  "official_zh" => "官方中文",
  "unregistered_zh" => "不得自动处理"
}

generator.send(:fill_pairs, record, "qa-fixture", %w[title name official])

raise "automatic field fallback failed" unless record["title_en"] == "中文标题"
raise "manual-only name fallback failed" unless record["name_en"] == "梁剑文"
raise "missing English key fallback failed" unless record["official_en"] == "官方中文"
raise "unregistered field was mutated" if record.key?("unregistered_en")

puts "Translation fallback fixture passed."
