"""Publish the latest built CV to bdsp-core.github.io.

Pushes three artifacts to stable paths under cv/ on the gh-pages branch:
  cv/1-Westover_CV.pdf    — authoritative download
  cv/1-Westover_CV.docx   — Word download
  cv/cv-content.md        — Jekyll-rendered web view (semantic HTML)

Stable filenames mean the brandon.md "View CV" / "Download PDF" /
"Download Word" links never need updating.

Safety gates:
  - PDF must be >= MIN_BYTES and >= MIN_PAGES (catches botched builds).
  - Refuses to push to a branch other than gh-pages.
  - Refuses if the working tree has unrelated staged/unstaged changes.
"""

import logging
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = Path.home() / "GithubRepos" / "bdsp-core.github.io"
CV_DIR_IN_REPO = "cv"
PDF_NAME = "1-Westover_CV.pdf"
DOCX_NAME = "1-Westover_CV.docx"
MD_NAME = "cv-content.md"

MIN_BYTES = 50_000  # smaller PDF than this means something is wrong
MIN_PAGES = 10


def _run(cmd, cwd=None, check=True):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=check)


def _pdf_page_count(pdf_path):
    out = _run(["mdls", "-name", "kMDItemNumberOfPages", str(pdf_path)]).stdout
    # output like 'kMDItemNumberOfPages = 47'
    try:
        return int(out.split("=")[-1].strip())
    except ValueError:
        return -1


def publish(pdf_path=None, docx=None, md=None):
    """Copy pdf/docx/md into the website repo, commit, and push.

    For backwards compatibility, only pdf_path is required; docx and md are
    optional kwargs. The expected caller is build.py, which passes all three.
    """
    pdf_path = Path(pdf_path) if pdf_path else _latest_output("*.pdf")
    if not pdf_path.exists():
        raise FileNotFoundError(f"No PDF to publish at {pdf_path}")

    size = pdf_path.stat().st_size
    pages = _pdf_page_count(pdf_path)
    if size < MIN_BYTES:
        raise RuntimeError(f"PDF too small ({size} bytes) — refusing to publish.")
    if pages < MIN_PAGES:
        raise RuntimeError(f"PDF only {pages} pages — refusing to publish.")
    logging.info(f"Publishing {pdf_path.name} ({size} bytes, {pages} pages)")

    docx_path = Path(docx) if docx else _latest_output("*.docx")
    md_path = Path(md) if md else _latest_output("*.md")

    if not REPO.exists():
        raise FileNotFoundError(f"Repo clone not found at {REPO}. See SETUP.md.")

    branch = _run(["git", "branch", "--show-current"], cwd=REPO).stdout.strip()
    if branch != "gh-pages":
        raise RuntimeError(f"Repo is on branch '{branch}', expected 'gh-pages'. Aborting.")

    targets = {
        f"{CV_DIR_IN_REPO}/{PDF_NAME}": pdf_path,
        f"{CV_DIR_IN_REPO}/{DOCX_NAME}": docx_path if docx_path and docx_path.exists() else None,
        f"{CV_DIR_IN_REPO}/{MD_NAME}":   md_path   if md_path   and md_path.exists()   else None,
    }
    paths_in_repo = {p for p in targets.keys()}

    # Reject if there are unstaged/staged changes to anything OTHER than our target files.
    status = _run(["git", "status", "--porcelain"], cwd=REPO).stdout.strip().splitlines()
    untracked_dirs = (".bundle/", "__pycache__/", "vendor/", "venv/", "_site/")
    foreign = [
        l for l in status
        if not (l[3:] in paths_in_repo or any(l[3:].startswith(p) for p in untracked_dirs))
    ]
    if foreign:
        raise RuntimeError("Repo has unrelated working-tree changes:\n  " + "\n  ".join(foreign))

    _run(["git", "pull", "--ff-only"], cwd=REPO)

    # Copy each artifact into place
    changed = []
    for rel_path, src in targets.items():
        if src is None:
            continue
        dst = REPO / rel_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        diff_stat = _run(["git", "diff", "--shortstat", "--", rel_path], cwd=REPO).stdout.strip()
        if diff_stat:
            _run(["git", "add", rel_path], cwd=REPO)
            changed.append(rel_path)
            logging.info(f"  changed: {rel_path}  ({diff_stat})")
        else:
            logging.info(f"  no change: {rel_path}")

    if not changed:
        logging.info("Nothing to publish (all artifacts unchanged).")
        return

    from datetime import date
    msg = f"CV update {date.today().isoformat()}\n\nAutomated build via build_cv pipeline."
    _run(["git", "commit", "-m", msg], cwd=REPO)
    _run(["git", "push", "origin", "gh-pages"], cwd=REPO)
    logging.info(f"Pushed CV update — {len(changed)} file(s): {', '.join(changed)}")


def _latest_output(glob):
    out_dir = ROOT / "output"
    matches = sorted(out_dir.glob(glob))
    return matches[-1] if matches else None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    pdf = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    publish(pdf)
