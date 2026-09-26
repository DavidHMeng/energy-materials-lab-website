---
permalink: /zh/team/
page_key: team
---

{% include custom/page-intro.html page_key="team" %}
{% assign roles = site.data.team_roles | where: "display", true | sort: "order" %}
{% for role in roles %}{% include custom/team-grid.html role_id=role.id label_en=role.label_en label_zh=role.label_zh %}{% endfor %}
