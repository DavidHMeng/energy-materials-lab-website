---
permalink: /zh/publications/
page_key: publications
page_class: publications-page
---

{% include custom/page-intro.html page_key="publications" %}
{% assign publications = site.data.citations | where_exp: "citation", "citation.publication_visible != false" | sort: "date" | reverse %}
{% for citation in publications %}
  {% include citation.html lookup=citation.id style="rich" %}
  {% if citation.description_zh %}<p class="citation-custom-note">{{ citation.description_zh }}</p>{% endif %}
{% endfor %}
