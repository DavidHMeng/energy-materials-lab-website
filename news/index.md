---
title: News
description: News archive.
permalink: /news/
---

<div class="page-intro"><h1>News</h1><p>Publications, awards, people, achievements, funding, and announcements.</p></div>
{% assign news = site.news | where: "display", true | sort: "date" | reverse %}
<div class="news-grid">{% for item in news %}{% include custom/news-card.html item=item %}{% endfor %}</div>
