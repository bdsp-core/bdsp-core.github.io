# Handoff email — automated CV build

> Drop this into an email when you need to hand the system off to a collaborator, future self, or new agent. Plain prose, no jargon assumed.

---

**Subject:** How my CV gets automatically rebuilt + published every week

Hi,

I've automated the rebuilding of my Stanford-format CV so that the PDF on my website (<https://bdsp-core.github.io/brandon/>) stays current without me touching it. Here's a quick orientation so you can find your way around if anything needs changing.

## What it does

Every Sunday morning a GitHub Actions workflow runs in the cloud. It:
1. Pulls structured data from ~27 Google Sheets (one per section of my CV — Honors, Grants, Trainees, Editorial Service, etc.) and ~4 Google Docs (free-text sections like "in press" publications).
2. Pulls my publication list from PubMed via the NCBI E-utilities API (driven by a curated list of PMIDs that I maintain).
3. Assembles everything into a Word document using the original Stanford CV as a formatting template — so the output matches the Stanford CV style exactly (page geometry, fonts, hanging indents, numbered publications list, bold author name in citations, etc.).
4. Exports a PDF.
5. Commits the PDF to my website repo so the public CV link refreshes automatically.

I never have to touch any of the code or push anything manually. To add a new grant or trainee, I just edit a row in a Google Sheet.

## Where the code lives

The active code lives in a **private** GitHub repo I own:

- <https://github.com/mb-westover/cv-build>

A **read-only snapshot** of the same code, plus full documentation, lives inside the website repo itself:

- <https://github.com/bdsp-core/bdsp-core.github.io/tree/gh-pages/build_cv>
- Open the `README.md` in that folder first — it walks through every file and explains the architecture.

If you ever need to make changes, edit the files in the private `mb-westover/cv-build` repo (not the snapshot). The snapshot is for documentation only; the cloud workflow runs from the private repo.

## How to trigger a rebuild manually

From a terminal with `gh` (GitHub CLI) installed and authenticated:

```
gh workflow run build-cv.yml -R mb-westover/cv-build
```

Or via the browser: go to <https://github.com/mb-westover/cv-build/actions>, pick "Build CV" on the left, and hit "Run workflow".

A run takes about 90 seconds. You'll see the new PDF on the website (<https://bdsp-core.github.io/brandon/>) within another minute or two.

## How to inspect a build that failed

Open <https://github.com/mb-westover/cv-build/actions> and click into the failed run. The logs are all there. Most common failures:
- A Google Sheet got renamed, deleted, or moved out of the service account's access — fix by re-sharing the Sheet with the service account email (find it in `config.yaml`'s drive folder or in the secrets).
- Google or NCBI temporarily rate-limited us — just re-run.
- A PMID I added doesn't actually exist in PubMed — pull it out of `data/pmids.txt`.

## How to add new content

| What | Where |
|---|---|
| New grant, honor, trainee, talk, etc. | The corresponding Google Sheet — IDs listed in `config.yaml` in the build_cv repo. Sheets live in my Drive folder "CV Sections". |
| New peer-reviewed publication | Add its PMID to `data/pmids.txt` in `mb-westover/cv-build`, commit. |
| New "in press" or book chapter | The corresponding Google Doc (linked from `config.yaml`). |
| Change to where on the website the CV lives | Edit `.github/workflows/build-cv.yml` in `mb-westover/cv-build` AND `_pages/brandon.md` in the website repo. |

## Authentication summary

- A Google Cloud **service account** has read access to all the CV Sheets and Docs.
- A GitHub **deploy key** (SSH) on the website repo lets the workflow push the rebuilt PDF.
- An NCBI **API key** gives us friendlier rate limits.

All three are stored as **GitHub Actions secrets** in `mb-westover/cv-build` settings. If any need rotating, update them at <https://github.com/mb-westover/cv-build/settings/secrets/actions>.

## If you want to run a build locally

```
cd build_cv
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
GOOGLE_APPLICATION_CREDENTIALS=.secrets/sa.json python src/build.py --offline
open output/*.pdf
```

You'll need:
- A copy of the service-account JSON at `.secrets/sa.json` (get from me, or from GitHub Actions secrets if you have admin access).
- LibreOffice installed (`brew install --cask libreoffice` on macOS) for the PDF export. Microsoft Word works as a fallback.

Use `--offline` to skip the Sheets / Docs / PubMed fetch and reuse cached content — much faster while you're iterating on formatting code.

## What to read first if you need to change formatting

1. **`build_cv/README.md`** — full architecture walkthrough.
2. **`src/assemble.py`** — the docx-emission logic. This is where most "the output doesn't look right" bugs end up getting fixed. Look especially at `HARMONIZE_TEMPLATE_SECTIONS` and `FALLBACK_TEMPLATE_SECTIONS` near the top.
3. **`src/sheets_schema.py`** — declarative schemas for each section's row format. If a section's data is right but the columns are mapped wrong, this is where to look.

## Caveats

- The Stanford CV format relies on lots of paragraph-level direct formatting in the template docx (specific hanging indents, tab stops, numbered list references). We preserve all of that by **cloning** the original template's paragraph properties for each new entry — we never reconstruct styles from a stylesheet. That means: if the template docx is ever replaced, the formatting heuristics may need re-tuning.
- The publication list is driven by a curated PMID list, not by an author-name PubMed search. This is intentional — name collisions in PubMed are common and a search would pull in other Westovers. The trade-off is that I have to add new PMIDs to the list manually (or in a future version, scrape my NCBI MyBibliography).
- Word **tables** in the original template (used for the old Postdoctoral Fellows / Graduate Students / Medical Trainees / etc. lists) have been migrated into Google Sheets and the assembler now deletes any leftover tables in section bounds. If you ever copy back from an unmodified template, expect to re-migrate.

Happy to walk through it live anytime.

— Brandon
