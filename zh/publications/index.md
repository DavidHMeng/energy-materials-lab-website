---
title: 论文发表
description: 以 DOI 为唯一数据源的论文列表；书目信息保留原文。
permalink: /zh/publications/
page_class: publications-page
---

<div class="page-intro"><h1>论文发表</h1><p>书目信息由 DOI 自动解析并保留原文，仅课题组自定义说明提供双语版本。</p></div>
{% assign publications = site.data.citations | sort: "date" | reverse %}
{% for citation in publications %}
  {% include citation.html lookup=citation.id style="rich" %}
  {% if citation.description_zh %}<p class="citation-custom-note">{{ citation.description_zh }}</p>{% endif %}
{% endfor %}
