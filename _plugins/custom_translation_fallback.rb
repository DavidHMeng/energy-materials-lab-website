# frozen_string_literal: true

# English editorial fields are optional in Pages CMS.  This generator fills a missing
# *_en value in Jekyll's in-memory representation from its Chinese source.  It never
# changes repository files and deliberately skips publication/citation data.
module LabWebsite
  class TranslationFallbackGenerator < Jekyll::Generator
    safe true
    priority :highest

    EXCLUDED_DATA_ROOTS = %w[citations sources translation-state].freeze

    def generate(site)
      site.data.each do |root, value|
        next if EXCLUDED_DATA_ROOTS.include?(root.to_s)

        fill_pairs(value, "_data/#{root}", site)
      end

      site.collections.each_value do |collection|
        next if collection.label == "posts"

        collection.docs.each do |document|
          fill_pairs(document.data, document.relative_path, site)
        end
      end
    end

    private

    def fill_pairs(value, location, site)
      case value
      when Hash
        value.keys.grep(/_zh\z/).each do |zh_key|
          en_key = zh_key.sub(/_zh\z/, "_en")
          next unless value.key?(en_key)
          next if blank?(value[zh_key]) || !blank?(value[en_key])

          value[en_key] = deep_copy(value[zh_key])
          Jekyll.logger.warn "Bilingual fallback:", "#{location} #{en_key} uses Chinese source"
        end
        value.each { |key, child| fill_pairs(child, "#{location}.#{key}", site) }
      when Array
        value.each_with_index { |child, index| fill_pairs(child, "#{location}[#{index}]", site) }
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
