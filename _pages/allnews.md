---
title: "News"
layout: textlay
excerpt: "CDAC news archive."
sitemap: false
permalink: /allnews.html
---

# News

<div markdown="0">
{% for article in site.data.news %}
<p><strong>{{ article.date }}</strong><br>
{{ article.headline | markdownify | replace: '<p>', '' | replace: '</p>', '' }}</p>
{% endfor %}
</div>
