---
permalink: /zh/publications/
page_key: publications
page_class: publications-page
---

{% include custom/page-intro.html page_key="publications" %}
{% assign sorted_citations = site.data.citations | sort: "date" | reverse %}
{% for citation in sorted_citations %}
  {% assign publication = citation.id | find_publication_by_doi: site.data.publications %}
  {% if publication and publication.display != false %}
    {% include citation.html lookup=citation.id style="rich" image=publication.image description=publication.description_zh tags=publication.tags %}
  {% endif %}
{% endfor %}
