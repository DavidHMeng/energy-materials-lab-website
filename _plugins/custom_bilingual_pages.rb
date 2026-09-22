# frozen_string_literal: true

module LabWebsite
  class LocalizedMemberPage < Jekyll::PageWithoutAFile
    def initialize(site, member)
      slug = member.data["slug"] || member.basename_without_ext
      super(site, site.source, File.join("zh", "team", slug), "index.html")
      self.content = member.content
      self.data = member.data.dup
      self.data["layout"] = "profile"
      self.data["lang"] = "zh"
      self.data["slug"] = slug
      self.data["title"] = member.data["name_zh"]
      self.data["permalink"] = "/zh/team/#{slug}/"
    end
  end

  class BilingualMemberGenerator < Jekyll::Generator
    safe true
    priority :low

    def generate(site)
      collection = site.collections["members"]
      return unless collection

      collection.docs.each do |member|
        next unless member.data.fetch("display", true) && member.data.fetch("active", true)

        site.pages << LocalizedMemberPage.new(site, member)
      end
    end
  end
end
