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
  GITHUB_TOKEN  PAT with `repo` scope (classic) or fine-grained
                Contents: read and write + Metadata: read on the org repos.
                ORG_PAT is also accepted for local/manual runs.

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

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("ORG_PAT")
DRY_RUN = os.environ.get("LICENSE_DRY_RUN") == "1"
SKIP_REPOS = {s.strip() for s in os.environ.get("LICENSE_SYNC_SKIP", "").split(",") if s.strip()}

PERMISSION_HELP = f"""\
ERROR: token can list {ORG_NAME} repos but cannot write repository contents.

The nightly license sync uses GitHub's Contents API to commit {TARGET_PATH} to
each repo that lacks a root license file. GitHub will return 403 until the
Actions secret used here has contents write access to the target repos.

Fix the ORG_PAT secret with either:
  Fine-grained PAT:
    Resource owner: {ORG_NAME}
    Repository access: All repositories, or the exact repos to sync
    Repository permissions:
      Contents: Read and write
      Metadata: Read
  Classic PAT:
    repo scope

Then update this repository's Actions secret named ORG_PAT and rerun the
workflow. No repo writes were attempted after the first permission failure.
"""


def summarize_http_error(error):
    """Return a readable GitHub API error body. Must be called at most once."""
    try:
        raw = error.read().decode("utf-8", errors="ignore")
    except Exception:
        raw = ""
    message = raw
    try:
        payload = json.loads(raw)
        message = payload.get("message") or raw
    except Exception:
        pass
    return message, raw[:500]


def is_token_permission_error(error, message):
    if error.code not in {401, 403}:
        return False
    lower = (message or "").lower()
    return (
        "resource not accessible by personal access token" in lower
        or "bad credentials" in lower
        or "requires authentication" in lower
        or ("must have" in lower and "permission" in lower)
    )


def write_step_summary(text):
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        return
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(text.rstrip() + "\n")
    except OSError:
        pass


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
        print("ERROR: GITHUB_TOKEN or ORG_PAT env var not set; cannot list org repos.")
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

    already, skipped, errored, to_add = [], [], [], []
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
                already.append(name); continue
            to_add.append(name)
            print(f"  + missing {TARGET_PATH}: {name}")
        except HTTPError as e:
            message, raw = summarize_http_error(e)
            if is_token_permission_error(e, message):
                print(f"\nWhile checking {name}: HTTP {e.code} {message}\n")
                print(PERMISSION_HELP)
                write_step_summary(f"### License sync failed\n\n```\n{PERMISSION_HELP}\n```")
                return 3
            errored.append((name, f"HTTP {e.code}: {raw}"))
            print(f"  ! {name}: HTTP {e.code} {raw}")

    print(f"\nScan complete: {len(to_add)} repos need {TARGET_PATH}.")

    added = []
    if DRY_RUN:
        for name in to_add:
            added.append(f"{name} [DRY_RUN]")
            print(f"  + [dry] {name}")
    else:
        for index, name in enumerate(to_add, start=1):
            try:
                add_license(name, license_b64)
                added.append(name)
                print(f"  + added {TARGET_PATH} to {name}")
            except HTTPError as e:
                message, raw = summarize_http_error(e)
                if is_token_permission_error(e, message):
                    remaining = len(to_add) - index
                    print(f"\nWhile writing {name}: HTTP {e.code} {message}\n")
                    print(PERMISSION_HELP)
                    print(f"Repos still unattempted after permission failure: {remaining}")
                    write_step_summary(
                        "### License sync failed\n\n"
                        f"First failing repo: `{name}`\n\n"
                        f"Repos needing `{TARGET_PATH}`: **{len(to_add)}**\n\n"
                        f"Repos still unattempted: **{remaining}**\n\n"
                        f"```\n{PERMISSION_HELP}\n```"
                    )
                    return 3
                errored.append((name, f"HTTP {e.code}: {raw}"))
                print(f"  ! {name}: HTTP {e.code} {raw}")

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
