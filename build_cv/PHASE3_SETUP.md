# Phase 3 — Automated cloud rebuilds + website deploy

Goal: every Sunday morning your CV at `bdsp-core.github.io/brandon/cv.pdf`
(and `.docx`) is automatically refreshed from your Google Sheets/Docs and
NCBI MyBibliography. No laptop, no manual rebuild.

There's a one-time setup. After it's done, you edit a Sheet → done.

---

## 1. Create the cv-build GitHub repo

1. Create a **private** GitHub repo named `cv-build` (or anything you like) under your account or the bdsp-core org.
2. Copy the contents of this `build_cv/` directory into the new repo's root and push:
   ```bash
   cd /path/to/cv-build-checkout
   cp -R "/Users/mwestover/Library/CloudStorage/Box-Box/Brandon - PHI/!@@@-Work/CV/build_cv/." .
   rm -rf .venv cache output logs token.json credentials.json   # local-only
   git add .
   git commit -m "Initial commit"
   git push
   ```
   The `.gitignore` already excludes the local-only files (venv, secrets, cache, output, logs).

---

## 2. Set up a Google service account (for unattended cloud auth)

A service account is a robot Google identity. Unlike OAuth, it doesn't need a browser to log in — perfect for cron jobs.

1. In Google Cloud Console, with the same project from SETUP.md:
   - Enable the **Sheets API** (alongside Docs + Drive that you enabled before).
   - Go to "IAM & Admin" → "Service Accounts" → **Create Service Account**.
   - Name it `cv-builder`. Click Done (no roles needed at the project level).
2. Click into the new service account → "Keys" tab → **Add Key** → **Create new key** → **JSON**. A `.json` file downloads. **This is the only copy** — keep it safe.
3. Note the service account's email (looks like `cv-builder@<project>.iam.gserviceaccount.com`).
4. Share access:
   - Open your "CV Sections" Drive folder, click Share, paste the service account email, give it **Editor** access. Same for "CV Sheets".
   - Once new Sheets/Docs land in those folders, they inherit the share. So you only do this once.

---

## 3. Add GitHub secrets

In your cv-build repo → Settings → Secrets and variables → Actions → **New repository secret**. Add three:

| Secret name | Value |
|---|---|
| `GOOGLE_SA_JSON` | Paste the entire contents of the service account JSON file from step 2 |
| `NCBI_API_KEY` | (Optional) Your NCBI API key — get one at <https://account.ncbi.nlm.nih.gov/settings/> → API Key Management. Doubles your fetch rate limit. |
| `NCBI_EMAIL` | `mb.westover@gmail.com` (NCBI asks for one with API calls) |
| `WEBSITE_PAT` | A **fine-grained personal access token** with `Contents: Read & Write` on `bdsp-core/bdsp-core.github.io` only. Create one at <https://github.com/settings/tokens?type=beta>. |

---

## 4. Migrate sections to Sheets

This is what makes editing pleasant. Run once, on your laptop, using your OAuth login (the local-dev path), to create the Sheets in your Drive:

```bash
cd build_cv
.venv/bin/python src/bootstrap_sheets.py --dry-run    # preview what will be created
.venv/bin/python src/bootstrap_sheets.py              # actually do it
```

This creates a "CV Sheets" Drive folder with one Sheet per structured section (Honors, Appointments, Grants, Talks, Trainees, …). The tab-structured sections (Honors, Appointments, Awards) are auto-populated from your current CV's content. Grants are also auto-populated. Talks/Trainees start with just headers — fill them in over time.

Now do the same for the prose sections (Identifying Data, Book Chapters, Non-peer-reviewed Articles):

```bash
.venv/bin/python src/bootstrap_gdocs.py --dry-run
.venv/bin/python src/bootstrap_gdocs.py
```

After both bootstraps, `config.yaml` has every section's Sheet/Doc ID. Commit and push it:

```bash
git add config.yaml
git commit -m "Wire up Sheets and Docs IDs"
git push
```

---

## 5. (Optional) Verify locally before turning on the cron

```bash
cd build_cv
.venv/bin/python src/build.py     # fetch everything fresh, build .docx + .pdf
```

Open `output/*.pdf` — it should look like your CV. If anything looks wrong, fix it now (likely in the Sheets, sometimes in `sheets_schema.py`).

---

## 6. Turn on the cron

You're done. The workflow at `.github/workflows/build-cv.yml` will run automatically every Sunday at 13:00 UTC. To trigger immediately, go to the repo → Actions → "Build CV" → **Run workflow**.

On each successful run:
- `output/*.docx` and `*.pdf` are committed to `bdsp-core/bdsp-core.github.io` at `brandon/cv.docx` and `brandon/cv.pdf`.
- The website serves them at `https://bdsp-core.github.io/brandon/cv.pdf` and `…/cv.docx`.
- The Actions run also keeps the build outputs as a downloadable artifact for 90 days (for debugging).

---

## 7. Link from your website

Add to your existing `bdsp-core.github.io/brandon/index.html` (or wherever your bio sits):

```html
<a href="cv.pdf">CV (PDF)</a> ·
<a href="cv.docx">CV (Word)</a>
```

---

## Troubleshooting

- **"Sheet not found" / 404 from Google**: the service account doesn't have access. Re-share the "CV Sheets" folder with the service account email.
- **PDF export fails on GitHub Actions**: LibreOffice install step failed (look at the logs). Re-run; transient apt errors are rare.
- **Action commits "No CV changes — nothing to deploy"**: the build produced the same content as last time (i.e., nothing changed in any Sheet/Doc/MyBib since the last run). This is fine — the cron is idempotent.
- **Need to force a fresh build**: Actions tab → "Build CV" → Run workflow.
