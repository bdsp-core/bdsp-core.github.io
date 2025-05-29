#!/usr/bin/env python3
"""Extract news data from YAML to CSV for Google Sheets import."""

import csv
import re

def parse_yaml_simple(filename):
    """Simple YAML parser for news structure."""
    news_items = []
    current_item = {}
    
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.rstrip()
        
        # New item starts with "- date:"
        if line.startswith('- date:'):
            if current_item:
                news_items.append(current_item)
            current_item = {}
            # Extract date value
            date_value = line[7:].strip()
            current_item['date'] = date_value
        
        # Headline line
        elif line.strip().startswith('headline:'):
            # Extract headline, removing quotes if present
            headline = line.strip()[9:].strip()
            if headline.startswith('"') and headline.endswith('"'):
                headline = headline[1:-1]
            current_item['headline'] = headline
    
    # Don't forget the last item
    if current_item:
        news_items.append(current_item)
    
    return news_items

def main():
    """Extract news data to CSV."""
    news_items = parse_yaml_simple('_data/news.yml')
    
    # Write to CSV
    with open('news_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Date', 'Headline']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for item in news_items:
            writer.writerow({
                'Date': item.get('date', ''),
                'Headline': item.get('headline', '')
            })
    
    print(f"Extracted {len(news_items)} news items to news_data.csv")
    print("\nYou can now copy the contents of news_data.csv to your Google Sheet!")

if __name__ == '__main__':
    main()