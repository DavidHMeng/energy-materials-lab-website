# frozen_string_literal: true

require "cgi"

module LabCustomFilters
  ZH_UI_LABELS = {
    "Publication" => "论文发表",
    "Award" => "获奖",
    "Member" => "成员动态",
    "Academic Achievement" => "学术成果",
    "Funding" => "科研项目",
    "Announcement" => "通知",
    "Academic" => "学术活动",
    "Group" => "组内活动",
    "Seminar" => "学术报告",
    "Group Meeting" => "组会"
  }.freeze

  def ui_label_zh(value)
    ZH_UI_LABELS.fetch(value.to_s, value.to_s)
  end

  def find_citation_by_doi(doi, citations)
    needle = normalize_doi(doi)
    return nil if needle.empty?

    Array(citations).find do |citation|
      normalize_doi(citation.fetch("id", "")) == needle
    end
  end

  def find_publication_by_doi(doi, publications)
    needle = normalize_doi(doi)
    return nil if needle.empty?

    Array(publications).find do |publication|
      normalize_doi(publication.fetch("doi", "")) == needle
    end
  end

  def normalize_doi(value)
    candidate = CGI.unescape(value.to_s.strip)
    previous = nil
    while candidate != previous
      previous = candidate
      candidate = candidate.sub(%r{\Ahttps?://(?:dx\.)?doi\.org/}i, "").strip
      candidate = candidate.sub(/\Adoi\s*[:：]\s*/i, "").strip
    end
    return "" unless candidate.match?(%r{\A10\.\d{4,9}/\S+\z}i)

    candidate.downcase
  end

  def doi_url(value)
    doi = normalize_doi(value)
    doi.empty? ? "" : "https://doi.org/#{doi}"
  end

  def surname(name)
    name.to_s.strip.split.last.to_s
  end

  def citations_for_member(citations, member_id)
    Array(citations).select { |citation| Array(citation["member_ids"]).include?(member_id) }
  end

  def opportunity_visible(opportunity, now = Time.now)
    display = opportunity["display"]
    display = true if display.nil?
    return false unless display

    override = opportunity["active_override"] || "auto"
    return true if override == "force_show"
    return false if override == "force_hide"

    today = now.strftime("%Y-%m-%d")
    opens = opportunity["opening_date"].to_s
    closes = opportunity["closing_date"].to_s
    (opens.empty? || opens <= today) && (closes.empty? || closes >= today)
  end
end

Liquid::Template.register_filter(LabCustomFilters)
