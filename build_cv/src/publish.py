"""Publish the latest built CV to bdsp-core.github.io.

Drops it in as cv/1-Westover_CV.pdf (stable filename — no need to update the
brandon.md link on each run). Pulls latest, copies, commits, pushes.

Safety gates: refuses to publish if the new PDF is < 50KB or < 10 pages, since
that strongly suggests a botched build. Refuses to push to a branch other than
gh-pages. Refuses if the working tree has unrelated changes staged.
"""

import logging
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = Path.home() / "GithubRepos" / "bdsp-core.github.io"
CV_PATH_IN_REPO = "cv/1-Westover_CV.pdf"

MIN_BYTES = 50_000  # smaller than this means something is wrong
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


def publish(pdf_path=None):
    pdf_path = Path(pdf_path) if pdf_path else _latest_pdf()
    if not pdf_path.exists():
        raise FileNotFoundError(f"No PDF to publish at {pdf_path}")

    size = pdf_path.stat().st_size
    pages = _pdf_page_count(pdf_path)
    if size < MIN_BYTES:
        raise RuntimeError(f"PDF too small ({size} bytes) — refusing to publish.")
    if pages < MIN_PAGES:
        raise RuntimeError(f"PDF only {pages} pages — refusing to publish.")
    logging.info(f"Publishing {pdf_path.name} ({size} bytes, {pages} pages)")

    if not REPO.exists():
        raise FileNotFoundError(f"Repo clone not found at {REPO}. See SETUP.md.")

    branch = _run(["git", "branch", "--show-current"], cwd=REPO).stdout.strip()
    if branch != "gh-pages":
        raise RuntimeError(f"Repo is on branch '{branch}', expected 'gh-pages'. Aborting.")

    # Reject if there are unstaged/staged changes to anything OTHER than our target file.
    status = _run(["git", "status", "--porcelain"], cwd=REPO).stdout.strip().splitlines()
    untracked_dirs = (".bundle/", "__pycache__/", "vendor/", "venv/", "_site/")
    foreign = [l for l in status if not (l[3:] == CV_PATH_IN_REPO or any(l[3:].startswith(p) for p in untracked_dirs))]
    if foreign:
        raise RuntimeError("Repo has unrelated working-tree changes:\n  " + "\n  ".join(foreign))

    _run(["git", "pull", "--ff-only"], cwd=REPO)

    dst = REPO / CV_PATH_IN_REPO
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(pdf_path, dst)

    diff_stat = _run(["git", "diff", "--shortstat", "--", CV_PATH_IN_REPO], cwd=REPO).stdout.strip()
    if not diff_stat:
        logging.info("No changes to publish (PDF is identical to current).")
        return

    _run(["git", "add", CV_PATH_IN_REPO], cwd=REPO)
    from datetime import date
    msg = f"CV update {date.today().isoformat()}\n\nAutomated build via build_cv pipeline."
    _run(["git", "commit", "-m", msg], cwd=REPO)
    _run(["git", "push", "origin", "gh-pages"], cwd=REPO)
    logging.info(f"Pushed CV update — {diff_stat}")


def _latest_pdf():
    out_dir = ROOT / "output"
    pdfs = sorted(out_dir.glob("*.pdf"))
    if not pdfs:
        raise FileNotFoundError(f"No PDFs in {out_dir}")
    return pdfs[-1]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    pdf = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    publish(pdf)
