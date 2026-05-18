"""Fetch publications from PubMed and format them in CV citation style.

Inputs (any one of):
- pmid_file:    path to a text file with one PMID per line
- pubmed_query: a PubMed query string (uses ESearch first, then EFetch)
- mybib_url:    public NCBI MyBibliography URL (scrape for PMIDs)

Output: list of dicts (one per pub) plus a formatted citation string for each.
"""

import os
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

NCBI_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
API_KEY = os.environ.get("NCBI_API_KEY")  # optional but doubles rate limit
EMAIL = os.environ.get("NCBI_EMAIL", "mb.westover@gmail.com")
TOOL = "cv-build"


def _params(extra):
    p = {"tool": TOOL, "email": EMAIL}
    if API_KEY:
        p["api_key"] = API_KEY
    p.update(extra)
    return p


def esearch_pmids(query, retmax=10000):
    """Return list of PMIDs matching a PubMed query."""
    r = requests.get(
        f"{NCBI_BASE}/esearch.fcgi",
        params=_params({"db": "pubmed", "term": query, "retmax": retmax, "retmode": "json"}),
        timeout=30,
    )
    r.raise_for_status()
    return r.json().get("esearchresult", {}).get("idlist", [])


def efetch_pubmed(pmids, batch=100):
    """Fetch PubMed XML records in batches. Returns list of PubmedArticle Elements."""
    pmids = [str(p).strip() for p in pmids if str(p).strip()]
    articles = []
    for i in range(0, len(pmids), batch):
        chunk = pmids[i : i + batch]
        r = requests.post(
            f"{NCBI_BASE}/efetch.fcgi",
            data=_params({"db": "pubmed", "id": ",".join(chunk), "retmode": "xml"}),
            timeout=60,
        )
        r.raise_for_status()
        root = ET.fromstring(r.content)
        articles.extend(root.findall(".//PubmedArticle"))
        # NCBI: ≤3 req/sec without key, ≤10 with. Be polite.
        time.sleep(0.34 if not API_KEY else 0.11)
    return articles


def _text(el, path, default=""):
    n = el.find(path)
    return (n.text or default).strip() if n is not None and n.text else default


def parse_article(article):
    """Pull the fields we need out of a PubmedArticle XML element."""
    pmid = _text(article, ".//MedlineCitation/PMID")
    title = "".join(article.find(".//Article/ArticleTitle").itertext()).strip() if article.find(".//Article/ArticleTitle") is not None else ""
    title = re.sub(r"\s+", " ", title)
    if title.endswith("."):
        title = title[:-1]

    authors = []
    for au in article.findall(".//AuthorList/Author"):
        last = _text(au, "LastName")
        initials = _text(au, "Initials")
        collective = _text(au, "CollectiveName")
        if last:
            authors.append(f"{last} {initials}".strip())
        elif collective:
            authors.append(collective)

    journal = _text(article, ".//Journal/ISOAbbreviation") or _text(article, ".//Journal/Title")

    year = _text(article, ".//Journal/JournalIssue/PubDate/Year")
    if not year:
        # MedlineDate fallback like "2021 Jan-Feb"
        md = _text(article, ".//Journal/JournalIssue/PubDate/MedlineDate")
        m = re.match(r"(\d{4})", md)
        year = m.group(1) if m else ""
    month = _text(article, ".//Journal/JournalIssue/PubDate/Month")
    day = _text(article, ".//Journal/JournalIssue/PubDate/Day")
    volume = _text(article, ".//Journal/JournalIssue/Volume")
    issue = _text(article, ".//Journal/JournalIssue/Issue")
    pages = _text(article, ".//Pagination/MedlinePgn") or _text(article, ".//Pagination/StartPage")

    doi = ""
    pmcid = ""
    # Use ONLY PubmedData/ArticleIdList — descendant search would pick up
    # ArticleId nodes inside the references list.
    for aid in article.findall("./PubmedData/ArticleIdList/ArticleId"):
        kind = aid.get("IdType", "")
        val = (aid.text or "").strip()
        if kind == "doi":
            doi = val
        elif kind == "pmc":
            pmcid = val
            if not pmcid.startswith("PMC"):
                pmcid = "PMC" + pmcid
    # Fallback: DOI is sometimes only in Article/ELocationID
    if not doi:
        for eloc in article.findall("./MedlineCitation/Article/ELocationID"):
            if eloc.get("EIdType") == "doi" and eloc.text:
                doi = eloc.text.strip()
                break

    # "Epub ahead of print" marker
    pub_status = _text(article, ".//PublicationStatus")
    epub_ahead = pub_status.lower() == "aheadofprint"

    # Separate Epub date (when present alongside a print PubDate)
    epub_date = ""
    for ad in article.findall("./MedlineCitation/Article/ArticleDate"):
        if ad.get("DateType") == "Electronic":
            y = _text(ad, "Year")
            m = _text(ad, "Month")
            d = _text(ad, "Day")
            # Convert numeric month to abbreviation
            try:
                import calendar
                if m.isdigit():
                    m = calendar.month_abbr[int(m)]
            except (ValueError, IndexError):
                pass
            epub_date = " ".join(b for b in [y, m, d] if b)
            break

    return {
        "pmid": pmid,
        "title": title,
        "authors": authors,
        "journal": journal,
        "year": year,
        "month": month,
        "day": day,
        "volume": volume,
        "issue": issue,
        "pages": pages,
        "doi": doi,
        "pmcid": pmcid,
        "epub_ahead": epub_ahead,
        "epub_date": epub_date,
    }


def format_citation(rec, annotation=""):
    """Produce a citation string matching the Stanford-format style used in the CV.

    Pattern (close to PubMed AMA):
        Authors. "Title." Journal. Year[ Month][ Day];Vol(Iss):Pages. doi: X.[ Epub ahead of print.] PMCID: PMCxxxxx.[annotation]
    Falls back to PMID when no PMCID is available.
    """
    authors = ", ".join(rec["authors"])
    parts = [f"{authors}."] if authors else []

    title = rec["title"].strip()
    if not (title.startswith("“") or title.startswith('"')):
        title = f"“{title}.”"
    parts.append(title)

    journal = rec["journal"].strip()
    if journal:
        parts.append(f"{journal}.")

    date_bits = [rec["year"]]
    if rec["month"]:
        date_bits.append(rec["month"])
    if rec["day"]:
        date_bits.append(rec["day"])
    date_str = " ".join(b for b in date_bits if b)

    locus = ""
    if rec["volume"]:
        locus = rec["volume"]
        if rec["issue"]:
            locus += f"({rec['issue']})"
    if rec["pages"]:
        locus = f"{locus}:{rec['pages']}" if locus else rec["pages"]

    if date_str and locus:
        parts.append(f"{date_str};{locus}.")
    elif date_str:
        parts.append(f"{date_str}.")
    elif locus:
        parts.append(f"{locus}.")

    if rec["doi"]:
        parts.append(f"doi: {rec['doi']}.")
    if rec["epub_ahead"]:
        parts.append("Epub ahead of print.")
    elif rec.get("epub_date") and rec["epub_date"] != date_str:
        parts.append(f"Epub {rec['epub_date']}.")

    if rec["pmcid"]:
        parts.append(f"PMCID: {rec['pmcid']}.")
    elif rec["pmid"]:
        parts.append(f"PMID: {rec['pmid']}.")

    cite = " ".join(parts)
    if annotation:
        cite = f"{cite} {annotation}".rstrip()
    return cite


def fetch_publications(pmids):
    """High-level: list of PMIDs → list of parsed records (preserves order)."""
    if not pmids:
        return []
    articles = efetch_pubmed(pmids)
    by_pmid = {}
    for a in articles:
        rec = parse_article(a)
        if rec["pmid"]:
            by_pmid[rec["pmid"]] = rec
    return [by_pmid[p] for p in pmids if p in by_pmid]


def pmcids_to_pmids(pmcids, batch=200):
    """Convert PMCIDs → PMIDs via the NCBI ID Converter API."""
    out = {}
    pmcids = [p if p.startswith("PMC") else f"PMC{p}" for p in pmcids]
    url = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/"
    for i in range(0, len(pmcids), batch):
        chunk = pmcids[i : i + batch]
        r = requests.get(
            url,
            params={"tool": TOOL, "email": EMAIL, "ids": ",".join(chunk), "format": "json"},
            timeout=60,
        )
        r.raise_for_status()
        for rec in r.json().get("records", []):
            if "pmcid" in rec and "pmid" in rec:
                out[str(rec["pmcid"])] = str(rec["pmid"])
        time.sleep(0.34 if not API_KEY else 0.11)
    return out


def read_pmid_file(path):
    """Read a file of PMIDs (one per line, # comments and blank lines ignored)."""
    out = []
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # tolerate "PMID: 12345" or "12345"
        m = re.search(r"(\d{6,9})", line)
        if m:
            out.append(m.group(1))
    return out
