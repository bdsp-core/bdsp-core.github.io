"""Refresh cache/sections/<key>.txt from Google Sheets.

For each section in sheets_schema.SHEET_SCHEMAS that has a configured
sheet_id in config.yaml under sections.<key>:
  1. Read row 2..N of the sheet (row 1 is the column-header row).
  2. Map each row to a dict using schema['columns'] as keys.
  3. Apply the schema's row_format template(s).
  4. Concatenate into a section text file (one paragraph per line, same
     contract as Docs / local-file fetchers).

Same failure policy as Docs: per-section failure logs a warning and keeps the
cached version. One bad sheet doesn't break the whole build.
"""

import logging
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from gauth import get_credentials, sheets_client
from sheets_schema import SHEET_SCHEMAS, render_row


def _row_to_dict(columns, row_values):
    """Pad/truncate row_values to the column count and zip into a dict."""
    out = {}
    for i, col in enumerate(columns):
        out[col] = row_values[i] if i < len(row_values) else ""
    return out


def _is_blank_row(row_dict):
    return all(not (v or "").strip() for v in row_dict.values())


def fetch_one_sheet(sheets, sheet_id, schema):
    """Pull rows from a sheet, render them, return the full section text."""
    # Read all values from the first tab. Sheet tab name is unspecified —
    # read the default range A:Z which covers our 1..4 column layouts.
    resp = sheets.spreadsheets().values().get(
        spreadsheetId=sheet_id, range="A1:Z10000"
    ).execute()
    rows = resp.get("values", [])
    if not rows:
        return "\n"  # empty section

    # Row 0 is the column header row. Skip it; trust schema's column order.
    paragraphs = []
    for r_idx, row in enumerate(rows[1:], start=2):
        row_dict = _row_to_dict(schema["columns"], row)
        if schema.get("skip_blank_rows", True) and _is_blank_row(row_dict):
            continue
        paragraphs.extend(render_row(schema, row_dict))
        if schema.get("blank_line_between_rows"):
            paragraphs.append("")
    return "\n".join(paragraphs) + "\n"


def fetch_all():
    cfg = yaml.safe_load((ROOT / "config.yaml").read_text())
    section_cfg = cfg.get("sections") or {}

    # Which sheet-backed sections are configured?
    configured = []
    for key, schema in SHEET_SCHEMAS.items():
        per = section_cfg.get(key) or {}
        if per.get("source") == "sheet" and per.get("sheet_id"):
            configured.append((key, schema, per["sheet_id"]))

    if not configured:
        logging.info("No sections configured for sheets; skipping Sheets fetch.")
        return

    creds = get_credentials(
        ROOT / cfg["google"]["credentials"],
        ROOT / cfg["google"]["token"],
    )
    sheets = sheets_client(creds)
    sections_dir = ROOT / "cache" / "sections"
    sections_dir.mkdir(parents=True, exist_ok=True)

    pulled = failed = 0
    for key, schema, sheet_id in configured:
        try:
            text = fetch_one_sheet(sheets, sheet_id, schema)
            (sections_dir / f"{key}.txt").write_text(text)
            pulled += 1
        except Exception as e:
            failed += 1
            logging.warning(f"  sheet fetch failed for {key} ({sheet_id}): {e}; keeping cached version")
    logging.info(f"Sheets fetch: pulled={pulled} failed={failed}")
