"""Find paragraph anchors (header positions) in a docx Document.

A section runs from the paragraph AFTER its header to the paragraph BEFORE the
next anchor (header). Parent headers are anchors too, but produce no content.
"""

from sections import SECTIONS, PARENT_HEADERS


def find_anchors(doc):
    """Return list of (idx, header_text, kind) sorted by paragraph index.

    kind is 'section:<key>' for a configured section, or 'parent' for a
    container header. Anchors define section boundaries.
    """
    leaf_lookup = [(s[0], s[1]) for s in SECTIONS]  # (key, prefix)
    leaf_seen = set()
    parent_seen = set()
    anchors = []

    for i, p in enumerate(doc.paragraphs):
        t = p.text.strip()
        if not t:
            continue
        # Leaf header — prefix match, first occurrence wins
        for key, prefix in leaf_lookup:
            if key in leaf_seen:
                continue
            if t.startswith(prefix):
                anchors.append((i, t, f"section:{key}"))
                leaf_seen.add(key)
                break
        else:
            for ph in PARENT_HEADERS:
                if ph in parent_seen:
                    continue
                if t.startswith(ph):
                    anchors.append((i, t, "parent"))
                    parent_seen.add(ph)
                    break

    anchors.sort(key=lambda a: a[0])
    return anchors


def section_ranges(doc):
    """Return dict: section_key -> (header_idx, content_start_idx, content_end_idx_exclusive).

    content range covers paragraphs strictly between this anchor and the next
    anchor of any kind.
    """
    anchors = find_anchors(doc)
    ranges = {}
    for i, (idx, _text, kind) in enumerate(anchors):
        if not kind.startswith("section:"):
            continue
        key = kind.split(":", 1)[1]
        next_idx = anchors[i + 1][0] if i + 1 < len(anchors) else len(doc.paragraphs)
        ranges[key] = (idx, idx + 1, next_idx)
    return ranges
