import copy


def test_normalize():
    """normalize() lowercases, straightens apostrophes and drops punctuation"""
    assert normalize("Didn’t verify identity!!") == "didn't verify identity", f"got {normalize('Didn’t verify identity!!')!r}"
    assert normalize("  Over-credited   (applied twice) ") == "over-credited applied twice"
    assert normalize("Invalid argument: tariff='fixed'") == "invalid argument tariff'fixed'"


def test_categorize():
    """categorize() uses the first matching codebook category"""
    assert categorize("Didn’t verify identity before changing tariff") == "identity_skipped", \
        "the curly apostrophe must still match \"didn't verify\""
    assert categorize("Booking NOT SAVED but told customer it was") == "false_completion"
    assert categorize("Vulnerable customer said done twice") == "missed_escalation", "codebook order decides ties"
    assert categorize("Greeting fine, picked the right intent") is None


def test_root_cause_uses_earliest_matching_step():
    """root_cause() attributes the failure to the earliest categorized note"""
    f = {"id": "X", "notes": [{"step": 6, "note": "Said done, reading not saved"},
                              {"step": 1, "note": "Greeting fine"},
                              {"step": 3, "note": "Bad date format (03/11) to book_engineer"}]}
    assert root_cause(f) == ("tool_args_error", ["false_completion"]), \
        f"sort by step; skip notes that match nothing; later categories are downstream: got {root_cause(f)}"
    assert root_cause({"id": "Y", "notes": [{"step": 2, "note": "Answered in Welsh"}]}) == ("uncategorized", [])


def test_rank_by_impact():
    """rank() orders categories by count x cost and adds a cumulative share"""
    tax = {"by_root": {"a": ["1", "2", "3", "4"], "b": ["5"], "c": ["6", "7"], "uncategorized": ["8"]}, "downstream": {}}
    got = rank(tax, {"a": 10, "b": 100, "c": 20}, 8)
    assert got == [
        {"category": "b", "count": 1, "share": 0.125, "cost_each": 100, "impact": 100, "cumulative_impact_share": 0.556},
        {"category": "a", "count": 4, "share": 0.5, "cost_each": 10, "impact": 40, "cumulative_impact_share": 0.778},
        {"category": "c", "count": 2, "share": 0.25, "cost_each": 20, "impact": 40, "cumulative_impact_share": 1.0},
    ], f"impact desc, ties by name, uncategorized left out: got {got}"


def test_analyze_gannet():
    """analyze() on the 60 Gannet failures ranks by impact, not frequency"""
    data = copy.deepcopy(FAILURES)
    a = analyze(data)
    assert a, "analyze() returned nothing"
    order = [(r["category"], r["count"], r["impact"]) for r in a["ranked"]]
    assert order == [("missed_escalation", 5, 1100), ("identity_skipped", 6, 900), ("false_completion", 14, 490),
                     ("wrong_credit_amount", 8, 480), ("wrong_tariff_info", 12, 300), ("tool_args_error", 7, 84),
                     ("looping", 4, 32), ("tone", 2, 10)], \
        f"counts are root causes only; downstream notes don't add to them: got {order}"
    assert a["most_frequent"] == "false_completion"
    assert a["uncategorized"] == ["F-35", "F-48"] and a["uncategorized_share"] == 0.033 and a["codebook_saturated"] is True
    assert a["downstream"] == {"false_completion": 4, "wrong_credit_amount": 3}, f"got {a['downstream']}"
    assert data == FAILURES, "don't modify the failures"


def test_fixes_for_top_two():
    """propose_fixes() pairs each top category with a fix, an eval and example traces"""
    a = analyze(FAILURES)
    fx = a and a["fixes"]
    assert fx and [f["category"] for f in fx] == ["missed_escalation", "identity_skipped"], f"got {fx}"
    assert fx[0]["examples"] == ["F-04", "F-12", "F-25"] and fx[1]["examples"] == ["F-07", "F-20", "F-33"], \
        "first three trace ids of each category, in FAILURES order"
    assert fx[1]["layer"] == "tool code" and fx[0]["eval"] == FIX_LIBRARY["missed_escalation"]["eval"]
    assert fx[0]["impact"] == 1100


def test_saturation_flag():
    """A codebook that leaves more than 10% uncategorized is not saturated"""
    extra = [{"id": f"N-{i}", "notes": [{"step": 2, "note": "Answered in Welsh"}]} for i in range(6)]
    a = analyze(FAILURES + extra)
    assert a and a["uncategorized_share"] == 0.121 and a["codebook_saturated"] is False, \
        f"8 of 66 uncategorized: read more traces and extend the codebook; got {a and a['uncategorized_share']}"
