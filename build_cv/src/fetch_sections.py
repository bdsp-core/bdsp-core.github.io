"""Refresh cache/sections/<key>.txt from Google Docs.

For each configured section whose source is 'gdoc' and that has a doc_id, pull
the Doc's plain text and write it to disk. Sections without a doc_id (or with
source='local') are left untouched — their existing text files are reused.

On any per-section fetch failure, we keep the previous cached file and log a
warning. That way one bad Doc doesn't break the whole build.
"""

import logging
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from gauth import get_credentials
from gdocs import fetch_doc_text
from sections import SECTIONS


def fetch_all():
    cfg = yaml.safe_load((ROOT / "config.yaml").read_text())
    default_source = cfg.get("default_source", "local")
    section_cfg = cfg.get("sections") or {}

    # Decide if we even need Google auth (any section actually pulling from gdoc?)
    needs_gdoc = False
    for key, _p, _h, _s, source in SECTIONS:
        if source != "gdoc":
            continue
        per = section_cfg.get(key) or {}
        effective_source = per.get("source", default_source)
        if effective_source == "gdoc" and per.get("doc_id"):
            needs_gdoc = True
            break
    if not needs_gdoc:
        logging.info("No sections configured for gdoc; skipping Google Docs fetch.")
        return

    creds = get_credentials(ROOT / cfg["google"]["credentials"],
                             ROOT / cfg["google"]["token"])
    sections_dir = ROOT / "cache" / "sections"
    sections_dir.mkdir(parents=True, exist_ok=True)

    pulled = 0
    skipped = 0
    failed = 0
    for key, _p, _h, _s, source in SECTIONS:
        if source != "gdoc":
            continue
        per = section_cfg.get(key) or {}
        effective_source = per.get("source", default_source)
        doc_id = per.get("doc_id")
        if effective_source != "gdoc" or not doc_id:
            skipped += 1
            continue
        try:
            text = fetch_doc_text(creds, doc_id)
            (sections_dir / f"{key}.txt").write_text(text)
            pulled += 1
        except Exception as e:
            failed += 1
            logging.warning(f"  fetch failed for {key} ({doc_id}): {e}; keeping cached version")
    logging.info(f"Google Docs fetch: pulled={pulled} skipped={skipped} failed={failed}")
