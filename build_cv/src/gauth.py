"""Unified Google auth — picks the right path depending on environment.

Order of preference:
  1. GOOGLE_APPLICATION_CREDENTIALS env var → service account JSON path
     (cleanest for GitHub Actions / cron — unattended, no browser).
  2. Local OAuth installed-app flow via credentials.json + token.json
     (used during local dev; opens a browser the first time).

Same SCOPES for both. The service account email is reported by `whoami()` so
you know what address to share the Sheets/Docs with.
"""

import json
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets",
]


def get_credentials(creds_path=None, token_path=None):
    """Return Google credentials, preferring service account when configured."""
    sa_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if sa_path and Path(sa_path).exists():
        return ServiceAccountCredentials.from_service_account_file(sa_path, scopes=SCOPES)

    if not creds_path or not token_path:
        raise FileNotFoundError(
            "No service account configured (GOOGLE_APPLICATION_CREDENTIALS) "
            "and no OAuth creds/token paths given."
        )

    creds_path = Path(creds_path)
    token_path = Path(token_path)
    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not creds_path.exists():
                raise FileNotFoundError(f"OAuth client JSON not found at {creds_path}.")
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json())
    return creds


def whoami(creds):
    """Return the email of the authenticated principal (service account or user)."""
    if hasattr(creds, "service_account_email"):
        return creds.service_account_email
    return "(OAuth user — check token.json for the active account)"


def docs_client(creds):
    return build("docs", "v1", credentials=creds, cache_discovery=False)


def drive_client(creds):
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def sheets_client(creds):
    return build("sheets", "v4", credentials=creds, cache_discovery=False)
