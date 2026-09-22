---
title: Research
description: Research areas and related DOI-linked publications.
permalink: /research/
---

<div class="page-intro"><h1>Research</h1><p>We study materials, interfaces, and electrochemical processes that shape next-generation energy storage.</p></div>
{% assign areas = site.research | where: "display", true | sort: "order" %}
<div class="research-list">
  {% for area in areas %}
    <section class="research-area">
      <div class="research-titlebar"><h2>{{ area.title_en }}</h2><span class="research-order">0{{ forloop.index }}</span></div>
      <div class="research-feature">
        <div class="research-image"><img src="{{ area.graphical_abstract | relative_url }}" alt="{{ area.alt_en }}" loading="lazy"></div>
        <div class="research-copy">
          <p>{{ area.short_intro_en }}</p>
          {% if area.doi_list.size > 0 %}<div class="related-publications"><h3>Related Publications</h3><ul>{% for doi in area.doi_list %}{% include custom/compact-publication.html doi=doi %}{% endfor %}</ul></div>{% endif %}
        </div>
      </div>
    </section>
  {% endfor %}
</div>
