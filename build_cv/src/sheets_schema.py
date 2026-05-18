"""Per-section schemas for Sheet-backed sections.

Each schema defines:
  - columns: ordered list of column headers in the Google Sheet's row-1
  - row_format: either a string template (one line per row) or a list of
    string templates (multi-line per row, e.g. grants: dates+funder/title/role)
  - skip_blank_rows: True to ignore rows where every column is empty
  - blank_line_between_rows: True to emit a blank paragraph between rendered rows

Placeholders in row_format use Python str.format with column names as keys.
Tabs (\t) within a template emit a real tab character — used for the date /
content two-column layout in many sections.

Sections NOT in this dict stay as Google Docs (prose) or local files.
"""

SHEET_SCHEMAS = {
    # ---- Identifying data: simple key/value table ----
    "identifying_data": {
        "columns": ["Field", "Value"],
        "row_format": "{Field}\t{Value}",
        "skip_blank_rows": True,
        "blank_line_between_rows": False,
    },

    # ---- Single-line, tab-separated sections ----
    "honors_awards": {
        "columns": ["Year", "Award", "Organization", "Description"],
        "row_format": "{Year}\t{Award}\t{Organization}\t{Description}",
        "skip_blank_rows": True,
        "blank_line_between_rows": False,
    },
    "academic_appointments": {
        "columns": ["Dates", "Description"],
        "row_format": "{Dates}\t{Description}",
        "skip_blank_rows": True,
        "blank_line_between_rows": False,
    },
    "other_appointments": {
        "columns": ["Dates", "Description"],
        "row_format": "{Dates}\t{Description}",
        "skip_blank_rows": True,
        "blank_line_between_rows": False,
    },
    "colleges": {
        "columns": ["Date", "Degree"],
        "row_format": "{Date}\t{Degree}",
        "skip_blank_rows": True,
        "blank_line_between_rows": False,
    },
    "residency_fellowship": {
        "columns": ["Dates", "Description"],
        "row_format": "{Dates}\t{Description}",
        "skip_blank_rows": True,
        "blank_line_between_rows": False,
    },
    "board_certification": {
        "columns": ["Year", "Description"],
        "row_format": "{Year}\t\t\t\t{Description}",
        "skip_blank_rows": True,
        "blank_line_between_rows": False,
    },

    # ---- Multi-line per row: grants ----
    "grants_current": {
        "columns": ["Dates", "Funder", "Title", "Role"],
        "row_format": [
            "{Dates}\tFunder: {Funder}",
            "Title: {Title}",
            "Role: {Role}",
        ],
        "skip_blank_rows": True,
        "blank_line_between_rows": True,
    },
    "grants_submitted": {
        "columns": ["Dates", "Funder", "Title", "Role"],
        "row_format": [
            "{Dates}\tFunder: {Funder}",
            "Title: {Title}",
            "Role: {Role}",
        ],
        "skip_blank_rows": True,
        "blank_line_between_rows": True,
    },
    "grants_completed": {
        "columns": ["Dates", "Funder", "Title", "Role"],
        "row_format": [
            "{Dates}\tFunder: {Funder}",
            "Title: {Title}",
            "Role: {Role}",
        ],
        "skip_blank_rows": True,
        "blank_line_between_rows": True,
    },

    # ---- Editorial / service ----
    "editorial_service": {
        "columns": ["Dates", "Description"],
        "row_format": "{Dates}\t{Description}",
        "skip_blank_rows": True,
        "blank_line_between_rows": False,
    },
    "ad_hoc_reviewer": {
        "columns": ["Dates", "Journal"],
        "row_format": "{Dates}\t{Journal}",
        "skip_blank_rows": True,
        "blank_line_between_rows": False,
    },
    "grant_reviewer": {
        "columns": ["Dates", "Description"],
        "row_format": "{Dates}\t{Description}",
        "skip_blank_rows": True,
        "blank_line_between_rows": False,
    },
    "university_admin_service": {
        "columns": ["Dates", "Description"],
        "row_format": "{Dates}\t{Description}",
        "skip_blank_rows": True,
        "blank_line_between_rows": False,
    },
    "service_professional_orgs": {
        "columns": ["Dates", "Description"],
        "row_format": "{Dates}\t{Description}",
        "skip_blank_rows": True,
        "blank_line_between_rows": False,
    },
    "community_service": {
        "columns": ["Dates", "Description"],
        "row_format": "{Dates}\t{Description}",
        "skip_blank_rows": True,
        "blank_line_between_rows": False,
    },

    # ---- Invited talks ----
    "invited_grand_rounds": {
        "columns": ["Date", "Title", "Venue", "Location"],
        "row_format": '“{Title}.” {Venue}, {Location} ({Date})',
        "skip_blank_rows": True,
        "blank_line_between_rows": False,
    },
    "invited_local": {
        "columns": ["Date", "Title", "Venue", "Location"],
        "row_format": '“{Title}.” {Venue}, {Location} ({Date})',
        "skip_blank_rows": True,
        "blank_line_between_rows": False,
    },
    "invited_national": {
        "columns": ["Date", "Title", "Venue", "Location"],
        "row_format": '“{Title}.” {Venue}, {Location} ({Date})',
        "skip_blank_rows": True,
        "blank_line_between_rows": False,
    },
    "invited_international": {
        "columns": ["Date", "Title", "Venue", "Location"],
        "row_format": '“{Title}.” {Venue}, {Location} ({Date})',
        "skip_blank_rows": True,
        "blank_line_between_rows": False,
    },

    # ---- Teaching ----
    "teaching_stanford": {
        "columns": ["Dates", "Description"],
        "row_format": "{Dates}\t{Description}",
        "skip_blank_rows": True,
        "blank_line_between_rows": False,
    },
    "teaching_pre_stanford": {
        "columns": ["Dates", "Description"],
        "row_format": "{Dates}\t{Description}",
        "skip_blank_rows": True,
        "blank_line_between_rows": False,
        # Rows where Dates is empty are sub-headings (Courses / Tutorials /
        # Clinical Supervisory / Research Supervisory). Renderer prefixes them
        # with the SUBHEADING_MARKER; assembler renders those as bold, no indent.
        "subheading_when_dates_empty": True,
    },

    # ---- Trainees ----
    "trainees_postdoc": {
        "columns": ["Dates", "Name", "Role", "Current Position"],
        "row_format": "{Dates}\t{Name}, {Role}. {Current Position}",
        "skip_blank_rows": True,
        "blank_line_between_rows": False,
    },
    "trainees_graduate": {
        "columns": ["Dates", "Name", "Role", "Current Position"],
        "row_format": "{Dates}\t{Name}, {Role}. {Current Position}",
        "skip_blank_rows": True,
        "blank_line_between_rows": False,
    },
    "trainees_med": {
        "columns": ["Dates", "Name", "Role", "Current Position"],
        "row_format": "{Dates}\t{Name}, {Role}. {Current Position}",
        "skip_blank_rows": True,
        "blank_line_between_rows": False,
    },
    "trainees_undergrad": {
        "columns": ["Dates", "Name", "Role", "Current Position"],
        "row_format": "{Dates}\t{Name}, {Role}. {Current Position}",
        "skip_blank_rows": True,
        "blank_line_between_rows": False,
    },
    "trainees_highschool": {
        "columns": ["Dates", "Name", "Role", "Current Position"],
        "row_format": "{Dates}\t{Name}, {Role}. {Current Position}",
        "skip_blank_rows": True,
        "blank_line_between_rows": False,
    },
}


def _tidy(s):
    """Strip dangling-punctuation artifacts left by empty-field substitution.

    Patterns like 'Name, . ' or 'Name. .' arise when a row_format like
    '{Name}, {Role}. {Current Position}' is rendered with Role/Current Position
    empty. We squash them so migrated minimal-data rows still read cleanly.
    """
    import re
    # ", . " or ", ." or ", " at end → "."
    s = re.sub(r",\s*\.\s*$", ".", s.rstrip())
    s = re.sub(r"\.\s*\.\s*$", ".", s)
    s = re.sub(r",\s*$", "", s)
    # ", , " (consecutive empty fields) → ", "
    s = re.sub(r",\s*,", ",", s)
    return s.rstrip()


SUBHEADING_MARKER = "[[H]]"


def render_row(schema, row_dict):
    """Render a single row (dict of column→value) into a list of paragraph strings.

    For a string row_format, returns a 1-element list. For a list of templates,
    returns one string per template. Missing columns are rendered as empty.

    Sub-heading rows (Dates column empty, when section has the
    subheading_when_dates_empty flag) are prefixed with SUBHEADING_MARKER so the
    assembler can render them as bold, indent-free paragraphs.
    """
    safe = {k: (row_dict.get(k, "") or "") for k in schema["columns"]}
    if schema.get("subheading_when_dates_empty") and not safe.get("Dates", "").strip():
        # Sub-heading row — emit just the Description with the marker.
        desc = safe.get("Description", "").strip()
        return [f"{SUBHEADING_MARKER}{desc}"] if desc else []
    fmt = schema["row_format"]
    if isinstance(fmt, str):
        return [_tidy(fmt.format(**safe))]
    return [_tidy(t.format(**safe)) for t in fmt]
