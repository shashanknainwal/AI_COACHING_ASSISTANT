import copy

_FACTS = {
    "a": {"status": "yes", "note": "", "source": "docs"},
    "b": {"status": "partial", "note": "", "source": "docs"},
    "c": {"status": "no", "note": "", "source": "docs"},
    "d": {"status": "unknown", "note": "", "source": "legal"},
}


def _row(topic, status, text="Explained.", owner="", id="Q1"):
    return {"id": id, "topic": topic, "status": status, "text": text, "owner": owner}


def _check(row, facts=_FACTS):
    r = check_row(row, facts)
    assert isinstance(r, dict), f"check_row should return a dict, got {r!r}"
    for key in ("id", "expected", "given", "errors", "warnings"):
        assert key in r, f"result is missing {key!r}: {r!r}"
    return r


def _codes(items):
    return [s.split(":", 1)[0] for s in items]


def test_matching_answers_are_clean():
    """An answer whose status matches the fact sheet has no errors or warnings"""
    for topic, status in (("a", "comply"), ("b", "partial"), ("c", "not_supported")):
        r = _check(_row(topic, status))
        assert r["errors"] == [] and r["warnings"] == [], f"{topic}/{status} should be clean: {r!r}"
        assert r["expected"] == status and r["given"] == status, f"expected and given should both be {status}: {r!r}"
    r = _check(_row("d", "to_confirm", owner="Legal, 21 Nov"))
    assert r["errors"] == [] and r["warnings"] == [], f"to_confirm with an owner on an unknown fact is clean: {r!r}"


def test_overclaim_is_an_error():
    """Claiming more than the fact sheet supports is an 'overclaim' error"""
    r = _check(_row("b", "comply"))
    assert _codes(r["errors"]) == ["overclaim"], f"comply on a partial fact is an overclaim: {r['errors']!r}"
    r2 = _check(_row("c", "partial"))
    assert _codes(r2["errors"]) == ["overclaim"], f"partial on a 'no' fact is an overclaim: {r2['errors']!r}"


def test_underclaim_is_a_warning():
    """Claiming less than documented, or to_confirm on a documented fact, is an 'underclaim' warning"""
    r = _check(_row("a", "partial"))
    assert r["errors"] == [] and _codes(r["warnings"]) == ["underclaim"], f"partial on a 'yes' fact: {r!r}"
    r2 = _check(_row("a", "to_confirm", owner="Me"))
    assert r2["errors"] == [] and _codes(r2["warnings"]) == ["underclaim"], f"to_confirm on a documented fact: {r2!r}"


def test_unknown_or_missing_fact_must_be_to_confirm():
    """Unknown facts and topics missing from the sheet must be answered to_confirm"""
    r = _check(_row("d", "comply"))
    assert _codes(r["errors"]) == ["unsourced"] and r["expected"] == "to_confirm", f"comply on an unknown fact: {r!r}"
    r2 = _check(_row("zzz", "not_supported"))
    assert _codes(r2["errors"]) == ["unsourced"], f"a topic not in the sheet must be to_confirm, even a 'no': {r2!r}"
    assert "zzz" in r2["errors"][0], f"the error should name the topic: {r2['errors'][0]!r}"


def test_invalid_status():
    """A status outside the four allowed values is a 'status' error"""
    r = _check(_row("a", "yes"))
    assert _codes(r["errors"])[0] == "status", f"'yes' isn't an allowed status: {r['errors']!r}"


def test_roadmap_language_is_an_error():
    """Each roadmap phrase in the text is a 'roadmap' error, whatever the status"""
    phrases = globals().get("ROADMAP_PHRASES")
    assert phrases, "ROADMAP_PHRASES should be loaded from setup"
    r = _check(_row("c", "not_supported", text="Not today, but it's on the Roadmap and Coming Soon."))
    assert _codes(r["errors"]) == ["roadmap", "roadmap"], f"two roadmap phrases, case-insensitive: {r['errors']!r}"


def test_explanations_and_owners():
    """Partial and not_supported need text; to_confirm needs an owner"""
    r = _check(_row("b", "partial", text="   "))
    assert _codes(r["errors"]) == ["explain"], f"a blank partial answer needs an explanation: {r['errors']!r}"
    r2 = _check(_row("d", "to_confirm", text="", owner=""))
    assert _codes(r2["errors"]) == ["owner"], f"to_confirm with no owner: {r2['errors']!r}"


def test_hedged_comply_is_a_warning():
    """Hedge words in a comply answer are 'hedged' warnings"""
    r = _check(_row("a", "comply", text="Typically met, in most cases."))
    assert r["errors"] == [] and _codes(r["warnings"]) == ["hedged", "hedged"], f"two hedge words: {r!r}"
    r2 = _check(_row("b", "partial", text="Typically met on two platforms."))
    assert r2["warnings"] == [], f"hedge words only matter on comply answers: {r2!r}"


def test_review_totals_and_ready():
    """review() checks every row, counts errors and warnings, and is ready only with zero errors"""
    rows = [_row("a", "comply", id="Q1"), _row("b", "comply", id="Q2"), _row("a", "partial", id="Q3")]
    before = copy.deepcopy(rows)
    out = review(rows, _FACTS)
    assert isinstance(out, dict), f"review should return a dict, got {out!r}"
    assert [r["id"] for r in out["rows"]] == ["Q1", "Q2", "Q3"], "keep rows in their original order"
    assert out["error_count"] == 1 and out["warning_count"] == 1, f"one overclaim, one underclaim: {out!r}"
    assert out["ready"] is False, "a response with errors isn't ready"
    assert rows == before, "review must not modify the rows"
    clean = review([_row("a", "comply")], _FACTS)
    assert clean["ready"] is True and clean["error_count"] == 0, f"a clean response is ready: {clean!r}"
