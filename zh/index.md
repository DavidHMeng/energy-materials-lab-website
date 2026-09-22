---
title: 首页
description: 能源材料课题组的最新动态与活动。
permalink: /zh/
---

{% assign home = site.data.homepage %}
{% assign news = site.news | where: "display", true | sort: "date" | reverse %}
{% assign events = site.events | where: "display", true | sort: "date" %}

<section aria-labelledby="highlights-heading">
  <div class="section-heading">
    <h2 id="highlights-heading">{{ home.highlights_heading_zh }}</h2>
    <a href="{{ '/zh/news/' | relative_url }}">全部动态 <span aria-hidden="true">→</span></a>
  </div>
  <div class="home-news-list">
    {% for item in news limit: home.news_limit %}{% include custom/news-card.html item=item %}{% endfor %}
  </div>
</section>

<section aria-labelledby="events-heading">
  <div class="section-heading">
    <h2 id="events-heading">{{ home.events_heading_zh }}</h2>
    <a href="{{ '/zh/events/' | relative_url }}">全部活动 <span aria-hidden="true">→</span></a>
  </div>
  <div class="event-grid">
    {% for item in events limit: home.events_limit %}{% include custom/event-card.html item=item %}{% endfor %}
  </div>
</section>
