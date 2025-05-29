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

# Your Google Sheets ID (update this with your quotes sheet ID)
SPREADSHEET_ID = 'YOUR_QUOTES_SPREADSHEET_ID_HERE'

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
/* this is kind of a hack */
blockquote {
 padding: 5px 20px;
 margin: 0 0 20px;
font-size: 16px;
 border-left: 5px solid #eee;
}
blockquote strong em {
 color: #7F8C8D;
}
</style>

# Table of Contents""")
    
    # Generate table of contents
    toc_items = []
    for section in sorted_sections:
        # Create anchor-friendly section ID
        section_id = section.lower().replace(' ', '-').replace('/', '-').replace('\'', '')
        toc_items.append(f"[{section} | ](#{section_id})")
    
    content.append(' | '.join(toc_items[:5]))  # First row
    for i in range(5, len(toc_items), 5):
        content.append(' | '.join(toc_items[i:i+5]))
    
    content.append("\n[Back to Brandon's page](/brandon/)")
    
    # Generate sections with quotes
    for section in sorted_sections:
        # Create anchor-friendly section ID
        section_id = section.lower().replace(' ', '-').replace('/', '-').replace('\'', '')
        
        content.append(f"\n### {section}")
        
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