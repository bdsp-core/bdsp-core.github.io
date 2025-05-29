# Google Sheets Data Sync Setup Guide

## Using Service Account (Recommended)

### Step 1: Create Service Account
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **IAM & Admin** → **Service Accounts**
3. Click **+ CREATE SERVICE ACCOUNT**
4. Name it something like "sheets-sync"
5. Click **Create and Continue** (skip optional steps)
6. Click **Done**

### Step 2: Create and Download Key
1. Click on your new service account
2. Go to **Keys** tab
3. Click **ADD KEY** → **Create new key**
4. Choose **JSON** format
5. Download the file and rename it to `service-account-key.json`
6. Place it in your repository root (it's already in .gitignore)

### Step 3: Get Service Account Email
1. Copy the service account email (looks like: `sheets-sync@your-project.iam.gserviceaccount.com`)

### Step 4: Share Google Sheet
1. Open your Google Sheet
2. Click **Share** button
3. Paste the service account email
4. Give it **Viewer** access
5. Click **Send**

### Step 5: Run the Sync

For team data:
```bash
cd "/Users/bwestove/cdac Dropbox/brandon westover/0_GithubRepos/bdsp-core.github.io"
source venv/bin/activate
python sync_team_service_account.py
```

For quotes:
```bash
# First, update the SPREADSHEET_ID in sync_quotes_from_sheets.py
python sync_quotes_from_sheets.py
```

## Google Sheet Formats

### Team Sheet Format
Your team sheet should have these columns:
- Name
- Link (optional URL)
- Photo (filename)
- Position
- Email
- Education1
- Education2
- Education3
- Education4
- Category (must be one of: Faculty, Alumni, Postdocs/Students/Staff, Collaborators)

### Quotes Sheet Format
Your quotes sheet should have these columns:
- Section (e.g., "Absurdity", "Academics", "Science", etc.)
- Quote (the actual quote text)
- Attribution (author name and any additional info)

## Automation with GitHub Actions

The GitHub Action will sync both team data and quotes automatically. You need to set these secrets in your repository:

1. **SERVICE_ACCOUNT_KEY**: The contents of your service-account-key.json file
2. **TEAM_SPREADSHEET_ID**: The ID of your team Google Sheet (optional, uses hardcoded ID if not set)
3. **QUOTES_SPREADSHEET_ID**: The ID of your quotes Google Sheet (optional, skips quotes sync if not set)

To set secrets:
1. Go to your repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add each secret with the appropriate value

The workflow runs daily at 2 AM UTC or can be manually triggered from the Actions tab.