#!/usr/bin/env python3
"""Extract team data from YAML files to CSV - simple version without dependencies."""

import re
import csv

def parse_yaml_simple(filename):
    """Simple YAML parser for the specific structure we have."""
    members = []
    current_member = {}
    
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.rstrip()
            
            # New member starts with "- name:"
            if line.startswith('- name:'):
                if current_member:
                    members.append(current_member)
                current_member = {}
                # Extract name value
                name_value = line[7:].strip()
                current_member['name'] = name_value
            
            # Other fields
            elif line.startswith('  '):
                if ':' in line:
                    key, value = line.strip().split(':', 1)
                    current_member[key.strip()] = value.strip()
        
        # Don't forget the last member
        if current_member:
            members.append(current_member)
            
    except FileNotFoundError:
        print(f"Warning: {filename} not found")
        
    return members

def extract_link_and_name(name_field):
    """Extract URL and clean name from HTML link if present."""
    # Check if it's an HTML link
    match = re.match(r'<a href="([^"]+)">([^<]+)</?a?/?>', name_field)
    if match:
        return match.group(2).strip(), match.group(1).strip()
    return name_field.strip(), ""

def main():
    """Extract all team data to CSV."""
    all_rows = []
    
    # Process each category
    categories = [
        ('_data/faculty.yml', 'Faculty'),
        ('_data/postdocsStudentsStaff.yml', 'Postdocs, Students, Staff'),
        ('_data/alumni.yml', 'Alumni'),
        ('_data/collaborators.yml', 'Collaborators')
    ]
    
    for yaml_file, category in categories:
        members = parse_yaml_simple(yaml_file)
        
        for member in members:
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
            all_rows.append(row)
        
        print(f"Extracted {len(members)} members from {yaml_file}")
    
    # Write to CSV
    fieldnames = ['Name', 'Link', 'Photo', 'Position', 'Email', 
                  'Education1', 'Education2', 'Education3', 'Education4', 'Category']
    
    with open('team_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
    
    print(f"\nTotal: {len(all_rows)} team members exported to team_data.csv")
    print("\nYou can now copy the contents of team_data.csv to your Google Sheet!")

if __name__ == '__main__':
    main()