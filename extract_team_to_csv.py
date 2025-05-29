#!/usr/bin/env python3
"""Extract team data from YAML files to CSV for Google Sheets import."""

import yaml
import csv
import re

def extract_link_and_name(name_field):
    """Extract URL and clean name from HTML link if present."""
    # Check if it's an HTML link
    match = re.match(r'<a href="([^"]+)">([^<]+)</?a?/?>', name_field)
    if match:
        return match.group(2).strip(), match.group(1).strip()
    return name_field.strip(), ""

def yaml_to_rows(yaml_file, category):
    """Convert YAML data to rows for CSV."""
    rows = []
    
    try:
        with open(f'_data/{yaml_file}', 'r') as f:
            data = yaml.safe_load(f)
            
        if not data:
            return rows
            
        for member in data:
            # Extract name and link
            name, link = extract_link_and_name(member.get('name', ''))
            
            # Build row
            row = {
                'Name': name,
                'Link': link,
                'Photo': member.get('photo', ''),
                'Position': member.get('info', ''),
                'Email': member.get('email', ''),
                'Education1': member.get('education1', ''),
                'Education2': member.get('education2', ''),
                'Education3': member.get('education3', ''),
                'Education4': member.get('education4', ''),
                'Category': category
            }
            rows.append(row)
            
    except FileNotFoundError:
        print(f"Warning: {yaml_file} not found")
        
    return rows

def main():
    """Extract all team data to CSV."""
    all_rows = []
    
    # Process each category
    categories = [
        ('faculty.yml', 'Faculty'),
        ('postdocsStudentsStaff.yml', 'Postdocs, Students, Staff'),
        ('alumni.yml', 'Alumni'),
        ('collaborators.yml', 'Collaborators')
    ]
    
    for yaml_file, category in categories:
        rows = yaml_to_rows(yaml_file, category)
        all_rows.extend(rows)
        print(f"Extracted {len(rows)} members from {yaml_file}")
    
    # Write to CSV
    fieldnames = ['Name', 'Link', 'Photo', 'Position', 'Email', 
                  'Education1', 'Education2', 'Education3', 'Education4', 'Category']
    
    with open('team_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
    
    print(f"\nTotal: {len(all_rows)} team members exported to team_data.csv")

if __name__ == '__main__':
    main()