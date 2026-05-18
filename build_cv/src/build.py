"""End-to-end CV build.

Steps:
  1. Refresh publications.json from NCBI (using cache/pmids.txt — for Phase 1
     this is cache/pmids_from_seed.txt; later it'll be MyBibliography-derived).
     If --offline is passed, skip and reuse cached publications.json.
  2. Run the assembler.
  3. Export PDF.
  4. Write outputs to output/ with today's date stamp.

Failure policy: if any step fails, leave previous outputs untouched. Always log
to logs/build-YYYY-MM-DD.log so the launchd job leaves an audit trail.
"""

import argparse
import json
import logging
import sys
import traceback
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from pubmed import fetch_publications, read_pmid_file
from assemble import assemble
from export_pdf import export_pdf
from export_md import export_md
from fetch_sections import fetch_all as fetch_gdoc_sections
from publish import publish as publish_to_website
from fetch_sheets import fetch_all as fetch_sheet_sections


def setup_logging():
    log_dir = ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"build-{date.today().isoformat()}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler(log_path), logging.StreamHandler()],
    )
    return log_path


def refresh_publications():
    """Refresh cache/publications.json from PubMed using the tracked PMID list."""
    pmid_file = ROOT / "data" / "pmids.txt"
    if not pmid_file.exists():
        raise FileNotFoundError(f"PMID list not found at {pmid_file}.")
    pmids = read_pmid_file(pmid_file)
    logging.info(f"Fetching {len(pmids)} PMIDs from PubMed...")
    recs = fetch_publications(pmids)
    logging.info(f"  Got {len(recs)} records.")
    out = ROOT / "cache" / "publications.json"
    out.write_text(json.dumps(recs, indent=2))
    return len(recs)


def main():
    parser = argparse.ArgumentParser(description="Build Westover CV")
    parser.add_argument("--offline", action="store_true",
                        help="Skip NCBI refresh; reuse cached publications.json")
    parser.add_argument("--no-pdf", action="store_true", help="Skip PDF export")
    parser.add_argument("--publish", action="store_true",
                        help="After build, push the PDF to bdsp-core.github.io")
    parser.add_argument("--out-stem", default=None,
                        help="Override output filename stem (default: 1-Westover-SU-CV-YYYY-MM-DD)")
    args = parser.parse_args()

    log_path = setup_logging()
    logging.info(f"Logging to {log_path}")

    try:
        if not args.offline:
            logging.info("Fetching Sheets-backed sections...")
            fetch_sheet_sections()
            logging.info("Fetching Docs-backed sections...")
            fetch_gdoc_sections()
            refresh_publications()
        else:
            logging.info("--offline: skipping Sheets/Docs fetch + NCBI refresh.")

        stem = args.out_stem or f"1-Westover-SU-CV-{date.today().isoformat()}"
        out_docx = ROOT / "output" / f"{stem}.docx"
        out_docx.parent.mkdir(parents=True, exist_ok=True)
        logging.info(f"Assembling {out_docx}")
        assemble(out_docx)

        pdf = None
        if not args.no_pdf:
            logging.info("Exporting PDF...")
            pdf = export_pdf(out_docx)
            logging.info(f"Wrote {pdf}")

        logging.info("Exporting Markdown for the web viewer...")
        md = export_md(out_docx)
        logging.info(f"Wrote {md}")

        if args.publish:
            if pdf is None:
                raise RuntimeError("--publish requires PDF export (don't combine with --no-pdf)")
            logging.info("Publishing to bdsp-core.github.io...")
            publish_to_website(pdf, docx=out_docx, md=md)

        logging.info("Build complete.")
    except Exception:
        logging.error("Build FAILED:\n" + traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
