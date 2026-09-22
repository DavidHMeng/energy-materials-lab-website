---
title: 研究方向
description: 课题组研究方向及 DOI 关联论文。
permalink: /zh/research/
---

<div class="page-intro"><h1>研究方向</h1><p>我们研究面向下一代储能体系的材料、界面与电化学过程。</p></div>
{% assign areas = site.research | where: "display", true | sort: "order" %}
<div class="research-list">
  {% for area in areas %}
    <section class="research-area">
      <div class="research-titlebar"><h2>{{ area.title_zh }}</h2><span class="research-order">0{{ forloop.index }}</span></div>
      <div class="research-feature">
        <div class="research-image"><img src="{{ area.graphical_abstract | relative_url }}" alt="{{ area.alt_zh }}" loading="lazy"></div>
        <div class="research-copy">
          <p>{{ area.short_intro_zh }}</p>
          {% if area.doi_list.size > 0 %}<div class="related-publications"><h3>相关论文</h3><ul>{% for doi in area.doi_list %}{% include custom/compact-publication.html doi=doi %}{% endfor %}</ul></div>{% endif %}
        </div>
      </div>
    </section>
  {% endfor %}
</div>
