# Google Sheets Team Sync Setup Guide

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
```bash
cd "/Users/bwestove/cdac Dropbox/brandon westover/0_GithubRepos/bdsp-core.github.io"
source venv/bin/activate
python sync_team_service_account.py
```

## Google Sheet Format
Your sheet should have these columns:
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

## Automation with GitHub Actions
Once the manual sync works, the GitHub Action will use the same service account to sync automatically.