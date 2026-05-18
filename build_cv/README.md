# `build_cv` — automated CV pipeline

This folder is a **read-only snapshot** of the code that builds Brandon Westover's CV every Sunday and publishes the PDF to <https://bdsp-core.github.io/brandon/>. It lives here so that anyone with access to the website repo can read, audit, and propose changes — **but the live code that actually runs in production is in the private repo [`mb-westover/cv-build`](https://github.com/mb-westover/cv-build)**.

> **TL;DR — to change something, edit a file in `mb-westover/cv-build` and push.** The next scheduled run (or a manual `gh workflow run build-cv.yml`) will rebuild and publish the CV.

---

## What it does, in one paragraph

It pulls structured CV data from a stack of Google Sheets (one per section: Honors and Awards, Grants, Trainees, etc.), pulls a few prose sections from Google Docs (e.g. "Peer-reviewed publications, in press"), pulls the publication list from PubMed (a curated PMID file), assembles all that content into a Word document that matches the Stanford CV format exactly (preserving fonts, indents, numbered list for pubs, bold-`Westover MB` in citations), exports a PDF, and publishes the PDF to the website at `cv/1-Westover_CV.pdf`.

---

## Where everything lives

| Asset | Location |
|---|---|
| Live source code | <https://github.com/mb-westover/cv-build> (private) |
| Snapshot for reference | this folder, `build_cv/` in `bdsp-core.github.io` |
| Cloud build runner | GitHub Actions, workflow `Build CV` in `mb-westover/cv-build` |
| Published PDF | `bdsp-core.github.io/cv/1-Westover_CV.pdf` (linked from `_pages/brandon.md`) |
| Google Sheets (one per section) | Brandon's Google Drive — IDs in [`config.yaml`](config.yaml) |
| Google Docs (for free-text sections) | Same Drive — IDs in `config.yaml` |
| Publication PMID list | Tracked in `data/pmids.txt` inside the cv-build repo |
| Manual annotations on pubs | `manual_annotations.yaml` (keyed by PMID) |
| Frozen CV template (Stanford style) | `template/cv-template.docx` |

---

## How it runs

**Schedule:** Sundays at 13:00 UTC (~8 am ET, 5 am PT) — defined in [`.github/workflows/build-cv.yml`](.github/workflows/build-cv.yml).

**Manual trigger:** From the GitHub Actions UI ("Run workflow" button on the [Build CV workflow page](https://github.com/mb-westover/cv-build/actions/workflows/build-cv.yml)) or from the CLI:

```bash
gh workflow run build-cv.yml -R mb-westover/cv-build
gh run watch -R mb-westover/cv-build    # follow the run
```

A run takes ~1.5 minutes. Each run produces an artifact (`output/*.docx`, `*.pdf`, `logs/*.log`) attached to the workflow run for debugging.

**Output:** the workflow pushes a single file — `cv/1-Westover_CV.pdf` — to the `gh-pages` branch of this repo using an SSH deploy key stored as a repo secret (`WEBSITE_DEPLOY_KEY`). The path is **stable**: no date stamps in the filename, no changes to `_pages/brandon.md` ever needed. The PDF link on Brandon's page always points to the same URL.

---

## Authentication

Three secrets are configured in `mb-westover/cv-build`'s GitHub Actions settings:

- `GOOGLE_SA_JSON` — the contents of a Google Cloud service account JSON key. The service account has read access to all the CV Google Sheets and Docs (shared with the SA's email).
- `WEBSITE_DEPLOY_KEY` — an SSH private key matching a deploy key registered on `bdsp-core/bdsp-core.github.io` with **write** access. This is what lets the workflow push the CV PDF.
- `NCBI_API_KEY` / `NCBI_EMAIL` — for PubMed E-utilities polite-pool rate limits (optional but recommended).

If any of these expire or rotate, the workflow will start failing and you'll need to update the secret value at <https://github.com/mb-westover/cv-build/settings/secrets/actions>.

---

## Architecture, file by file

The whole pipeline is six pieces wired together by [`src/build.py`](src/build.py):

```
                          ┌──────────────────────┐
   Google Sheets ───────► │ src/fetch_sheets.py  │ ──► cache/sections/*.txt
                          └──────────────────────┘
                          ┌──────────────────────┐
   Google Docs ─────────► │ src/fetch_sections.py│ ──► cache/sections/*.txt
                          └──────────────────────┘
                          ┌──────────────────────┐
   PubMed E-utilities ──► │ src/pubmed.py        │ ──► cache/publications.json
                          └──────────────────────┘
                                     │
                                     ▼
                          ┌──────────────────────┐
   template/cv-template.docx ──────► │ src/assemble.py      │ ──► output/*.docx
                          └──────────────────────┘
                                     │
                                     ▼
                          ┌──────────────────────┐
                          │ src/export_pdf.py    │ ──► output/*.pdf
                          └──────────────────────┘
                                     │
                                     ▼
                            cv/1-Westover_CV.pdf  (committed by workflow)
```

### Inputs

- **[`src/fetch_sheets.py`](src/fetch_sheets.py)** — pulls each configured Google Sheet, runs each row through its schema's `row_format` template, writes one line per row to `cache/sections/<section_key>.txt`.
- **[`src/fetch_sections.py`](src/fetch_sections.py)** — pulls each configured Google Doc as plain text, writes the same `cache/sections/<section_key>.txt` files. Used for free-text sections (e.g., "in press" pubs, book chapters) where structured rows don't fit.
- **[`src/pubmed.py`](src/pubmed.py)** — given a list of PMIDs, calls NCBI EFetch in batches, parses each record's authors / title / journal / DOI / PMCID / publication date, and produces a uniform citation string matching the Stanford CV style (bolds "Westover MB" via the assembler later).

### Schemas

- **[`src/sheets_schema.py`](src/sheets_schema.py)** — declarative per-section schemas: `columns` (the sheet's column headers in order), `row_format` (how to render each row into a paragraph string), and a few flags (`skip_blank_rows`, `blank_line_between_rows`, `subheading_when_dates_empty`). Tabs (`\t`) in the row_format produce real tab characters which the assembler then aligns via the section's hanging indent.

  Special case: `teaching_pre_stanford` uses `subheading_when_dates_empty: True` so a row with an empty Dates cell renders as a **bold sub-heading** (e.g., "Courses", "Tutorials and Lectures") rather than an entry. The marker is the literal string `[[H]]` prefixed by `render_row`; the assembler strips it and applies bold formatting.

- **[`src/sections.py`](src/sections.py)** — single source of truth for the section list: each entry is `(key, header_prefix, header_template, default_style, source)`. The `header_template` may include `{count}` which gets filled with the live entry count at build time (e.g., "Peer-reviewed original research (370 total)").

- **[`src/anchors.py`](src/anchors.py)** — finds each section's header paragraph in the docx by prefix match. The header positions become anchors that define section boundaries.

### Assembly (the hard part)

- **[`src/assemble.py`](src/assemble.py)** — opens the frozen `template/cv-template.docx`, walks the section anchors, and for each section:
  1. **Captures** the original paragraph properties (`<w:pPr>`: indent, tabs, list-numbering reference) and run properties (`<w:rPr>`: font, color) from the existing content paragraphs. This is how the new content inherits the Stanford styling — we never construct styles from scratch.
  2. **Deletes** the original `<w:p>` and `<w:tbl>` elements in that section (preserves `<w:sectPr>` so page size, margins, headers/footers survive).
  3. **Inserts** new paragraphs whose pPr is cloned from the captured template, with text from the cache file. For publications, the citation gets split into runs around occurrences of "Westover MB" / "Westover BM" so the author name renders bold.
  4. **Updates** the section header text to reflect the new entry count (where applicable).

  Special handling:
  - `FALLBACK_TEMPLATE_SECTIONS` — sections empty in the original template (e.g., `trainees_*`) borrow a pPr from a sibling (`residency_fellowship`) so they inherit the right hanging-indent layout.
  - `HARMONIZE_TEMPLATE_SECTIONS` — for sections whose original pPr was inconsistent with the rest of the CV (e.g., `university_admin_service` had no indent, `service_professional_orgs` had a 1.5" indent), force them to use the `residency_fellowship` 2" hanging indent for visual consistency.

### Output

- **[`src/export_pdf.py`](src/export_pdf.py)** — converts the docx to PDF via `soffice --headless --convert-to pdf` (LibreOffice). On macOS it falls back to Microsoft Word via AppleScript if soffice is unavailable.
- **[`src/publish.py`](src/publish.py)** — used only by the local build path; the cloud workflow has its own push logic in the YAML.

### Orchestration

- **[`src/build.py`](src/build.py)** — entry point. `python src/build.py` runs the whole pipeline. Flags: `--offline` (skip Sheets/Docs/PubMed fetch and reuse cached content), `--no-pdf` (skip PDF export), `--publish` (local-only; cloud uses workflow YAML to push).

### One-shot bootstrap scripts (not run on every build)

- **[`src/split_cv.py`](src/split_cv.py)** — one-time: split the original CV docx into per-section text files. Already run.
- **[`src/seed_to_pmids.py`](src/seed_to_pmids.py)** — one-time: parsed all PMCID/PMID strings out of the original pub list, resolved to PMIDs via NCBI ID converter. Already run; output is `cache/pmids_from_seed.txt` (now `data/pmids.txt` in the live repo).
- **[`src/bootstrap_sheets.py`](src/bootstrap_sheets.py) / [`bootstrap_gdocs.py`](src/bootstrap_gdocs.py) / [`bootstrap_via_drive.py`](src/bootstrap_via_drive.py)** — one-time: created all 27 Google Sheets and 4 Google Docs from the seeded text files, wrote their IDs back into `config.yaml`. Already run.
- **[`src/parse_legacy_into_sheets.py`](src/parse_legacy_into_sheets.py)** — one-time: migrated data from Word **tables** in the original template (trainees, teaching) into the corresponding Google Sheets.

---

## Common tasks

### "I want to add a new grant / honor / trainee"
Open the relevant Google Sheet (IDs in [`config.yaml`](config.yaml) — they're in your Drive folder "CV Sections"). Add a row. Next build picks it up.

### "I want to add a new publication"
Two paths depending on type:
- **Peer-reviewed in PubMed:** add its PMID to `data/pmids.txt` in `mb-westover/cv-build`, commit, push. (Or rebuild the seed by running `seed_to_pmids.py`.)
- **Other (in press / book chapter / non-peer-reviewed):** edit the relevant Google Doc directly. Doc IDs in `config.yaml` under `peer_reviewed_in_press`, `peer_reviewed_other`, etc.

### "The formatting is wrong in section X"
1. Look at the current cache file under `cache/sections/<key>.txt` in the workflow run artifacts (download from the GitHub Actions UI).
2. If the text is right but the layout is wrong, edit [`src/assemble.py`](src/assemble.py) — most likely you want to adjust `HARMONIZE_TEMPLATE_SECTIONS` to point that section at a different pPr donor.
3. If the text itself is wrong, fix the schema in [`src/sheets_schema.py`](src/sheets_schema.py) or the sheet content.

### "I want to trigger a build right now"
```bash
gh workflow run build-cv.yml -R mb-westover/cv-build
```
Or click "Run workflow" in the GitHub Actions UI.

### "The build failed"
1. Open the failed run in <https://github.com/mb-westover/cv-build/actions>.
2. The "Build CV" step's logs show the Python traceback.
3. Most common failures: (a) Google service-account secret expired or revoked; (b) a Google Sheet was renamed or trashed; (c) PubMed rate-limit. All are loggable from the step output.

### "I want to change where the CV gets published"
The workflow YAML pushes to a hardcoded path: `cv/1-Westover_CV.pdf` in the `gh-pages` branch of this repo. Change that in `.github/workflows/build-cv.yml` in `mb-westover/cv-build`, AND update the link in `_pages/brandon.md` here to match.

---

## What's NOT here (and where to find it)

- **`.secrets/sa.json`** — the Google service account credentials. NEVER commit. Stored in GitHub Actions secrets only; for local development you generate your own and put it at `build_cv/.secrets/sa.json`.
- **`cache/`** — regenerated each build. Local clones contain it; CI starts clean.
- **`output/`** — regenerated each build. Local clones may have stale PDFs.
- **`.venv/`** — local virtualenv. Not committed.
- **`credentials.json` / `token.json`** — local OAuth flow files, only used for local dev. Not needed in CI (service account is used instead).

---

## History / why it looks the way it does

A few things that may surprise a future reader:

- **Stanford CV format is preserved by *cloning* the original template's paragraph properties**, not by reconstructing them from a stylesheet. Many sections in the original docx had direct paragraph-level overrides (specific tab stops, hanging indents) that weren't expressible via the "Normal" style. We clone the whole `<w:pPr>` element so all that formatting comes along for free.
- **The publication list uses a numbered list whose paragraph reference (`<w:numPr w:numId="20"/>`) lives in the template's `numbering.xml` part**. We clone the pub paragraph's pPr (including the numId reference) for every new entry, so numbering "just works" — we never add a numbering definition, we ride on the template's.
- **"Westover MB" is bolded by post-processing each rendered citation through a regex** that matches the name in any of its PubMed variants (`Westover MB`, `Westover BM`, `Westover, MB`), then splits the run.
- **The cloud workflow uses an SSH deploy key, not a personal access token**, so revoking access doesn't require touching anyone's GitHub account.

---

## Contact

Code maintained by M. Brandon Westover (mb.westover@gmail.com) with assistance from Claude / Anthropic.
Built originally in May 2026.
