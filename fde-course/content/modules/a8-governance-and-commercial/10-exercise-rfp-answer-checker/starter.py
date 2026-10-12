# FACT_SHEET, ROADMAP_PHRASES and HEDGE_WORDS are already defined for you
# (see the lesson). The fact sheet is illustrative: don't hard-code it.

STATUSES = ("comply", "partial", "not_supported", "to_confirm")
EXPECTED = {"yes": "comply", "partial": "partial", "no": "not_supported", "unknown": "to_confirm"}


def check_row(row, facts):
    """Return {"id", "expected", "given", "errors", "warnings"} for one answer row."""
    # TODO
    pass


def review(rows, facts):
    """Return {"rows": [...], "error_count", "warning_count", "ready"}."""
    # TODO
    pass


# --- Try it out (this part isn't graded) ---
draft = [
    {"id": "Q1", "topic": "us_only_inference", "status": "comply",
     "text": "Set inference_geo to 'us'; priced at 1.1x.", "owner": ""},
    {"id": "Q2", "topic": "eu_only_inference", "status": "comply",
     "text": "Generally yes, and an EU option for the Claude API is on the roadmap.", "owner": ""},
    {"id": "Q3", "topic": "uptime_sla_with_credits", "status": "comply",
     "text": "99.5% uptime.", "owner": ""},
    {"id": "Q4", "topic": "fine_tuning", "status": "partial", "text": "", "owner": ""},
]
print(review(draft, FACT_SHEET))
