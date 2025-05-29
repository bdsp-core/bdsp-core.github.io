#!/usr/bin/env python3
"""
Sync news/publications from Google Sheets to Jekyll YAML file.

This script reads news items from a Google Sheet and updates the news.yml file.
"""

import os
import yaml
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

# Scopes for read-only access
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# Your Google Sheets ID (update this with your news sheet ID)
SPREADSHEET_ID = '1i2cyibZBERRqQ5DR76qdHZK3c-FMUsfNwIQjY9HWZJk'

# Sheet name and range
RANGE_NAME = 'Sheet1!A:B'  # Assumes columns: Date, Headline

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

def parse_date(date_str):
    """Parse various date formats and return standardized format."""
    # Try different date formats
    date_formats = [
        '%Y-%m-%d',      # 2024-11-21
        '%m/%d/%Y',      # 11/21/2024
        '%d/%m/%Y',      # 21/11/2024
        '%B %d, %Y',     # November 21, 2024
        '%b %d, %Y',     # Nov 21, 2024
        '%d %b %Y',      # 21 Nov 2024
        '%d %B %Y',      # 21 November 2024
        '%d-%b-%y',      # 21-Nov-24
        '%d-%B-%y',      # 21-November-24
    ]
    
    for fmt in date_formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            # Return in the format used by the site: "21 Nov 2024"
            return dt.strftime('%-d %b %Y')
        except ValueError:
            continue
    
    # If no format matches, return the original string
    print(f"Warning: Could not parse date '{date_str}', using as-is")
    return date_str.strip()

def format_news_item(row):
    """Format a row from sheets into news YAML structure."""
    item = {}
    
    # Parse and format date
    if row.get('Date'):
        item['date'] = parse_date(row['Date'])
    
    # Add headline (supports markdown links)
    if row.get('Headline'):
        item['headline'] = row['Headline'].strip()
    
    return item

def save_news_yaml(news_items):
    """Save news items to YAML file."""
    output_path = '_data/news.yml'
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Sort by date (newest first)
    # Convert dates to datetime for sorting
    def sort_key(item):
        try:
            return datetime.strptime(item['date'], '%-d %b %Y')
        except:
            try:
                return datetime.strptime(item['date'], '%d %b %Y')
            except:
                return datetime.min
    
    sorted_items = sorted(news_items, key=sort_key, reverse=True)
    
    # Write to YAML with proper formatting
    with open(output_path, 'w', encoding='utf-8') as f:
        # Write each item manually to control formatting
        for i, item in enumerate(sorted_items):
            if i > 0:
                f.write('\n')
            f.write(f"- date: {item['date']}\n")
            f.write(f'  headline: "{item["headline"]}"\n')
    
    print(f"Saved {len(sorted_items)} news items to {output_path}")

def main():
    """Main function to sync news from Google Sheets."""
    # Check if service account key exists
    if not os.path.exists('service-account-key.json'):
        print("Error: service-account-key.json not found!")
        print("Please ensure you're using the same service account as for team/quotes sync.")
        return
    
    print("Authenticating with Google Sheets...")
    service = authenticate_google_sheets()
    
    print("Fetching news from Google Sheets...")
    news_data = fetch_sheet_data(service)
    
    if not news_data:
        print("No news items to process.")
        return
    
    print(f"Found {len(news_data)} news items")
    
    # Format news items
    news_items = []
    for row in news_data:
        if row.get('Date') and row.get('Headline'):  # Only include complete entries
            item = format_news_item(row)
            if item:
                news_items.append(item)
    
    # Save to YAML file
    save_news_yaml(news_items)
    
    print("News sync complete!")

if __name__ == '__main__':
    main()