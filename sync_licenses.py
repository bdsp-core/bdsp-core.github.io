#!/usr/bin/env python3
"""
Routine nightly license sync for the bdsp-core organization.

For every active source repo in the bdsp-core org that DOES NOT yet contain a
license file in its root, commits the canonical noncommercial LICENSE.txt
(taken from bdsp-core/CAISR-App/LICENSE.txt) directly to the default branch.

Idempotent: a repo that already has any of {LICENSE, LICENSE.txt, LICENSE.md,
COPYING, COPYING.txt, COPYING.md, UNLICENSE} (case-insensitive) is left alone.

Skips:
  - forks (the upstream license governs)
  - archived / disabled repos (shouldn't be modified)
  - CAISR-App itself (the source of truth)
  - repos listed in LICENSE_SYNC_SKIP env var (comma-separated)

Requires:
  GITHUB_TOKEN  PAT with `repo` scope (contents:write) across the org. Without
                write scope, the script will list what it WOULD do and exit
                non-zero on first PUT attempt.

Optional:
  LICENSE_DRY_RUN=1   print intended actions, make no API writes.
"""

import os
import json
import base64
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

ORG_NAME = "bdsp-core"
SOURCE_REPO = "CAISR-App"
SOURCE_PATH = "LICENSE.txt"
TARGET_PATH = "LICENSE.txt"
COMMIT_MESSAGE = (
    "Add LICENSE.txt (noncommercial)\n\n"
    "Routine sync from bdsp-core/CAISR-App/LICENSE.txt to ensure every active "
    "source repo in the bdsp-core org carries the canonical noncommercial "
    "license. See bdsp-core.github.io for context."
)
LICENSE_NAMES = {
    "license", "license.txt", "license.md", "license.rst",
    "copying", "copying.txt", "copying.md",
    "unlicense", "unlicense.txt", "unlicense.md",
}

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
DRY_RUN = os.environ.get("LICENSE_DRY_RUN") == "1"
SKIP_REPOS = {s.strip() for s in os.environ.get("LICENSE_SYNC_SKIP", "").split(",") if s.strip()}


def gh(method, path, body=None):
    """Minimal GitHub REST helper."""
    url = f"https://api.github.com{path}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "bdsp-license-sync",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode("utf-8")
    req = Request(url, data=data, method=method, headers=headers)
    with urlopen(req, timeout=30) as resp:
        if resp.status == 204:
            return None
        raw = resp.read()
        return json.loads(raw) if raw else None


def list_org_repos():
    repos = []
    page = 1
    while True:
        batch = gh("GET", f"/orgs/{ORG_NAME}/repos?per_page=100&page={page}&type=all")
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return repos


def repo_has_license(name):
    """True iff the repo root contains any common license file (case-insensitive)."""
    try:
        contents = gh("GET", f"/repos/{ORG_NAME}/{name}/contents")
    except HTTPError as e:
        if e.code == 404:
            return False                     # empty repo (no default branch yet)
        raise
    if not isinstance(contents, list):
        return False
    return any(
        item.get("type") == "file" and item.get("name", "").lower() in LICENSE_NAMES
        for item in contents
    )


def fetch_license_source():
    data = gh("GET", f"/repos/{ORG_NAME}/{SOURCE_REPO}/contents/{SOURCE_PATH}")
    return base64.b64decode(data["content"]).decode("utf-8")


def add_license(name, content_b64):
    body = {"message": COMMIT_MESSAGE, "content": content_b64}
    return gh("PUT", f"/repos/{ORG_NAME}/{name}/contents/{TARGET_PATH}", body)


def main():
    if not GITHUB_TOKEN:
        print("ERROR: GITHUB_TOKEN env var not set; cannot list org repos.")
        return 2
    try:
        license_text = fetch_license_source()
    except (HTTPError, URLError) as e:
        print(f"ERROR: could not fetch {SOURCE_REPO}/{SOURCE_PATH}: {e}")
        return 2
    license_b64 = base64.b64encode(license_text.encode("utf-8")).decode()
    print(f"License source: {SOURCE_REPO}/{SOURCE_PATH}  ({len(license_text)} bytes)")
    print(f"DRY_RUN={DRY_RUN}  SKIP={sorted(SKIP_REPOS) or '(none)'}\n")

    repos = list_org_repos()
    print(f"Scanning {len(repos)} repos in {ORG_NAME}/...\n")

    # If the GITHUB_TOKEN can list the org but lacks Contents:write on individual
    # repos, EVERY per-repo PUT will return 403 with this message. Detecting it
    # on the first few tries lets us bail out with a clear actionable summary
    # instead of logging 200+ identical 403s every night.
    SCOPE_MSG = "Resource not accessible by personal access token"
    consecutive_scope_403 = 0

    added, already, skipped, errored = [], [], [], []
    for r in sorted(repos, key=lambda x: x["name"].lower()):
        name = r["name"]
        if name == SOURCE_REPO:
            continue
        if name in SKIP_REPOS:
            skipped.append((name, "in LICENSE_SYNC_SKIP")); continue
        if r.get("fork"):
            skipped.append((name, "fork")); continue
        if r.get("archived"):
            skipped.append((name, "archived")); continue
        if r.get("disabled"):
            skipped.append((name, "disabled")); continue

        try:
            if repo_has_license(name):
                already.append(name); consecutive_scope_403 = 0; continue
            if DRY_RUN:
                added.append(f"{name} [DRY_RUN]")
                print(f"  + [dry] {name}")
                continue
            add_license(name, license_b64)
            added.append(name); consecutive_scope_403 = 0
            print(f"  + added LICENSE.txt to {name}")
        except HTTPError as e:
            try:
                msg = e.read().decode(errors="ignore")[:300]
            except Exception:
                msg = ""
            if e.code == 403 and SCOPE_MSG in msg:
                consecutive_scope_403 += 1
                if consecutive_scope_403 >= 3:
                    print(f"\n*** ABORTING — GITHUB_TOKEN lacks per-repo Contents access. ***")
                    print(f"*** {consecutive_scope_403}+ consecutive 403s with: \"{SCOPE_MSG}\".")
                    print(f"***")
                    print(f"*** The token can list the org but cannot read/write individual")
                    print(f"*** repos. To fix, regenerate the ORG_PAT secret as either:")
                    print(f"***   - fine-grained PAT: Resource owner=bdsp-core, Repository access=")
                    print(f"***     All repositories, Permissions->Repository->Contents=Read & write,")
                    print(f"***     Metadata=Read; OR")
                    print(f"***   - classic PAT: scope `repo` (full repo access).")
                    print(f"*** Then update Settings -> Secrets and variables -> Actions -> ORG_PAT.")
                    print(f"*** (Exit 0 so the workflow's catalog publish step still runs.)")
                    return 0
            errored.append((name, f"HTTP {e.code}: {msg}"))
            print(f"  ! {name}: HTTP {e.code} {msg}")

    print(f"\nSummary")
    print(f"  added:              {len(added)}")
    print(f"  already had a file: {len(already)}")
    print(f"  skipped:            {len(skipped)}")
    if skipped:
        for n, why in skipped:
            print(f"    - {n} ({why})")
    print(f"  errored:            {len(errored)}")
    return 0 if not errored else 1


if __name__ == "__main__":
    raise SystemExit(main())
