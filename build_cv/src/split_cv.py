"""One-shot: split current CV docx into per-section text files.

Run once to seed cache/sections/. The output of each file is what you'd paste
into the corresponding Google Doc once Phase 2 is wired up.

Bibliography main pub list (peer_reviewed_original) is written to a parallel
publications_seed.txt for later diffing against NCBI MyBibliography output.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from docx import Document
from anchors import section_ranges
from sections import SECTIONS


def extract_section_text(doc, start, end):
    """Return the verbatim text of paragraphs[start:end], one paragraph per line.

    Empty paragraphs become empty lines (preserves the original blank-line
    visual grouping inside grant entries, etc.).
    """
    lines = []
    for i in range(start, end):
        lines.append(doc.paragraphs[i].text)
    # Collapse trailing empty lines down to exactly one, which preserves the
    # one blank paragraph the Stanford format leaves between sections.
    while len(lines) > 1 and not lines[-1].strip() and not lines[-2].strip():
        lines.pop()
    if not lines or lines[-1].strip():
        lines.append("")
    return "\n".join(lines) + "\n"


def main():
    template = ROOT / "template" / "cv-template.docx"
    out_dir = ROOT / "cache" / "sections"
    out_dir.mkdir(parents=True, exist_ok=True)

    doc = Document(template)
    ranges = section_ranges(doc)

    section_keys = [s[0] for s in SECTIONS]
    missing = [k for k in section_keys if k not in ranges]
    if missing:
        print(f"WARNING: sections not found in template: {missing}")

    for key in section_keys:
        if key not in ranges:
            continue
        _hdr, start, end = ranges[key]
        text = extract_section_text(doc, start, end)
        # Special case: pub list seed goes to a parallel file
        if key == "peer_reviewed_original":
            (ROOT / "cache" / "publications_seed.txt").write_text(text)
            print(f"  publications_seed.txt  ({end - start} paragraphs)")
            continue
        (out_dir / f"{key}.txt").write_text(text)
        print(f"  {key}.txt  ({end - start} paragraphs)")


if __name__ == "__main__":
    main()
