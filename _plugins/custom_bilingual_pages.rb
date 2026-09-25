# frozen_string_literal: true

module LabWebsite
  Jekyll::Hooks.register :documents, :post_init do |document|
    next unless document.collection&.label == "members"

    slug = document.data["slug"] || document.basename_without_ext
    document.data["permalink"] = "/team/#{slug}/"
  end

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

        # The editable slug is the public member ID. Use it for the English
        # collection URL as well as the generated Chinese page so a CMS slug
        # edit cannot leave the two language trees out of sync with the file name.
        slug = member.data["slug"] || member.basename_without_ext
        member.data["permalink"] = "/team/#{slug}/"
        site.pages << LocalizedMemberPage.new(site, member)
      end
    end
  end
end
