"""Bootstrap CV Sheets + Docs in YOUR Drive using only the Drive API (no Docs/
Sheets API needed for creation), authenticated as your gcloud user.

Why this exists: service accounts on personal Gmail can't own Drive files
("storageQuotaExceeded"). And gcloud's default ADC client no longer permits
Sheets/Docs scopes for personal projects. But Drive scope is fine, and Drive
API can create a Sheet by uploading a CSV (auto-converts) or a Doc by
uploading text/html. The resulting files are owned by YOU. We then share each
one with the service account so the cron job can read them.

After this runs:
  - "CV - <section>" Sheets / Docs live in your Drive, in folder "CV Sources"
  - Each file is shared with the service account as Editor
  - config.yaml has every Sheet ID / Doc ID

Run once. Re-run with --force to overwrite a section's file.
"""

import argparse
import csv
import io
import json
import subprocess
import sys
import time
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from sections import SECTIONS
from sheets_schema import SHEET_SCHEMAS

FOLDER_NAME = "CV Sources"
DRIVE_API = "https://www.googleapis.com/drive/v3"
DRIVE_UPLOAD = "https://www.googleapis.com/upload/drive/v3/files"


def get_user_token():
    """Mint a short-lived Drive-scoped access token from gcloud."""
    r = subprocess.run(
        ["gcloud", "auth", "print-access-token",
         "--scopes=https://www.googleapis.com/auth/drive"],
        capture_output=True, text=True, check=True,
    )
    return r.stdout.strip()


def get_sa_email():
    """Read the service account email from .secrets/sa.json (if present)."""
    sa_path = ROOT / ".secrets" / "sa.json"
    if sa_path.exists():
        return json.loads(sa_path.read_text())["client_email"]
    return None


# ----- Drive REST helpers -----

def drive_get(token, path, **params):
    r = requests.get(f"{DRIVE_API}{path}", params=params,
                     headers={"Authorization": f"Bearer {token}"}, timeout=30)
    r.raise_for_status()
    return r.json()


def drive_post(token, path, body):
    r = requests.post(f"{DRIVE_API}{path}",
                      headers={"Authorization": f"Bearer {token}",
                               "Content-Type": "application/json"},
                      data=json.dumps(body), timeout=30)
    r.raise_for_status()
    return r.json()


def drive_delete(token, file_id):
    r = requests.delete(f"{DRIVE_API}/files/{file_id}",
                        headers={"Authorization": f"Bearer {token}"}, timeout=30)
    if r.status_code not in (204, 404):
        r.raise_for_status()


def drive_upload(token, metadata, content_bytes, content_type):
    """Multipart upload: returns the new file id."""
    boundary = "-------cv-build-boundary-9b3d0f"
    body = (
        f"--{boundary}\r\n"
        "Content-Type: application/json; charset=UTF-8\r\n\r\n"
        f"{json.dumps(metadata)}\r\n"
        f"--{boundary}\r\n"
        f"Content-Type: {content_type}\r\n\r\n"
    ).encode("utf-8") + content_bytes + f"\r\n--{boundary}--".encode("utf-8")

    r = requests.post(
        DRIVE_UPLOAD,
        params={"uploadType": "multipart", "fields": "id"},
        headers={"Authorization": f"Bearer {token}",
                 "Content-Type": f"multipart/related; boundary={boundary}"},
        data=body, timeout=60,
    )
    r.raise_for_status()
    return r.json()["id"]


def ensure_folder(token, existing_id):
    if existing_id:
        try:
            f = drive_get(token, f"/files/{existing_id}", fields="id,name,trashed")
            if not f.get("trashed"):
                return existing_id
        except requests.HTTPError:
            pass
    f = drive_post(token, "/files", {"name": FOLDER_NAME,
                                      "mimeType": "application/vnd.google-apps.folder"})
    return f["id"]


def share_with(token, file_id, email, role="writer"):
    drive_post(
        token, f"/files/{file_id}/permissions?sendNotificationEmail=false",
        {"type": "user", "role": role, "emailAddress": email},
    )


# ----- file creation -----

def create_sheet(token, folder_id, title, columns, rows, sa_email):
    """Create a Google Sheet by uploading a CSV (auto-converted on upload)."""
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(columns)
    for row in rows:
        w.writerow([row.get(c, "") for c in columns])
    csv_bytes = buf.getvalue().encode("utf-8")

    metadata = {
        "name": title,
        "mimeType": "application/vnd.google-apps.spreadsheet",
        "parents": [folder_id],
    }
    file_id = drive_upload(token, metadata, csv_bytes, "text/csv")
    if sa_email:
        share_with(token, file_id, sa_email)
    return file_id


def create_doc(token, folder_id, title, text, sa_email):
    """Create a Google Doc by uploading text/plain (auto-converted on upload)."""
    metadata = {
        "name": title,
        "mimeType": "application/vnd.google-apps.document",
        "parents": [folder_id],
    }
    file_id = drive_upload(token, metadata, text.encode("utf-8"), "text/plain")
    if sa_email:
        share_with(token, file_id, sa_email)
    return file_id


# ----- parsers for seeding -----

def _parse_tab(path, columns):
    if not path.exists():
        return []
    rows = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        parts += [""] * max(0, len(columns) - len(parts))
        rows.append(dict(zip(columns, parts[: len(columns)])))
    return rows


def _parse_grants(path, columns):
    import re
    if not path.exists():
        return []
    rows = []
    current = {c: "" for c in columns}
    for line in path.read_text().splitlines():
        s = line.strip()
        if not s:
            if any(current.values()):
                rows.append(current)
                current = {c: "" for c in columns}
            continue
        if "\tFunder:" in line:
            m = re.match(r"^(.*?)\tFunder:\s*(.*)$", line)
            if m:
                current["Dates"] = m.group(1).strip()
                current["Funder"] = m.group(2).strip()
        elif s.lower().startswith("title:"):
            current["Title"] = s.split(":", 1)[1].strip()
        elif s.lower().startswith("role:"):
            current["Role"] = s.split(":", 1)[1].strip()
    if any(current.values()):
        rows.append(current)
    return rows


def parse_section_rows(key, schema):
    """Return list of row-dicts to pre-populate the Sheet with.

    Sections whose existing text is tab-structured (or grants-block-structured)
    are seeded; free-form ones (invited talks, trainees) start empty.
    """
    path = ROOT / "cache" / "sections" / f"{key}.txt"
    if key.startswith("grants_"):
        return _parse_grants(path, schema["columns"])
    if key.startswith("invited_") or key.startswith("trainees_"):
        return []
    return _parse_tab(path, schema["columns"])


# ----- config -----

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
                        help="Section keys to recreate (overwrites existing).")
    parser.add_argument("--only", action="append", default=[],
                        help="Only process these section keys.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    token = get_user_token()
    sa_email = get_sa_email()
    if not sa_email:
        print("WARN: .secrets/sa.json not found; created files will not be shared with the SA.")

    cfg = load_config()
    if cfg.get("sections") is None:
        cfg["sections"] = {}

    if not args.dry_run:
        folder_id = ensure_folder(token, cfg["google"].get("drive_folder_id") or "")
        cfg["google"]["drive_folder_id"] = folder_id
        if sa_email:
            try:
                share_with(token, folder_id, sa_email)
            except requests.HTTPError:
                pass  # already shared
        print(f"Drive folder: https://drive.google.com/drive/folders/{folder_id}")
        if sa_email:
            print(f"Service account: {sa_email}")
    else:
        folder_id = "(dry-run)"

    # --- Sheets ---
    for key, schema in SHEET_SCHEMAS.items():
        if args.only and key not in args.only:
            continue
        existing = cfg["sections"].get(key) or {}
        if existing.get("sheet_id") and key not in args.force:
            print(f"  skip sheet  {key}  (already has sheet_id={existing['sheet_id'][:10]}...)")
            continue
        rows = parse_section_rows(key, schema)
        if args.dry_run:
            print(f"  CREATE sheet {key}  ({len(rows)} rows)")
            continue
        if existing.get("sheet_id") and key in args.force:
            try:
                drive_delete(token, existing["sheet_id"])
            except Exception as e:
                print(f"  warn: couldn't delete old sheet for {key}: {e}")
        sheet_id = create_sheet(token, folder_id, f"CV - {key}",
                                schema["columns"], rows, sa_email)
        cfg["sections"][key] = {"sheet_id": sheet_id, "source": "sheet"}
        print(f"  created sheet {key}  ({len(rows)} rows)  sheet_id={sheet_id}")
        time.sleep(0.2)  # polite

    # --- Docs (for sections not in SHEET_SCHEMAS) ---
    sections_dir = ROOT / "cache" / "sections"
    for key, prefix, _h, _s, source in SECTIONS:
        if args.only and key not in args.only:
            continue
        if source != "gdoc":
            continue
        if key in SHEET_SCHEMAS:
            continue
        existing = cfg["sections"].get(key) or {}
        if existing.get("doc_id") and key not in args.force:
            print(f"  skip doc    {key}  (already has doc_id={existing['doc_id'][:10]}...)")
            continue
        txt_path = sections_dir / f"{key}.txt"
        text = txt_path.read_text() if txt_path.exists() else ""
        if args.dry_run:
            print(f"  CREATE doc   {key}  ({len(text)} bytes)")
            continue
        if existing.get("doc_id") and key in args.force:
            try:
                drive_delete(token, existing["doc_id"])
            except Exception as e:
                print(f"  warn: couldn't delete old doc for {key}: {e}")
        doc_id = create_doc(token, folder_id, f"CV - {key}", text, sa_email)
        cfg["sections"][key] = {"doc_id": doc_id, "source": "gdoc"}
        print(f"  created doc   {key}  doc_id={doc_id}")
        time.sleep(0.2)

    if not args.dry_run:
        save_config(cfg)
        print("Saved config.yaml")


if __name__ == "__main__":
    main()
