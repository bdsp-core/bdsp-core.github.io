"""One-shot: create a Google Sheet per Sheet-backed section.

What it does:
  1. Authenticates (service account if GOOGLE_APPLICATION_CREDENTIALS is set,
     else OAuth installed-app flow).
  2. Creates (or reuses) a Drive folder "CV Sheets".
  3. For each section in sheets_schema.SHEET_SCHEMAS:
       - Creates a Sheet named "CV - <key>".
       - Writes the column header row.
       - For tab-separated sections, parses cache/sections/<key>.txt and seeds
         the data rows. Multi-line entries (grants, etc.) are parsed best-effort.
       - Records sheet_id in config.yaml under sections.<key>.
  4. For each section, sets per.source = "sheet" so build.py reads it from
     the Sheet next time.

Idempotent: skips sections that already have a sheet_id. --force <key> to
recreate a single section's Sheet.
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from gauth import get_credentials, drive_client, sheets_client, whoami
from sheets_schema import SHEET_SCHEMAS

FOLDER_NAME = "CV Sheets"


# ----- parsers: text file -> list of row-dicts -----

def parse_tab_separated(path, columns):
    """Each non-blank line is one row; columns are tab-separated."""
    if not path.exists():
        return []
    rows = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        # Pad to column count
        parts = parts + [""] * max(0, len(columns) - len(parts))
        row = dict(zip(columns, parts[: len(columns)]))
        rows.append(row)
    return rows


def parse_grants(path, columns):
    """Grants are 3 lines per entry separated by blanks.

    Line 1: "MM/YYYY – MM/YYYY \tFunder: ..."
    Line 2: "Title: ..."
    Line 3: "Role: ..."
    """
    if not path.exists():
        return []
    rows = []
    current = {"Dates": "", "Funder": "", "Title": "", "Role": ""}
    for line in path.read_text().splitlines():
        s = line.strip()
        if not s:
            if any(current.values()):
                rows.append(current)
                current = {"Dates": "", "Funder": "", "Title": "", "Role": ""}
            continue
        if "\tFunder:" in line or line.lower().startswith(("01/", "02/", "03/", "04/", "05/", "06/", "07/", "08/", "09/", "10/", "11/", "12/")):
            # Date + Funder: line
            m = re.match(r"^(.*?)\tFunder:\s*(.*)$", line)
            if m:
                current["Dates"] = m.group(1).strip()
                current["Funder"] = m.group(2).strip()
            else:
                current["Dates"] = line.strip()
        elif s.lower().startswith("title:"):
            current["Title"] = s.split(":", 1)[1].strip()
        elif s.lower().startswith("role:"):
            current["Role"] = s.split(":", 1)[1].strip()
    if any(current.values()):
        rows.append(current)
    return rows


def parse_section(key, schema):
    """Pick the right parser for each section.

    Only auto-populates sections whose text is genuinely tab-structured (or
    structured as grant blocks). For sections like invited talks and trainees
    whose existing text is free-form prose, we leave the Sheet empty so the
    user can fill in columns properly — tab-splitting prose would put
    everything in the first column.
    """
    path = ROOT / "cache" / "sections" / f"{key}.txt"
    if key.startswith("grants_"):
        return parse_grants(path, schema["columns"])
    if key.startswith("invited_") or key.startswith("trainees_"):
        return []  # leave empty — user fills in over time
    return parse_tab_separated(path, schema["columns"])


# ----- Drive / Sheets API helpers -----

def ensure_folder(drive, existing_id):
    if existing_id:
        try:
            f = drive.files().get(fileId=existing_id, fields="id,name,trashed").execute()
            if not f.get("trashed"):
                return existing_id
        except Exception:
            pass
    body = {"name": FOLDER_NAME, "mimeType": "application/vnd.google-apps.folder"}
    f = drive.files().create(body=body, fields="id").execute()
    return f["id"]


def share_with_user(drive, file_id, user_email):
    """If we're a service account, share the file with the human user too."""
    if not user_email:
        return
    drive.permissions().create(
        fileId=file_id,
        body={"type": "user", "role": "writer", "emailAddress": user_email},
        sendNotificationEmail=False,
    ).execute()


def create_sheet(drive, sheets, folder_id, title, columns, rows, share_email=None):
    body = {
        "name": title,
        "mimeType": "application/vnd.google-apps.spreadsheet",
        "parents": [folder_id],
    }
    f = drive.files().create(body=body, fields="id").execute()
    sheet_id = f["id"]
    if share_email:
        share_with_user(drive, sheet_id, share_email)

    values = [columns]
    for row in rows:
        values.append([row.get(c, "") for c in columns])
    sheets.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range="A1",
        valueInputOption="RAW",
        body={"values": values},
    ).execute()
    # Bold the header row
    sheets.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body={
            "requests": [
                {
                    "repeatCell": {
                        "range": {"sheetId": 0, "startRowIndex": 0, "endRowIndex": 1},
                        "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
                        "fields": "userEnteredFormat.textFormat.bold",
                    }
                },
                {
                    "updateSheetProperties": {
                        "properties": {"sheetId": 0, "gridProperties": {"frozenRowCount": 1}},
                        "fields": "gridProperties.frozenRowCount",
                    }
                },
            ]
        },
    ).execute()
    return sheet_id


# ----- config helpers -----

def load_config():
    return yaml.safe_load((ROOT / "config.yaml").read_text())


def save_config(cfg):
    (ROOT / "config.yaml").write_text(
        yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True, width=200)
    )


# ----- entry point -----

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="append", default=[],
                        help="Section keys to recreate (deletes existing sheet).")
    parser.add_argument("--share-with", default=None,
                        help="Email to share each created sheet with (use when "
                             "authenticating as a service account, so you can "
                             "still see/edit the sheets).")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    cfg = load_config()
    creds = get_credentials(ROOT / cfg["google"]["credentials"], ROOT / cfg["google"]["token"])
    print(f"Authenticated as: {whoami(creds)}")

    drive = drive_client(creds)
    sheets = sheets_client(creds)

    if cfg.get("sections") is None:
        cfg["sections"] = {}

    if not args.dry_run:
        folder_id = ensure_folder(drive, cfg["google"].get("sheets_folder_id") or "")
        cfg["google"]["sheets_folder_id"] = folder_id
        if args.share_with:
            share_with_user(drive, folder_id, args.share_with)
        print(f"Sheets folder: https://drive.google.com/drive/folders/{folder_id}")
    else:
        folder_id = "(dry-run)"

    for key, schema in SHEET_SCHEMAS.items():
        existing = cfg["sections"].get(key) or {}
        if existing.get("sheet_id") and key not in args.force:
            print(f"  skip   {key}  (already has sheet_id={existing['sheet_id'][:10]}...)")
            continue
        rows = parse_section(key, schema)
        if args.dry_run:
            print(f"  CREATE {key}  ({len(rows)} rows parsed from text)")
            continue
        if existing.get("sheet_id") and key in args.force:
            try:
                drive.files().delete(fileId=existing["sheet_id"]).execute()
            except Exception as e:
                print(f"  warn: couldn't delete old sheet for {key}: {e}")
        sheet_id = create_sheet(drive, sheets, folder_id, f"CV - {key}",
                                schema["columns"], rows, share_email=args.share_with)
        cfg["sections"][key] = {"sheet_id": sheet_id, "source": "sheet"}
        print(f"  created {key}  ({len(rows)} rows)  sheet_id={sheet_id}")

    if not args.dry_run:
        save_config(cfg)
        print("Saved config.yaml")


if __name__ == "__main__":
    main()
