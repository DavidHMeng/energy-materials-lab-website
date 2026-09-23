---
title: Team
description: Current members of the research group.
permalink: /team/
---

<div class="page-intro"><h1>Team</h1><p>Current members are grouped by role. Empty groups are hidden automatically.</p></div>
{% assign roles = site.data.team_roles | where: "display", true | sort: "order" %}
{% for role in roles %}{% include custom/team-grid.html role_id=role.id label_en=role.label_en label_zh=role.label_zh %}{% endfor %}
