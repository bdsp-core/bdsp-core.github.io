"""Section definitions: maps each CV section to its header anchor and styling.

Header prefixes are matched against paragraph text after stripping. Templates with
{count} placeholders are filled at build time. Each section's text file in
cache/sections/ contains one paragraph per line (blank lines preserved verbatim).
"""

SECTIONS = [
    # (key, header_prefix, header_template, default_style, source)
    ("identifying_data",            "Identifying Data",                          "Identifying Data",                                                              "Normal",            "gdoc"),
    ("colleges",                    "Colleges and Universities Attended",        "Colleges and Universities Attended",                                            "Normal",            "gdoc"),
    ("residency_fellowship",        "Residency and Fellowship Training",         "Residency and Fellowship Training",                                             "Normal",            "gdoc"),
    ("board_certification",         "Board Certification",                       "Board Certification",                                                           "Normal",            "gdoc"),
    ("academic_appointments",       "Academic Appointments:",                    "Academic Appointments:",                                                        "Normal",            "gdoc"),
    ("other_appointments",          "Other Appointments:",                       "Other Appointments:",                                                           "Normal",            "gdoc"),
    ("honors_awards",               "Honors and Awards",                         "Honors and Awards",                                                             "Normal",            "gdoc"),
    ("peer_reviewed_original",      "Peer-reviewed original research",           "Peer-reviewed original research ({count} total)",                               "List Paragraph",    "ncbi"),
    ("peer_reviewed_in_press",      "Peer-reviewed publications (accepted",      "Peer-reviewed publications (accepted, in press)",                               "Normal",            "gdoc"),
    ("peer_reviewed_other",         "Peer-reviewed publications (other",         "Peer-reviewed publications (other - {count} total)",                            "Normal",            "gdoc"),
    ("non_peer_reviewed_articles",  "Non-Peer-reviewed Articles",                "Non-Peer-reviewed Articles",                                                    "Normal",            "gdoc"),
    ("book_chapters",               "Book Chapters",                             "Book Chapters",                                                                 "Normal",            "gdoc"),
    ("grants_current",              "Current:",                                  "Current:",                                                                      "Normal",            "gdoc"),
    ("grants_submitted",            "Submitted:",                                "Submitted:",                                                                    "Normal",            "gdoc"),
    ("grants_completed",            "Completed:",                                "Completed:",                                                                    "Normal",            "gdoc"),
    ("editorial_service",           "Editorial Service",                         "Editorial Service",                                                             "Normal",            "gdoc"),
    ("ad_hoc_reviewer",             "Ad Hoc Reviewer",                           "Ad Hoc Reviewer",                                                               "Normal",            "gdoc"),
    ("grant_reviewer",              "Service as Grant Reviewer",                 "Service as Grant Reviewer",                                                     "Normal",            "gdoc"),
    ("university_admin_service",    "University Administrative Service",         "University Administrative Service",                                             "Normal",            "gdoc"),
    ("service_professional_orgs",   "Service to Professional Organizations",     "Service to Professional Organizations",                                         "Normal",            "gdoc"),
    ("community_service",           "Community Service",                         "Community Service",                                                             "Body Text Indent 2","gdoc"),
    ("invited_grand_rounds",        "Grand Rounds:",                             "Grand Rounds:",                                                                 "Normal",            "gdoc"),
    ("invited_local",               "Local Invited Presentations:",              "Local Invited Presentations:",                                                  "List Paragraph",    "gdoc"),
    ("invited_national",            "National and Regional Meetings:",           "National and Regional Meetings:",                                               "List Paragraph",    "gdoc"),
    ("invited_international",       "International Meetings:",                   "International Meetings:",                                                       "List Paragraph",    "gdoc"),
    ("teaching_stanford",           "Teaching during Stanford appointment:",     "Teaching during Stanford appointment:",                                         "Normal",            "gdoc"),
    ("teaching_pre_stanford",       "Teaching prior to Stanford:",               "Teaching prior to Stanford:",                                                   "Normal",            "gdoc"),
    ("trainees_postdoc",            "Postdoctoral Fellows",                      "Postdoctoral Fellows",                                                          "Normal",            "gdoc"),
    ("trainees_graduate",           "Graduate Students",                         "Graduate Students",                                                             "Normal",            "gdoc"),
    ("trainees_med",                "Medical Students / Residents / Fellows",    "Medical Students / Residents / Fellows",                                        "Normal",            "gdoc"),
    ("trainees_undergrad",          "Undergraduate Students",                    "Undergraduate Students",                                                        "Normal",            "gdoc"),
    ("trainees_highschool",         "High School Students",                      "High School Students",                                                          "Normal",            "gdoc"),
]

# Parent / container headers that have no direct content (just visual section breaks).
# We never touch the paragraphs between these and their next anchor.
PARENT_HEADERS = [
    "Education History",
    "Employment",
    "Bibliography",
    "Grant Funding",
    "Professional Activities",
    "Invited Presentations",
    "Teaching",
    "Trainees",
]
