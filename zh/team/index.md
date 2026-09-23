---
title: 团队成员
description: 课题组现有成员。
permalink: /zh/team/
---

<div class="page-intro"><h1>团队成员</h1><p>现有成员按岗位分类展示；无内容的分类会自动隐藏。</p></div>
{% assign roles = site.data.team_roles | where: "display", true | sort: "order" %}
{% for role in roles %}{% include custom/team-grid.html role_id=role.id label_en=role.label_en label_zh=role.label_zh %}{% endfor %}
