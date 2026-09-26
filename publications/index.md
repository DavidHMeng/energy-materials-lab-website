---
title: Publications
description: DOI-driven publication list with original bibliographic metadata.
permalink: /publications/
page_class: publications-page
---

<div class="page-intro"><h1>Publications</h1><p>Bibliographic metadata is resolved from DOI records and retained in its original language.</p></div>
{% assign publications = site.data.citations | where_exp: "citation", "citation.publication_visible != false" | sort: "date" | reverse %}
{% for citation in publications %}
  {% include citation.html lookup=citation.id style="rich" %}
  {% if citation.description_en %}<p class="citation-custom-note">{{ citation.description_en }}</p>{% endif %}
{% endfor %}
