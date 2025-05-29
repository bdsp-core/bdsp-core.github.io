#!/usr/bin/env python3
"""
Sync team member data from Google Sheets to Jekyll YAML files.

Requirements:
- pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client PyYAML

Setup:
1. Enable Google Sheets API in Google Cloud Console
2. Create credentials and download as 'credentials.json'
3. Update SPREADSHEET_ID with your Google Sheets ID
4. Run the script - it will authenticate on first run
"""

import os
import yaml
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# Your Google Sheets ID (from the URL)
# Get this from your sheet URL: https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
SPREADSHEET_ID = '1ph4QHAwB4HUMM7QCcz00kUlNTUZtnQSVFrtvD14k_HQ'

# Sheet name and range
RANGE_NAME = 'Team!A:H'  # Adjust based on your sheet structure

def authenticate_google_sheets():
    """Authenticate and return Google Sheets service."""
    creds = None
    
    # Token file stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            # Use a fixed port to match the redirect URI in Google Cloud Console
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
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

def format_team_member(row):
    """Format a row from sheets into YAML structure."""
    member = {}
    
    # Handle name with optional link
    if row.get('Link'):
        member['name'] = f'<a href="{row["Link"]}">{row["Name"]}<a/>'
    else:
        member['name'] = row['Name']
    
    # Add other fields
    if row.get('Photo'):
        member['photo'] = row['Photo']
    if row.get('Position'):
        member['info'] = row['Position']
    if row.get('Email'):
        member['email'] = row['Email']
    
    # Handle education fields
    education_fields = []
    for i in range(1, 5):  # Support up to 4 education entries
        if row.get(f'Education{i}'):
            education_fields.append(row[f'Education{i}'])
    
    if education_fields:
        member['number_educ'] = len(education_fields)
        for i, edu in enumerate(education_fields, 1):
            member[f'education{i}'] = edu
    
    return member

def categorize_data(data):
    """Categorize team members based on their category field."""
    categories = {
        'faculty': [],
        'postdocsStudentsStaff': [],
        'alumni': [],
        'collaborators': []
    }
    
    for row in data:
        category = row.get('Category', '').lower()
        
        # Map variations to standard categories
        if 'faculty' in category:
            categories['faculty'].append(format_team_member(row))
        elif any(x in category for x in ['postdoc', 'student', 'staff']):
            categories['postdocsStudentsStaff'].append(format_team_member(row))
        elif 'alumni' in category:
            categories['alumni'].append(format_team_member(row))
        elif 'collaborator' in category:
            categories['collaborators'].append(format_team_member(row))
    
    return categories

def save_yaml_files(categories):
    """Save categorized data to YAML files."""
    data_dir = '_data'
    
    # Ensure data directory exists
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Save each category
    for category, members in categories.items():
        if members:  # Only save if there are members
            filename = os.path.join(data_dir, f'{category}.yml')
            
            with open(filename, 'w') as f:
                yaml.dump(members, f, default_flow_style=False, 
                         allow_unicode=True, sort_keys=False)
            
            print(f"Saved {len(members)} members to {filename}")

def main():
    """Main function to sync Google Sheets to YAML."""
    print("Authenticating with Google Sheets...")
    service = authenticate_google_sheets()
    
    print("Fetching data from Google Sheets...")
    data = fetch_sheet_data(service)
    
    if not data:
        print("No data to process.")
        return
    
    print(f"Found {len(data)} team members")
    
    # Categorize the data
    categories = categorize_data(data)
    
    # Save to YAML files
    save_yaml_files(categories)
    
    print("Sync complete!")

if __name__ == '__main__':
    main()