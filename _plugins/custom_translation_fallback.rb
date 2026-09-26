# frozen_string_literal: true

# English editorial fields are optional in Pages CMS. This generator fills a missing
# *_en value in Jekyll's in-memory representation from its Chinese source. The same
# central registry drives the asynchronous translator, coverage QA and this fallback.
require "yaml"

module LabWebsite
  class TranslationFallbackGenerator < Jekyll::Generator
    safe true
    priority :highest

    def generate(site)
      registry(site).fetch("resources").each do |resource|
        next if resource["exclude_all"]

        allowed = Array(resource["auto_fields"]) + Array(resource["manual_fields"])
        next if allowed.empty?

        apply_resource(site, resource.fetch("pattern"), allowed)
      end
    end

    private

    def registry(site)
      path = File.join(site.source, "_translation", "registry.yml")
      YAML.safe_load_file(path, permitted_classes: [], aliases: false)
    end

    def apply_resource(site, pattern, allowed)
      if pattern.start_with?("_data/")
        key = File.basename(pattern, ".yaml")
        fill_pairs(site.data[key], pattern, allowed)
        return
      end

      collection_name = pattern.split("/").first.delete_prefix("_")
      collection = site.collections[collection_name]
      return unless collection

      collection.docs.each { |document| fill_pairs(document.data, document.relative_path, allowed) }
    end

    def fill_pairs(value, location, allowed)
      case value
      when Hash
        value.keys.grep(/_zh\z/).each do |zh_key|
          stem = zh_key.sub(/_zh\z/, "")
          next unless allowed.include?(stem)

          en_key = zh_key.sub(/_zh\z/, "_en")
          next if blank?(value[zh_key]) || !blank?(value[en_key])

          value[en_key] = deep_copy(value[zh_key])
          Jekyll.logger.warn "Bilingual fallback:", "#{location} #{en_key} uses Chinese source"
        end
        value.each { |key, child| fill_pairs(child, "#{location}.#{key}", allowed) }
      when Array
        value.each_with_index { |child, index| fill_pairs(child, "#{location}[#{index}]", allowed) }
      end
    end

    def blank?(value)
      value.nil? || (value.respond_to?(:empty?) && value.empty?)
    end

    def deep_copy(value)
      Marshal.load(Marshal.dump(value))
    end
  end
end
