# FACT_SHEET, ROADMAP_PHRASES and HEDGE_WORDS are already defined for you
# (see the lesson). The fact sheet is illustrative: don't hard-code it.

STATUSES = ("comply", "partial", "not_supported", "to_confirm")
EXPECTED = {"yes": "comply", "partial": "partial", "no": "not_supported", "unknown": "to_confirm"}
RANK = {"not_supported": 0, "partial": 1, "comply": 2}


def check_row(row, facts):
    """Return {"id", "expected", "given", "errors", "warnings"} for one answer row."""
    topic = row.get("topic")
    given = row.get("status")
    text = (row.get("text") or "").strip()
    fact = facts.get(topic)
    expected = EXPECTED[fact["status"]] if fact else "to_confirm"
    errors, warnings = [], []

    if given not in STATUSES:
        errors.append(f"status: {given!r} is not one of {', '.join(STATUSES)}")
    elif given != expected:
        if expected == "to_confirm":
            why = "isn't in the fact sheet" if fact is None else "isn't documented"
            errors.append(f"unsourced: {topic} {why}, so the status must be to_confirm, not {given}")
        elif given == "to_confirm":
            warnings.append(f"underclaim: the fact sheet documents {topic} as {expected}; answer it")
        elif RANK[given] > RANK[expected]:
            errors.append(f"overclaim: the fact sheet says {expected}, the answer says {given}")
        else:
            warnings.append(f"underclaim: the fact sheet says {expected}, the answer says {given}")

    lowered = text.lower()
    for phrase in ROADMAP_PHRASES:
        if phrase in lowered:
            errors.append(f"roadmap: the text says '{phrase}'; describe what's available today")

    if given in ("partial", "not_supported") and not text:
        errors.append(f"explain: a {given} answer needs text saying what is and isn't met")
    if given == "to_confirm" and not (row.get("owner") or "").strip():
        errors.append("owner: a to_confirm answer needs an owner")

    if given == "comply":
        for word in HEDGE_WORDS:
            if word in lowered:
                warnings.append(f"hedged: a comply answer says '{word}'; the status is probably partial")

    return {"id": row.get("id"), "expected": expected, "given": given, "errors": errors, "warnings": warnings}


def review(rows, facts):
    """Return {"rows": [...], "error_count", "warning_count", "ready"}."""
    checked = [check_row(r, facts) for r in rows]
    errors = sum(len(r["errors"]) for r in checked)
    warnings = sum(len(r["warnings"]) for r in checked)
    return {"rows": checked, "error_count": errors, "warning_count": warnings, "ready": errors == 0}


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
for r in review(draft, FACT_SHEET)["rows"]:
    print(r["id"], r["expected"], r["given"], r["errors"], r["warnings"])
