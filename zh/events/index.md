---
title: 活动
description: 学术活动与组内活动归档。
permalink: /zh/events/
---

<div class="page-intro"><h1>活动</h1><p>学术活动与组内活动。</p></div>
{% include search-box.html %}
{% include search-info.html %}
{% assign events = site.events | where: "display", true | sort: "date" | reverse %}
<div class="event-grid">{% for item in events %}{% include custom/event-card.html item=item archive=true %}{% endfor %}</div>
