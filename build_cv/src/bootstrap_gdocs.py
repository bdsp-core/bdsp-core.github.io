"""One-shot: create the per-section Google Docs from cache/sections/*.txt.

What it does:
  1. Authenticates (opens browser the first time).
  2. Creates a Drive folder "CV Sections" (or reuses if config has its ID).
  3. For each section key in sections.py:
       a. Reads cache/sections/<key>.txt.
       b. Creates a Doc named "CV - <key>" inside the folder.
       c. Inserts the text content.
       d. Records doc_id in config.yaml under sections.<key>.
  4. Sets default_source to 'gdoc' on success.

Idempotent: if a section already has a doc_id in config.yaml, it's skipped.
Re-run with --force <key> to recreate a single section.
"""

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from gauth import get_credentials, drive_client, docs_client
from sections import SECTIONS
from sheets_schema import SHEET_SCHEMAS

FOLDER_NAME = "CV Sections"


def load_config():
    return yaml.safe_load((ROOT / "config.yaml").read_text())


def save_config(cfg):
    (ROOT / "config.yaml").write_text(
        yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True, width=200)
    )


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


def create_doc(drive, docs, folder_id, title, text):
    body = {
        "name": title,
        "mimeType": "application/vnd.google-apps.document",
        "parents": [folder_id],
    }
    f = drive.files().create(body=body, fields="id").execute()
    doc_id = f["id"]
    if text:
        # Insert all text at the start of the document (after the implicit
        # initial empty paragraph at index 1).
        docs.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": [{"insertText": {"location": {"index": 1}, "text": text}}]},
        ).execute()
    return doc_id


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="append", default=[],
                        help="Section keys to recreate (deletes existing doc and creates new).")
    parser.add_argument("--dry-run", action="store_true", help="Just print what would happen.")
    args = parser.parse_args()

    cfg = load_config()
    creds_path = ROOT / cfg["google"]["credentials"]
    token_path = ROOT / cfg["google"]["token"]

    creds = get_credentials(creds_path, token_path)
    drive = drive_client(creds)
    docs = docs_client(creds)

    cfg.setdefault("sections", {}) or None
    if cfg["sections"] is None:
        cfg["sections"] = {}

    if not args.dry_run:
        folder_id = ensure_folder(drive, cfg["google"].get("drive_folder_id") or "")
        cfg["google"]["drive_folder_id"] = folder_id
        print(f"Drive folder: https://drive.google.com/drive/folders/{folder_id}")
    else:
        folder_id = "(dry-run)"

    sections_dir = ROOT / "cache" / "sections"
    for key, prefix, _header_template, _style, source in SECTIONS:
        if source != "gdoc":
            continue  # skipped (e.g. peer_reviewed_original lives in NCBI)
        if key in SHEET_SCHEMAS:
            continue  # this section goes to a Sheet, not a Doc
        existing = cfg["sections"].get(key)
        if existing and existing.get("doc_id") and key not in args.force:
            print(f"  skip   {key}  (already has doc_id={existing['doc_id'][:10]}...)")
            continue
        txt_path = sections_dir / f"{key}.txt"
        text = txt_path.read_text() if txt_path.exists() else ""
        title = f"CV - {key}"
        if args.dry_run:
            print(f"  CREATE {key}  '{title}'  ({len(text)} bytes)")
            continue
        if existing and existing.get("doc_id") and key in args.force:
            try:
                drive.files().delete(fileId=existing["doc_id"]).execute()
            except Exception as e:
                print(f"  warn: couldn't delete old doc for {key}: {e}")
        doc_id = create_doc(drive, docs, folder_id, title, text)
        cfg["sections"][key] = {"doc_id": doc_id, "source": "gdoc"}
        print(f"  created {key}  doc_id={doc_id}")

    if not args.dry_run:
        cfg["default_source"] = "gdoc"
        save_config(cfg)
        print("Saved config.yaml")


if __name__ == "__main__":
    main()
