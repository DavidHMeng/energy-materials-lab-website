---
title: 课题组动态
description: 课题组动态归档。
permalink: /zh/news/
---

<div class="page-intro"><h1>课题组动态</h1><p>论文、获奖、成员、学术成果、项目与通知。</p></div>
{% assign news = site.news | where: "display", true | sort: "date" | reverse %}
<div class="news-grid">{% for item in news %}{% include custom/news-card.html item=item %}{% endfor %}</div>
