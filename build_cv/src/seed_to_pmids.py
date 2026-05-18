"""Convert the seed publications file (with PMCIDs/PMIDs) into a clean PMID list.

This is a one-time bridge: we extract every PMCID and bare PMID from the
existing CV's pub list, resolve PMCIDs to PMIDs, and produce
cache/pmids_from_seed.txt — a canonical PMID-per-line file we can validate the
formatter against (and use as the starting publication list until the user has
NCBI MyBibliography configured).
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from pubmed import pmcids_to_pmids


def main():
    seed = (ROOT / "cache" / "publications_seed.txt").read_text()

    # Per-line parse: keep order, capture (pmid, pmcid) per line. Some lines are
    # not pub entries at all (e.g., "Featured article..." sub-bullets).
    ordered = []  # list of (line_idx, pmcid_or_None, pmid_or_None)
    for i, line in enumerate(seed.splitlines()):
        pmcid_m = re.search(r"PMC\d+", line)
        pmid_m = re.search(r"PMID:\s*(\d+)", line)
        if pmcid_m or pmid_m:
            ordered.append((i, pmcid_m.group(0) if pmcid_m else None, pmid_m.group(1) if pmid_m else None))

    pmcids = [p[1] for p in ordered if p[1]]
    print(f"Resolving {len(pmcids)} PMCIDs → PMIDs ...")
    mapping = pmcids_to_pmids(pmcids)
    print(f"  Resolved {len(mapping)} / {len(pmcids)}")

    unresolved = []
    pmids_out = []
    for _idx, pmcid, pmid in ordered:
        if pmcid and pmcid in mapping:
            pmids_out.append(mapping[pmcid])
        elif pmid:
            pmids_out.append(pmid)
        else:
            unresolved.append(pmcid or "?")

    # Dedupe while preserving order
    seen = set()
    final = []
    for p in pmids_out:
        if p not in seen:
            seen.add(p)
            final.append(p)
    print(f"Unique PMIDs: {len(final)}")
    if unresolved:
        print(f"Unresolved PMCIDs: {len(unresolved)} (first 5: {unresolved[:5]})")

    out_path = ROOT / "cache" / "pmids_from_seed.txt"
    out_path.write_text("\n".join(final) + "\n")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
