---
title: Home
description: Latest news and events from the Placeholder Energy Materials Lab.
permalink: /
page_class: homepage-page
---

{% assign home = site.data.homepage %}
{% assign news = site.news | where: "display", true | sort: "date" | reverse %}
{% assign events = site.events | where: "display", true | sort: "date" %}

{% include custom/homepage-introduction.html %}

<section aria-labelledby="highlights-heading" data-reveal>
  <div class="section-heading">
    <h2 id="highlights-heading">{{ home.highlights_heading_en | default: home.highlights_heading_zh }}</h2>
    <a href="{{ '/news/' | relative_url }}">Archive <span aria-hidden="true">→</span></a>
  </div>
  <div class="home-news-list">
    {% for item in news limit: home.news_limit %}{% include custom/news-card.html item=item %}{% endfor %}
  </div>
</section>

<section aria-labelledby="events-heading" data-reveal>
  <div class="section-heading">
    <h2 id="events-heading">{{ home.events_heading_en | default: home.events_heading_zh }}</h2>
    <a href="{{ '/events/' | relative_url }}">Archive <span aria-hidden="true">→</span></a>
  </div>
  <div class="event-grid">
    {% for item in events limit: home.events_limit %}{% include custom/event-card.html item=item %}{% endfor %}
  </div>
</section>
