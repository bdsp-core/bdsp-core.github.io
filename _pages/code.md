---
title: "CDAC - Code"
layout: textlay
excerpt: "CDAC Code Catalog"
sitemap: false
permalink: /code/
---

<style>
/* Sticky search bar */
.sticky-search {
 position: sticky;
 top: 0;
 background: white;
 padding: 20px;
 border: 1px solid #ddd;
 border-radius: 8px;
 margin-bottom: 20px;
 box-shadow: 0 2px 8px rgba(0,0,0,0.1);
 z-index: 1000;
}
.repo-search {
 width: 100%;
 padding: 12px;
 margin-bottom: 10px;
 border: 2px solid #ddd;
 border-radius: 6px;
 font-size: 16px;
 transition: border-color 0.3s ease;
}
.repo-search:focus {
 outline: none;
 border-color: #3498db;
}
.search-stats {
 display: flex;
 justify-content: space-between;
 align-items: center;
 font-size: 14px;
 color: #7f8c8d;
}

/* Category navigation */
.category-nav {
 background: white;
 padding: 20px;
 border: 1px solid #ddd;
 border-radius: 8px;
 margin-bottom: 30px;
 box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.category-nav h3 {
 margin-top: 0;
 margin-bottom: 15px;
 color: #2c3e50;
}
.toc-grid {
 display: grid;
 grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
 gap: 8px;
}
.toc-link {
 padding: 8px 12px;
 background: #f8f9fa;
 border: 1px solid #e9ecef;
 border-radius: 4px;
 text-decoration: none;
 transition: all 0.2s ease;
 display: block;
 cursor: pointer;
 color: #333;
}
.toc-link:hover {
 background: #3498db;
 color: white;
 text-decoration: none;
}
.toc-link.active {
 background: #3498db;
 color: white;
 border-color: #3498db;
}

/* Section headers */
.section-header {
 background: linear-gradient(135deg, #34495e, #2c3e50);
 color: white;
 padding: 15px 20px;
 margin: 40px 0 20px 0;
 border-radius: 8px;
 box-shadow: 0 2px 4px rgba(0,0,0,0.1);
 position: relative;
}
.section-header:first-of-type {
 margin-top: 0;
}
.section-header::before {
 content: '';
 position: absolute;
 left: 0;
 top: 0;
 height: 100%;
 width: 4px;
 background: #3498db;
 border-radius: 8px 0 0 8px;
}

/* Repo count badge */
.repo-count {
 font-size: 12px;
 color: #7f8c8d;
 margin-left: 8px;
 background: #ecf0f1;
 padding: 2px 8px;
 border-radius: 12px;
}
.section-header .repo-count {
 color: rgba(255,255,255,0.8);
 background: rgba(255,255,255,0.15);
}

/* Repo cards */
.repo-card {
 padding: 15px 20px;
 margin: 0 0 12px;
 background-color: #f8f9fa;
 border-left: 4px solid #3498db;
 border-radius: 5px;
 box-shadow: 0 1px 3px rgba(0,0,0,0.1);
 transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.repo-card:hover {
 transform: translateY(-2px);
 box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}
.repo-card-header {
 display: flex;
 align-items: center;
 flex-wrap: wrap;
 gap: 8px;
 margin-bottom: 6px;
}
.repo-card-header h4 {
 margin: 0;
 font-size: 17px;
}
.repo-card-header h4 a {
 color: #2c3e50;
 text-decoration: none;
}
.repo-card-header h4 a:hover {
 color: #3498db;
 text-decoration: underline;
}
.repo-description {
 margin: 0 0 8px;
 color: #555;
 font-size: 14px;
 line-height: 1.4;
}
.repo-meta {
 display: flex;
 flex-wrap: wrap;
 gap: 10px;
 align-items: center;
}

/* Language badges */
.language-badge {
 display: inline-block;
 padding: 2px 8px;
 border-radius: 12px;
 font-size: 11px;
 font-weight: 600;
 color: white;
}
.language-python { background-color: #3572A5; }
.language-matlab { background-color: #e16737; }
.language-r { background-color: #198CE7; }
.language-jupyter-notebook { background-color: #DA5B0B; }
.language-javascript { background-color: #f1e05a; color: #333; }
.language-html { background-color: #e34c26; }
.language-shell { background-color: #89e051; color: #333; }
.language-default { background-color: #6c757d; }

/* Stat badges */
.stat-badge {
 font-size: 12px;
 color: #7f8c8d;
}
.stat-badge.updated {
 color: #95a5a6;
}

/* Private badge */
.private-badge {
 display: inline-block;
 padding: 2px 8px;
 border-radius: 12px;
 font-size: 11px;
 font-weight: 600;
 background-color: #e9ecef;
 color: #6c757d;
 border: 1px solid #ced4da;
}

/* Search highlighting */
.highlight {
 background-color: #ffeb3b;
 padding: 1px 2px;
 border-radius: 2px;
}

/* Back to top button */
.back-to-top {
 position: fixed;
 bottom: 30px;
 right: 30px;
 background: #3498db;
 color: white;
 padding: 12px 16px;
 border-radius: 50%;
 text-decoration: none;
 box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
 opacity: 0;
 visibility: hidden;
 transition: all 0.3s ease;
 z-index: 1000;
 cursor: pointer;
 border: none;
 font-size: 18px;
}
.back-to-top.visible {
 opacity: 1;
 visibility: visible;
}
.back-to-top:hover {
 background: #2980b9;
 transform: translateY(-2px);
 text-decoration: none;
 color: white;
}

/* Responsive */
@media (max-width: 768px) {
 .sticky-search {
  padding: 15px;
 }
 .category-nav {
  padding: 15px;
 }
 .toc-grid {
  grid-template-columns: 1fr;
 }
 .repo-card {
  padding: 12px 15px;
 }
 .repo-card-header h4 {
  font-size: 15px;
 }
 .back-to-top {
  bottom: 20px;
  right: 20px;
  padding: 10px 14px;
 }
}
</style>

<script>
function searchRepos() {
 var searchTerm = document.getElementById('repoSearch').value.toLowerCase().trim();
 var allCards = document.querySelectorAll('.repo-card');
 var sections = document.querySelectorAll('.category-section');
 var totalVisible = 0;

 // Clear previous highlights
 var highlights = document.querySelectorAll('.highlight');
 for (var i = 0; i < highlights.length; i++) {
  highlights[i].outerHTML = highlights[i].innerHTML;
 }

 // Filter cards
 for (var j = 0; j < allCards.length; j++) {
  var card = allCards[j];
  var name = card.getAttribute('data-name');
  var desc = card.getAttribute('data-description');
  var lang = card.getAttribute('data-language');
  var cat = card.getAttribute('data-category');
  var matches = searchTerm === '' ||
                name.indexOf(searchTerm) !== -1 ||
                desc.indexOf(searchTerm) !== -1 ||
                lang.indexOf(searchTerm) !== -1 ||
                cat.indexOf(searchTerm) !== -1;

  if (matches) {
   card.style.display = '';
   totalVisible++;
   if (searchTerm !== '') {
    highlightText(card, searchTerm);
   }
  } else {
   card.style.display = 'none';
  }
 }

 // Hide/show category sections based on visible cards
 for (var k = 0; k < sections.length; k++) {
  var section = sections[k];
  var cards = section.querySelectorAll('.repo-card');
  var hasVisible = false;
  for (var m = 0; m < cards.length; m++) {
   if (cards[m].style.display !== 'none') {
    hasVisible = true;
    break;
   }
  }
  section.style.display = (hasVisible || searchTerm === '') ? '' : 'none';
 }

 // Update search info
 var searchInfo = document.getElementById('searchInfo');
 if (searchTerm !== '') {
  searchInfo.textContent = 'Found ' + totalVisible + ' repo' + (totalVisible !== 1 ? 's' : '') + ' matching "' + searchTerm + '"';
 } else {
  searchInfo.textContent = '';
 }

 // Clear category filter active state when searching
 if (searchTerm !== '') {
  var links = document.querySelectorAll('.toc-link');
  for (var n = 0; n < links.length; n++) {
   links[n].classList.remove('active');
  }
 }
}

function filterByCategory(slug) {
 var sections = document.querySelectorAll('.category-section');

 // Clear search
 document.getElementById('repoSearch').value = '';
 var highlights = document.querySelectorAll('.highlight');
 for (var i = 0; i < highlights.length; i++) {
  highlights[i].outerHTML = highlights[i].innerHTML;
 }
 document.getElementById('searchInfo').textContent = '';

 // Update active nav
 var links = document.querySelectorAll('.toc-link');
 for (var j = 0; j < links.length; j++) {
  links[j].classList.remove('active');
 }
 var activeLink = document.getElementById('filter-' + slug);
 if (activeLink) activeLink.classList.add('active');

 // Show/hide sections
 for (var k = 0; k < sections.length; k++) {
  var section = sections[k];
  if (section.getAttribute('data-category') === slug) {
   section.style.display = '';
   var cards = section.querySelectorAll('.repo-card');
   for (var m = 0; m < cards.length; m++) {
    cards[m].style.display = '';
   }
  } else {
   section.style.display = 'none';
  }
 }

 // Scroll to category
 var target = document.getElementById('category-' + slug);
 if (target) {
  target.scrollIntoView({ behavior: 'smooth', block: 'start' });
 }
}

function showAllRepos() {
 var sections = document.querySelectorAll('.category-section');
 var cards = document.querySelectorAll('.repo-card');

 // Clear search
 document.getElementById('repoSearch').value = '';
 var highlights = document.querySelectorAll('.highlight');
 for (var i = 0; i < highlights.length; i++) {
  highlights[i].outerHTML = highlights[i].innerHTML;
 }
 document.getElementById('searchInfo').textContent = '';

 // Update active nav
 var links = document.querySelectorAll('.toc-link');
 for (var j = 0; j < links.length; j++) {
  links[j].classList.remove('active');
 }
 document.getElementById('filter-all').classList.add('active');

 // Show everything
 for (var k = 0; k < sections.length; k++) {
  sections[k].style.display = '';
 }
 for (var m = 0; m < cards.length; m++) {
  cards[m].style.display = '';
 }
}

function highlightText(element, searchTerm) {
 var walker = document.createTreeWalker(
  element,
  NodeFilter.SHOW_TEXT,
  null,
  false
 );

 var textNodes = [];
 var node;
 while (node = walker.nextNode()) {
  if (node.parentElement && node.parentElement.classList &&
      node.parentElement.classList.contains('highlight')) continue;
  if (node.textContent.toLowerCase().indexOf(searchTerm) !== -1) {
   textNodes.push(node);
  }
 }

 for (var i = 0; i < textNodes.length; i++) {
  var tNode = textNodes[i];
  var text = tNode.textContent;
  var lowerText = text.toLowerCase();
  var idx = lowerText.indexOf(searchTerm);
  if (idx === -1) continue;

  var fragment = document.createDocumentFragment();
  var lastIdx = 0;

  while (idx !== -1) {
   fragment.appendChild(document.createTextNode(text.substring(lastIdx, idx)));
   var span = document.createElement('span');
   span.className = 'highlight';
   span.textContent = text.substring(idx, idx + searchTerm.length);
   fragment.appendChild(span);
   lastIdx = idx + searchTerm.length;
   idx = lowerText.indexOf(searchTerm, lastIdx);
  }
  fragment.appendChild(document.createTextNode(text.substring(lastIdx)));
  tNode.parentNode.replaceChild(fragment, tNode);
 }
}

// Back to top button
document.addEventListener('DOMContentLoaded', function() {
 var btn = document.getElementById('backToTop');
 if (btn) {
  window.addEventListener('scroll', function() {
   if (window.scrollY > 400) {
    btn.classList.add('visible');
   } else {
    btn.classList.remove('visible');
   }
  });
  btn.addEventListener('click', function() {
   window.scrollTo({ top: 0, behavior: 'smooth' });
  });
 }

 // Ctrl+F / Cmd+F to focus search
 document.addEventListener('keydown', function(e) {
  if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
   e.preventDefault();
   document.getElementById('repoSearch').focus();
  }
 });
});
</script>

# CDAC Code Catalog

This catalog lists all code repositories from CDAC, auto-synced from GitHub.

<!-- Sticky Search Bar -->
<div class="sticky-search">
 <input type="text" id="repoSearch" class="repo-search"
        placeholder="Search repositories by name, description, language, or topic..."
        onkeyup="searchRepos()">
 <div class="search-stats">
  <span id="searchInfo"></span>
  <span>{{ site.data.repos | size }} repositories total</span>
 </div>
</div>

<!-- Category Navigation -->
<div class="category-nav">
 <h3>Browse by Research Topic</h3>
 <div class="toc-grid">
  <a href="javascript:void(0)" onclick="showAllRepos()" class="toc-link active" id="filter-all">
   All <span class="repo-count">({{ site.data.repos | size }})</span>
  </a>
  {% assign grouped_for_nav = site.data.repos | group_by: "category" | sort: "name" %}
  {% for cat in grouped_for_nav %}
  {% assign first_repo = cat.items | first %}
  <a href="javascript:void(0)" onclick="filterByCategory('{{ first_repo.category_slug }}')" class="toc-link" id="filter-{{ first_repo.category_slug }}">
   {{ cat.name }} <span class="repo-count">({{ cat.size }})</span>
  </a>
  {% endfor %}
 </div>
</div>

{::nomarkdown}
<!-- Repo Cards, grouped by category -->
{% assign sorted_repos = site.data.repos | sort: "sort_order" %}
{% assign grouped = sorted_repos | group_by: "category" %}
{% for cat in grouped %}
{% assign first_repo = cat.items | first %}
<div class="category-section" data-category="{{ first_repo.category_slug }}" id="category-{{ first_repo.category_slug }}">
<div class="section-header">
<h3 style="margin: 0; color: white;">{{ cat.name }} <span class="repo-count">({{ cat.size }})</span></h3>
</div>
{% for repo in cat.items %}
<div class="repo-card" data-category="{{ repo.category_slug }}" data-name="{{ repo.name | downcase }}" data-description="{{ repo.description | downcase | escape }}" data-language="{{ repo.language | downcase }}" data-stars="{{ repo.stars }}" data-updated="{{ repo.updated_at }}">
<div class="repo-card-header">
<h4><a href="{{ repo.url }}" target="_blank" rel="noopener">{{ repo.name }}</a></h4>
{% if repo.language != "" %}{% assign lang_class = repo.language | downcase | replace: " ", "-" %}<span class="language-badge language-{{ lang_class }}">{{ repo.language }}</span>{% endif %}
{% if repo.visibility == "private" %}<span class="private-badge">&#128274; Private</span>{% endif %}
</div>
<p class="repo-description">{{ repo.description }}</p>
<div class="repo-meta">
{% if repo.stars > 0 %}<span class="stat-badge">&#9733; {{ repo.stars }}</span>{% endif %}
{% if repo.forks > 0 %}<span class="stat-badge">&#128276; {{ repo.forks }}</span>{% endif %}
<span class="stat-badge updated">Updated: {{ repo.updated_at }}</span>
</div>
</div>
{% endfor %}
</div>
{% endfor %}

<!-- Back to Top Button -->
<button id="backToTop" class="back-to-top" title="Back to top">&#9650;</button>
{:/nomarkdown}
