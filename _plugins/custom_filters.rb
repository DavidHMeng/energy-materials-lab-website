# frozen_string_literal: true

module LabCustomFilters
  def find_citation_by_doi(doi, citations)
    needle = doi.to_s.downcase.sub(%r{^https?://(dx\.)?doi\.org/}, "").sub(/^doi:/, "")
    Array(citations).find do |citation|
      citation.fetch("id", "").to_s.downcase.sub(/^doi:/, "") == needle
    end
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
