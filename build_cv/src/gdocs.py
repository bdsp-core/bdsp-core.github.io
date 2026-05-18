"""Google Docs: read plain-text content from a Doc. Auth via gauth.py."""

from gauth import get_credentials, docs_client, drive_client


def doc_to_text(doc):
    """Convert a documents.get response to plain text, one paragraph per line.

    Tabs inside a paragraph are preserved as `\t`. Mirrors how the splitter
    extracts text from the docx so the assembler treats both sources identically.
    """
    lines = []
    for block in doc.get("body", {}).get("content", []):
        para = block.get("paragraph")
        if para is None:
            continue
        line_parts = []
        for el in para.get("elements", []):
            tr = el.get("textRun")
            if tr is not None:
                line_parts.append(tr.get("content", ""))
        text = "".join(line_parts)
        if text.endswith("\n"):
            text = text[:-1]
        lines.append(text)
    return "\n".join(lines) + "\n"


def fetch_doc_text(creds, doc_id):
    doc = docs_client(creds).documents().get(documentId=doc_id).execute()
    return doc_to_text(doc)
