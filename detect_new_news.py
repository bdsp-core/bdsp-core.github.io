#!/usr/bin/env python3
"""
detect_new_news.py — Detect new publications/datasets and append to the news Google Sheet.

Sources:
  1. PubMed: papers by "Westover MB" indexed in the last LOOKBACK_DAYS days.
  2. bdsp.io: dataset/project entries on the homepage published in the last LOOKBACK_DAYS days.

For each new item not already mentioned in _data/news.yml or in the Sheet,
appends a row [date, headline] to the news Google Sheet. The existing
sync_news_from_sheets.py step then pulls these rows into _data/news.yml.

Run nightly via .github/workflows/sync-team-data.yml, BEFORE the news sync step.

Requires the service account to have EDITOR access to the news Sheet.
"""

import os
import re
import sys
import time
import html
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime

import yaml
from bs4 import BeautifulSoup
from google.oauth2 import service_account
from googleapiclient.discovery import build


NEWS_YML = "_data/news.yml"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = os.environ.get(
    "NEWS_SPREADSHEET_ID", "1i2cyibZBERRqQ5DR76qdHZK3c-FMUsfNwIQjY9HWZJk"
)
SHEET_RANGE = "Sheet1!A:B"

LOOKBACK_DAYS = 30
MAX_NEW_ITEMS = 20  # safety cap per run

NCBI_AUTHOR = "Westover MB[Author]"
NCBI_EMAIL = "westover@mgh.harvard.edu"
NCBI_TOOL = "bdsp_news_detector"
NCBI_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

BDSP_HOME = "https://bdsp.io/"

PMID_RE = re.compile(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d+)")
BDSP_SLUG_RE = re.compile(r"bdsp\.io/content/([^/?#\s]+)")

MONTH_NORMALIZE = {
    "Sept": "Sep",
    "sept": "sep",
    "SEPT": "SEP",
}


def log(msg):
    print(f"[detect_new_news] {msg}", flush=True)


def http_get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "bdsp-news-detector/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def authenticate_sheets():
    creds = service_account.Credentials.from_service_account_file(
        "service-account-key.json", scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds)


def fetch_existing_sheet_rows(service):
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=SPREADSHEET_ID, range=SHEET_RANGE)
        .execute()
    )
    return result.get("values", [])


def collect_dedup_keys(news_yml_path, sheet_rows):
    """Return (set_of_pmids, set_of_bdsp_slugs) already mentioned anywhere."""
    blobs = []
    if os.path.exists(news_yml_path):
        with open(news_yml_path, "r", encoding="utf-8") as f:
            blobs.append(f.read())
    for row in sheet_rows:
        blobs.append(" ".join(str(c) for c in row))
    text = "\n".join(blobs)
    return set(PMID_RE.findall(text)), set(BDSP_SLUG_RE.findall(text))


def append_rows(service, rows):
    if not rows:
        return
    body = {"values": rows}
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=SHEET_RANGE,
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body=body,
    ).execute()


def format_date(dt):
    # Match existing news.yml format, e.g. "16 Dec 2025"
    return f"{dt.day} {dt.strftime('%b')} {dt.year}"


def sanitize_for_md_link_text(s):
    # Markdown link text can't contain unbalanced []; strip them to be safe.
    return s.replace("[", "(").replace("]", ")").strip()


def fetch_recent_pubmed():
    """Return list of dicts: {pmid, title, journal, date} for Westover MB papers
    that appeared on PubMed in the last LOOKBACK_DAYS days."""
    search_params = {
        "db": "pubmed",
        "term": NCBI_AUTHOR,
        "reldate": str(LOOKBACK_DAYS),
        "datetype": "edat",
        "retmax": "100",
        "retmode": "xml",
        "email": NCBI_EMAIL,
        "tool": NCBI_TOOL,
    }
    url = NCBI_BASE + "esearch.fcgi?" + urllib.parse.urlencode(search_params)
    try:
        xml_data = http_get(url, timeout=30)
    except Exception as e:
        log(f"PubMed esearch failed: {e}")
        return []
    root = ET.fromstring(xml_data)
    pmids = [e.text for e in root.findall(".//Id")]
    log(f"PubMed: {len(pmids)} candidate(s) in last {LOOKBACK_DAYS} days")
    if not pmids:
        return []

    time.sleep(0.5)

    fetch_params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
        "email": NCBI_EMAIL,
        "tool": NCBI_TOOL,
    }
    url = NCBI_BASE + "efetch.fcgi?" + urllib.parse.urlencode(fetch_params)
    try:
        xml_data = http_get(url, timeout=60)
    except Exception as e:
        log(f"PubMed efetch failed: {e}")
        return []
    root = ET.fromstring(xml_data)

    out = []
    for art in root.findall(".//PubmedArticle"):
        pmid = art.findtext(".//PMID") or ""
        title_elem = art.find(".//ArticleTitle")
        title = "".join(title_elem.itertext()).strip() if title_elem is not None else ""
        journal = (
            art.findtext(".//Journal/ISOAbbreviation")
            or art.findtext(".//Journal/Title")
            or ""
        ).strip()

        # Use entrez date as the news date (the date PubMed indexed it).
        edate = art.find('.//PubMedPubDate[@PubStatus="entrez"]')
        dt = None
        if edate is not None:
            try:
                dt = datetime(
                    int(edate.findtext("Year")),
                    int(edate.findtext("Month")),
                    int(edate.findtext("Day")),
                )
            except (TypeError, ValueError):
                dt = None
        if dt is None:
            dt = datetime.now()

        if pmid and title:
            out.append({"pmid": pmid, "title": title, "journal": journal, "date": dt})
    return out


def normalize_month(s):
    for k, v in MONTH_NORMALIZE.items():
        s = s.replace(k, v)
    return s


def parse_bdsp_pub_date(text):
    """Parse strings like 'Published: Sept. 9, 2025.\\n      Version: 1.0'."""
    m = re.search(r"Published:\s*([A-Za-z]+\.?\s*\d{1,2},\s*\d{4})", text)
    if not m:
        return None
    raw = m.group(1).replace(".", "")  # 'Sept 9, 2025'
    raw = normalize_month(raw)
    for fmt in ("%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None


def fetch_recent_bdsp():
    """Scrape bdsp.io homepage for project entries published in the last
    LOOKBACK_DAYS days. Returns list of {slug, title, url, date}."""
    try:
        html_bytes = http_get(BDSP_HOME, timeout=30)
    except Exception as e:
        log(f"bdsp.io fetch failed: {e}")
        return []
    soup = BeautifulSoup(html_bytes, "html.parser")
    cutoff = datetime.now()
    out = []
    for proj in soup.select("div.project"):
        h3 = proj.find("h3")
        if not h3:
            continue
        a = h3.find("a", href=True)
        if not a:
            continue
        href = a["href"]
        if not href.startswith("/content/"):
            continue
        title = a.get_text(strip=True)
        pub_p = proj.find("p", class_="pub-details")
        pub_text = pub_p.get_text(" ", strip=True) if pub_p else ""
        dt = parse_bdsp_pub_date(pub_text)
        if dt is None:
            continue
        if (cutoff - dt).days > LOOKBACK_DAYS:
            continue
        slug_match = BDSP_SLUG_RE.search("https://bdsp.io" + href)
        slug = slug_match.group(1) if slug_match else None
        if not slug:
            continue
        full_url = "https://bdsp.io" + href if href.startswith("/") else href
        out.append({"slug": slug, "title": title, "url": full_url, "date": dt})
    log(f"bdsp.io: {len(out)} candidate(s) in last {LOOKBACK_DAYS} days")
    return out


def build_pubmed_headline(item):
    title = sanitize_for_md_link_text(html.unescape(item["title"]))
    url = f"https://pubmed.ncbi.nlm.nih.gov/{item['pmid']}/"
    journal = item["journal"]
    if journal:
        return f'[{title}]({url}) is published in {journal}'
    return f'[{title}]({url}) is published'


def build_bdsp_headline(item):
    title = sanitize_for_md_link_text(item["title"])
    return f'[{title}]({item["url"]}) is published on bdsp.io'


def main():
    if not os.path.exists("service-account-key.json"):
        log("ERROR: service-account-key.json not found; aborting.")
        sys.exit(0)  # don't fail the workflow — just skip

    log("Authenticating with Google Sheets...")
    service = authenticate_sheets()

    log("Reading existing Sheet rows...")
    sheet_rows = fetch_existing_sheet_rows(service)

    log("Collecting dedup keys from news.yml + Sheet...")
    seen_pmids, seen_slugs = collect_dedup_keys(NEWS_YML, sheet_rows)
    log(f"Seen: {len(seen_pmids)} PMIDs, {len(seen_slugs)} bdsp slugs")

    new_rows = []

    for item in fetch_recent_pubmed():
        if item["pmid"] in seen_pmids:
            continue
        seen_pmids.add(item["pmid"])
        headline = build_pubmed_headline(item)
        date_str = format_date(item["date"])
        log(f"+ PubMed: {date_str} | {headline}")
        new_rows.append([date_str, headline])
        if len(new_rows) >= MAX_NEW_ITEMS:
            break

    if len(new_rows) < MAX_NEW_ITEMS:
        for item in fetch_recent_bdsp():
            if item["slug"] in seen_slugs:
                continue
            seen_slugs.add(item["slug"])
            headline = build_bdsp_headline(item)
            date_str = format_date(item["date"])
            log(f"+ bdsp.io: {date_str} | {headline}")
            new_rows.append([date_str, headline])
            if len(new_rows) >= MAX_NEW_ITEMS:
                break

    if not new_rows:
        log("No new items to add.")
        return

    log(f"Appending {len(new_rows)} new row(s) to the news Sheet...")
    append_rows(service, new_rows)
    log("Done.")


if __name__ == "__main__":
    main()
