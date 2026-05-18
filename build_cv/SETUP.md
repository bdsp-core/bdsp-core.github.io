# CV Build — Setup

One-time setup needed before Phase 2 (Google Docs) will work.

## 1. Google Cloud project + OAuth client

You only do this once. The credentials sit on your laptop; nothing is published anywhere.

1. Go to <https://console.cloud.google.com/projectcreate> and create a project
   (any name — e.g. "cv-build"). Switch into it.
2. Enable the Docs and Drive APIs:
   - <https://console.cloud.google.com/apis/library/docs.googleapis.com> — click Enable.
   - <https://console.cloud.google.com/apis/library/drive.googleapis.com> — click Enable.
3. Configure the OAuth consent screen (left sidebar → "OAuth consent screen"):
   - User Type: **External**
   - App name: `cv-build` (any string)
   - User support email + developer contact email: your Gmail
   - Scopes: skip (we request them at runtime)
   - Test users: add `mb.westover@gmail.com` (your Gmail) — required so you
     can authorize without going through Google's app verification.
   - Publishing status: leave as **Testing**. Test mode is fine indefinitely
     for a personal tool — the only catch is that refresh tokens expire every
     7 days, so you'll re-auth weekly. If that's annoying, click "Publish App"
     later (no review needed for internal-only scopes you're already using).
4. Create OAuth credentials (left sidebar → "Credentials" → "+ Create
   credentials" → "OAuth client ID"):
   - Application type: **Desktop app**
   - Name: `cv-build` (any)
   - Click Create, then **Download JSON**.
5. Save the downloaded JSON as [build_cv/credentials.json](credentials.json).
   This file is `.gitignore`d.

## 2. Create the per-section Google Docs

From inside `build_cv/`, run the bootstrap:

```bash
.venv/bin/python src/bootstrap_gdocs.py --dry-run   # preview what will be created
.venv/bin/python src/bootstrap_gdocs.py             # actually create them
```

What this does:

- First run opens a browser for OAuth consent. Approve it. A `token.json` is
  saved so subsequent runs are unattended.
- Creates a Drive folder called **"CV Sections"** in your Google Drive.
- Creates one Doc per section ("CV - identifying_data", "CV - colleges", …)
  pre-populated with the text already extracted from your current CV.
- Writes the Doc IDs to `config.yaml` and flips `default_source` to `gdoc`.

After that you can edit any section's Google Doc directly. The next build
pulls the new content.

## 3. (Optional later) NCBI MyBibliography

For now the pub list comes from `cache/pmids_from_seed.txt` (derived from your
existing CV). To switch to live MyBib pulls, you have two options:

- **Public sharing URL**: In NCBI MyBibliography → Manage My Bibliography → "Make
  Public", grab the URL ending in `/bibliography/public/`, and put it in
  `config.yaml` under `publications.mybib_url`. (TODO: scraper not yet wired —
  ask me when you're ready and I'll add it.)
- **Exported PMIDs**: From MyBib → Export → PMID list → save the file as
  `cache/pmids.txt`. The build will use it automatically (it takes precedence
  over the seed file).

## 4. Run the build

```bash
.venv/bin/python src/build.py                  # full refresh: Google Docs + NCBI + assemble + PDF
.venv/bin/python src/build.py --offline        # reuse last-cached pulls, just rebuild
.venv/bin/python src/build.py --no-pdf         # skip PDF
```

Outputs land in `output/` named `1-Westover-SU-CV-YYYY-MM-DD.docx` (+.pdf).

## 5. Weekly auto-rebuild (Phase 3)

When the build is dialed in, ask me to add a launchd job and we'll wire it to
run Sundays at 6am with email-on-failure.
