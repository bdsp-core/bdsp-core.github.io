#!/usr/bin/env python3
"""
Sync quotes from Google Sheets to Jekyll markdown file.

This script reads quotes from a Google Sheet and generates the quotes.md file.
"""

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Scopes for read-only access
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# Your Google Sheets ID - CDAC_QUOTES spreadsheet
SPREADSHEET_ID = '1HeU0368kUL7J4dIY8Lv-Pknd9UyrmI_rZ6J50aivNKM'

# Sheet name and range
RANGE_NAME = 'Sheet1!A:C'  # Assumes columns: Section, Quote, Attribution

def authenticate_google_sheets():
    """Authenticate using service account and return Google Sheets service."""
    creds = service_account.Credentials.from_service_account_file(
        'service-account-key.json', scopes=SCOPES)
    
    return build('sheets', 'v4', credentials=creds)

def fetch_sheet_data(service):
    """Fetch data from Google Sheets."""
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=RANGE_NAME).execute()
    values = result.get('values', [])
    
    if not values:
        print('No data found.')
        return []
    
    # First row is headers
    headers = values[0]
    data = []
    
    for row in values[1:]:
        # Pad row to match header length
        row_data = row + [''] * (len(headers) - len(row))
        data.append(dict(zip(headers, row_data)))
    
    return data

def escape_markdown(text):
    """Escape special characters for markdown."""
    # Don't escape characters inside quotes
    return text

def generate_quotes_markdown(quotes_data):
    """Generate the quotes.md file content from quotes data."""
    # Group quotes by section
    sections = {}
    for quote in quotes_data:
        section = quote.get('Section', 'Uncategorized')
        if section not in sections:
            sections[section] = []
        sections[section].append(quote)
    
    # Sort sections alphabetically
    sorted_sections = sorted(sections.keys())
    
    # Generate markdown content
    content = []
    content.append("""---
title: "Brandon - quotes"
layout: textlay
excerpt: "Quote collection"
sitemap: false
permalink: /quotes/
---

<style>
/* Enhanced quotes styling */
blockquote {
 padding: 15px 25px;
 margin: 0 0 25px;
 font-size: 16px;
 border-left: 4px solid #3498db;
 background-color: #f8f9fa;
 border-radius: 5px;
 box-shadow: 0 1px 3px rgba(0,0,0,0.1);
 transition: transform 0.2s ease;
}
blockquote:hover {
 transform: translateY(-2px);
 box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}
blockquote strong em {
 color: #7F8C8D;
 font-size: 14px;
}

/* TOC container */
.quotes-toc {
 background: white;
 padding: 20px;
 border: 1px solid #ddd;
 border-radius: 8px;
 margin-bottom: 30px;
 box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* Sticky search container */
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

/* Search box */
.quote-search {
 width: 100%;
 padding: 12px;
 margin-bottom: 20px;
 border: 2px solid #ddd;
 border-radius: 6px;
 font-size: 16px;
 transition: border-color 0.3s ease;
}
.quote-search:focus {
 outline: none;
 border-color: #3498db;
}

/* Section headers */
.section-header {
 background: linear-gradient(135deg, #34495e, #2c3e50);
 color: white;
 padding: 15px 20px;
 margin: 40px 0 25px 0;
 border-radius: 8px;
 box-shadow: 0 2px 4px rgba(0,0,0,0.1);
 position: relative;
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

/* Quote counter */
.quote-count {
 font-size: 12px;
 color: #7f8c8d;
 margin-left: 10px;
 background: #ecf0f1;
 padding: 2px 8px;
 border-radius: 12px;
}

/* TOC styling */
.toc-grid {
 display: grid;
 grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
 gap: 8px;
 margin-bottom: 15px;
}
.toc-link {
 padding: 8px 12px;
 background: #f8f9fa;
 border: 1px solid #e9ecef;
 border-radius: 4px;
 text-decoration: none;
 transition: all 0.2s ease;
 display: block;
}
.toc-link:hover {
 background: #3498db;
 color: white;
 text-decoration: none;
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

/* Search highlighting */
.highlight {
 background-color: #ffeb3b;
 padding: 1px 2px;
 border-radius: 2px;
}

/* Navigation highlight */
blockquote.nav-highlight {
 outline: 3px solid #3498db !important;
 outline-offset: 2px;
}

/* Responsive design */
@media (max-width: 768px) {
 .quotes-toc {
  font-size: 14px;
  padding: 15px;
 }
 .sticky-search {
  padding: 15px;
 }
 .toc-grid {
  grid-template-columns: 1fr;
 }
 blockquote {
  padding: 12px 18px;
  font-size: 15px;
 }
 .back-to-top {
  bottom: 20px;
  right: 20px;
  padding: 10px 14px;
 }
}

/* Loading animation for search */
.searching::after {
 content: '...';
 animation: dots 1.5s steps(5, end) infinite;
}
@keyframes dots {
 0%, 20% { color: rgba(0,0,0,0); text-shadow: .25em 0 0 rgba(0,0,0,0), .5em 0 0 rgba(0,0,0,0); }
 40% { color: black; text-shadow: .25em 0 0 rgba(0,0,0,0), .5em 0 0 rgba(0,0,0,0); }
 60% { text-shadow: .25em 0 0 black, .5em 0 0 rgba(0,0,0,0); }
 80%, 100% { text-shadow: .25em 0 0 black, .5em 0 0 black; }
}
</style>

<script>
// Enhanced search functionality with highlighting
function searchQuotes() {
 const searchTerm = document.getElementById('quoteSearch').value.toLowerCase().trim();
 const allQuotes = document.querySelectorAll('blockquote');
 const sections = document.querySelectorAll('.section-header');
 let totalVisible = 0;
 window.visibleQuotes = [];
 
 // Clear previous highlights and navigation
 document.querySelectorAll('.highlight').forEach(el => {
  el.outerHTML = el.innerHTML;
 });
 document.querySelectorAll('.nav-highlight').forEach(el => {
  el.classList.remove('nav-highlight');
 });
 
 // First, hide/show all quotes based on search
 allQuotes.forEach(quote => {
  const quotText = quote.textContent.toLowerCase();
  const matches = searchTerm === '' || quotText.includes(searchTerm);
  
  if (matches) {
   quote.style.display = 'block';
   window.visibleQuotes.push(quote);
   totalVisible++;
   
   // Highlight search terms
   if (searchTerm !== '') {
    highlightText(quote, searchTerm);
   }
  } else {
   quote.style.display = 'none';
  }
 });
 
 // Then, hide/show section headers based on whether they have visible quotes
 sections.forEach(sectionHeader => {
  let hasVisibleQuotes = false;
  let element = sectionHeader.nextElementSibling;
  
  while (element && !element.classList.contains('section-header')) {
   if (element.tagName === 'BLOCKQUOTE' && element.style.display !== 'none') {
    hasVisibleQuotes = true;
    break;
   }
   element = element.nextElementSibling;
  }
  
  sectionHeader.style.display = hasVisibleQuotes || searchTerm === '' ? 'block' : 'none';
 });
 
 // Update search results info
 updateSearchInfo(searchTerm, totalVisible);
 
 window.currentQuoteIndex = -1;
 console.log('Search complete. Total quotes:', allQuotes.length, 'Visible quotes:', window.visibleQuotes.length);
}

// Navigate through search results
function navigateQuotes(direction) {
 console.log('navigateQuotes called, direction:', direction, 'visibleQuotes:', window.visibleQuotes ? window.visibleQuotes.length : 0);
 
 if (!window.visibleQuotes || window.visibleQuotes.length === 0) {
  console.log('No visible quotes to navigate');
  return;
 }
 
 // Remove previous navigation highlight
 document.querySelectorAll('.nav-highlight').forEach(el => el.classList.remove('nav-highlight'));
 
 // Update index
 console.log('Before update - currentQuoteIndex:', window.currentQuoteIndex);
 if (direction === 'next') {
  window.currentQuoteIndex = (window.currentQuoteIndex + 1) % window.visibleQuotes.length;
 } else {
  window.currentQuoteIndex = window.currentQuoteIndex <= 0 ? window.visibleQuotes.length - 1 : window.currentQuoteIndex - 1;
 }
 
 console.log('After update - currentQuoteIndex:', window.currentQuoteIndex);
 
 // Highlight and scroll to current quote
 const currentQuote = window.visibleQuotes[window.currentQuoteIndex];
 if (currentQuote) {
  currentQuote.classList.add('nav-highlight');
  currentQuote.scrollIntoView({ behavior: 'smooth', block: 'center' });
  console.log('Scrolled to quote:', currentQuote.textContent.substring(0, 50) + '...');
 } else {
  console.error('Quote at index', window.currentQuoteIndex, 'not found');
 }
}

function highlightText(element, searchTerm) {
 const walker = document.createTreeWalker(
  element,
  NodeFilter.SHOW_TEXT,
  null,
  false
 );
 
 const textNodes = [];
 let node;
 while (node = walker.nextNode()) {
  textNodes.push(node);
 }
 
 textNodes.forEach(textNode => {
  const text = textNode.textContent;
  const regex = new RegExp(`(${searchTerm})`, 'gi');
  if (regex.test(text)) {
   const highlightedText = text.replace(regex, '<span class="highlight">$1</span>');
   const span = document.createElement('span');
   span.innerHTML = highlightedText;
   textNode.parentNode.replaceChild(span, textNode);
  }
 });
}

function updateSearchInfo(searchTerm, totalVisible) {
 let infoElement = document.getElementById('searchInfo');
 if (!infoElement) {
  infoElement = document.createElement('div');
  infoElement.id = 'searchInfo';
  infoElement.style.cssText = 'margin-bottom: 15px; padding: 8px 12px; background: #e8f4f8; border-radius: 4px; font-size: 14px;';
  // Insert after the search controls div
  const searchControls = document.querySelector('.sticky-search > div');
  if (searchControls) {
   searchControls.parentNode.insertBefore(infoElement, searchControls.nextSibling);
  } else {
   document.querySelector('.sticky-search').appendChild(infoElement);
  }
 }
 
 if (searchTerm === '') {
  infoElement.style.display = 'none';
 } else {
  infoElement.style.display = 'block';
  infoElement.innerHTML = `Found ${totalVisible} quote${totalVisible !== 1 ? 's' : ''} matching "${searchTerm}"`;
 }
}

// Smooth scrolling for anchor links
function initSmoothScrolling() {
 document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
   e.preventDefault();
   const targetId = this.getAttribute('href').substring(1);
   const target = document.getElementById(targetId);
   if (target) {
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
   }
  });
 });
}

// Back to top button functionality
function initBackToTop() {
 const backToTop = document.createElement('a');
 backToTop.href = '#';
 backToTop.className = 'back-to-top';
 backToTop.innerHTML = '↑';
 backToTop.title = 'Back to top';
 document.body.appendChild(backToTop);
 
 window.addEventListener('scroll', () => {
  if (window.pageYOffset > 300) {
   backToTop.classList.add('visible');
  } else {
   backToTop.classList.remove('visible');
  }
 });
 
 backToTop.addEventListener('click', (e) => {
  e.preventDefault();
  window.scrollTo({ top: 0, behavior: 'smooth' });
 });
}

// Random quote functionality
function showRandomQuote() {
 const quotes = document.querySelectorAll('blockquote');
 const randomQuote = quotes[Math.floor(Math.random() * quotes.length)];
 
 // Clear search and show all quotes first
 document.getElementById('quoteSearch').value = '';
 searchQuotes();
 
 // Scroll to random quote
 randomQuote.scrollIntoView({ behavior: 'smooth', block: 'center' });
 
 // Briefly highlight the quote
 randomQuote.style.border = '3px solid #e74c3c';
 setTimeout(() => {
  randomQuote.style.border = '';
 }, 3000);
}

// Initialize everything when page loads
document.addEventListener('DOMContentLoaded', function() {
 initSmoothScrolling();
 initBackToTop();
 
 // Add keyboard navigation for search input
 const searchInput = document.getElementById('quoteSearch');
 if (!searchInput) {
  console.error('Search input not found!');
  return;
 }
 
 searchInput.addEventListener('keydown', function(e) {
  console.log('Key pressed:', e.key, 'Visible quotes:', window.visibleQuotes ? window.visibleQuotes.length : 0);
  
  if (e.key === 'Enter') {
   e.preventDefault();
   // Jump to first result or continue navigation
   if (window.visibleQuotes && window.visibleQuotes.length > 0) {
    navigateQuotes('next');
   } else {
    console.log('No visible quotes to navigate to');
   }
  } else if (e.key === 'ArrowDown') {
   e.preventDefault();
   navigateQuotes('next');
  } else if (e.key === 'ArrowUp') {
   e.preventDefault();
   navigateQuotes('prev');
  }
 });
 
 // Add keyboard shortcut for search (Ctrl+F or Cmd+F)
 document.addEventListener('keydown', function(e) {
  if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
   e.preventDefault();
   document.getElementById('quoteSearch').focus();
  }
 });
});
</script>

<div class="sticky-search">
<input type="text" id="quoteSearch" class="quote-search" placeholder="🔍 Search quotes... (Ctrl+F)" onkeyup="if(event.key !== 'Enter' && event.key !== 'ArrowDown' && event.key !== 'ArrowUp') searchQuotes()">

<div style="margin-bottom: 15px;">
<button onclick="showRandomQuote()" style="background: #e74c3c; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; margin-right: 10px;">🎲 Random Quote</button>
<span style="font-size: 14px; color: #7f8c8d;">Navigate by category below ↓</span>
</div>
</div>

<div class="quotes-toc">
<h1>Table of Contents</h1>""")
    
    # Generate table of contents with grid layout and quote counts
    content.append('{::nomarkdown}')
    content.append('<div class="toc-grid">')
    for section in sorted_sections:
        # Create anchor-friendly section ID
        section_id = section.lower().replace(' ', '-').replace('/', '-').replace('\'', '')
        quote_count = len(sections[section])
        content.append(f'<a href="#{section_id}" class="toc-link">{section} <span class="quote-count">({quote_count})</span></a>')
    content.append('</div>')
    content.append('{:/nomarkdown}')
    content.append('</div>')
    
    content.append("\n[Back to Brandon's page](/brandon/)")
    
    # Generate sections with quotes
    for section in sorted_sections:
        # Create anchor-friendly section ID
        section_id = section.lower().replace(' ', '-').replace('/', '-').replace('\'', '')
        quote_count = len(sections[section])
        
        content.append(f'\n<div class="section-header" id="{section_id}">')
        content.append(f'<h3 style="margin: 0; color: white;">{section} <span class="quote-count">({quote_count} quotes)</span></h3>')
        content.append('</div>')
        
        for quote in sections[section]:
            quote_text = quote.get('Quote', '').strip()
            attribution = quote.get('Attribution', '').strip()
            
            if quote_text:
                # Format the quote
                content.append(f"> {quote_text}  ")
                if attribution:
                    content.append(f"> **--_{attribution}_**")
                content.append("")  # Empty line between quotes
        
        content.append("[Back to Top](# )\n")
        content.append("\n[Back to Brandon's page](/brandon/)")
    
    return '\n'.join(content)

def save_quotes_file(content):
    """Save the generated content to quotes.md."""
    output_path = '_pages/quotes.md'
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Saved quotes to {output_path}")

def main():
    """Main function to sync quotes from Google Sheets."""
    # Check if service account key exists
    if not os.path.exists('service-account-key.json'):
        print("Error: service-account-key.json not found!")
        print("Please ensure you're using the same service account as for team sync.")
        return
    
    print("Authenticating with Google Sheets...")
    service = authenticate_google_sheets()
    
    print("Fetching quotes from Google Sheets...")
    quotes_data = fetch_sheet_data(service)
    
    if not quotes_data:
        print("No quotes to process.")
        return
    
    print(f"Found {len(quotes_data)} quotes")
    
    # Generate markdown content
    markdown_content = generate_quotes_markdown(quotes_data)
    
    # Save to file
    save_quotes_file(markdown_content)
    
    print("Quotes sync complete!")

if __name__ == '__main__':
    main()