"""Convert the assembled .docx to GitHub-Flavored Markdown via pandoc.

This produces semantic Markdown that Jekyll can render as real HTML on
the website's /cv/ page — much crisper than the JPEG-fallback approach
and reflows on mobile / copy-pastes cleanly.

The Word and PDF remain the authoritative downloads; the Markdown is
purely the *web* render.

Requires pandoc on PATH (the GitHub Actions workflow installs it via apt;
on macOS, `brew install pandoc`).
"""

import logging
import shutil
import subprocess
from pathlib import Path

PANDOC = shutil.which("pandoc")


def export_md(docx_path):
    """Convert <stem>.docx -> <stem>.md next to it. Returns the .md path."""
    docx_path = Path(docx_path)
    md_path = docx_path.with_suffix(".md")
    if PANDOC is None:
        raise RuntimeError(
            "pandoc not found on PATH. Install with: "
            "`apt-get install pandoc` (Linux) or `brew install pandoc` (macOS)."
        )
    cmd = [
        PANDOC,
        str(docx_path),
        "-t", "gfm",          # GitHub-Flavored Markdown — Jekyll/kramdown handles it well
        "--wrap=none",        # one paragraph per line; better diffs across runs
        "-o", str(md_path),
    ]
    logging.info("Running: %s", " ".join(cmd))
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"pandoc failed (exit {res.returncode}):\n{res.stderr}")
    if res.stderr.strip():
        logging.info("pandoc stderr: %s", res.stderr.strip())
    logging.info(f"Wrote {md_path} ({md_path.stat().st_size:,} bytes)")
    return md_path
