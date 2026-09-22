---
title: Events
description: Academic and group event archive.
permalink: /events/
---

<div class="page-intro"><h1>Events</h1><p>Academic events and group activities.</p></div>
{% assign events = site.events | where: "display", true | sort: "date" | reverse %}
<div class="event-grid">{% for item in events %}{% include custom/event-card.html item=item archive=true %}{% endfor %}</div>
