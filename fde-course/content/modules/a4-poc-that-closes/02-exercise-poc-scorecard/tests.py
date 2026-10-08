def _crit(metric, threshold, direction="higher", must_have=True, baseline=0, **extra):
    c = {"metric": metric, "threshold": threshold, "direction": direction, "must_have": must_have, "baseline": baseline}
    c.update(extra)
    return c


def test_validate_good_criteria():
    """validate_criteria() returns an empty list for the agreed Halvorsen criteria"""
    got = validate_criteria(CRITERIA)
    assert got == [], f"Halvorsen's criteria are complete, so expect [], got {got!r}"


def test_validate_finds_problems():
    """validate_criteria() names each problem, in order, and flags a plan with no must-have"""
    bad = [
        {"metric": "accuracy", "threshold": 0.9, "direction": "up", "must_have": False, "baseline": 0.8},
        {"metric": "", "threshold": 1, "direction": "lower", "must_have": False, "baseline": 0},
        {"metric": "latency_s", "threshold": "fast", "direction": "lower", "must_have": False},
        {"metric": "accuracy", "threshold": 0.95, "direction": "higher", "must_have": False, "baseline": None},
    ]
    got = validate_criteria(bad)
    expected = [
        "accuracy: direction must be 'higher' or 'lower'",
        "criterion 2: missing metric name",
        "latency_s: threshold must be a number",
        "latency_s: no baseline agreed",
        "accuracy: duplicate metric",
        "accuracy: no baseline agreed",
        "no must-have criterion",
    ]
    assert got == expected, f"expected\n{expected}\ngot\n{got}"
    assert validate_criteria([_crit("x", True)]) == ["x: threshold must be a number"], \
        "True is a bool, not a threshold: treat bools as not-a-number"


def test_evaluate_met_and_missed():
    """evaluate_criterion() handles both directions outside the borderline band"""
    r = evaluate_criterion(_crit("acc", 0.90, baseline=0.85), {"acc": 0.95})
    assert r and r["status"] == "met", f"0.95 >= 0.90 is met: {r}"
    assert r == {"metric": "acc", "status": "met", "measured": 0.95, "threshold": 0.90, "direction": "higher",
                 "must_have": True, "vs_baseline": 0.1}, f"row shape or vs_baseline wrong: {r}"
    r = evaluate_criterion(_crit("acc", 0.90), {"acc": 0.80})
    assert r["status"] == "missed", f"0.80 < 0.90 is missed: {r}"
    r = evaluate_criterion(_crit("lat", 10, "lower"), {"lat": 7})
    assert r["status"] == "met", f"for 'lower', 7 <= 10 is met: {r}"
    r = evaluate_criterion(_crit("lat", 10, "lower"), {"lat": 12})
    assert r["status"] == "missed", f"for 'lower', 12 > 10 is missed: {r}"


def test_evaluate_borderline():
    """Results within margin x |threshold| of the target are borderline, on either side"""
    c = _crit("acc", 0.90)
    assert evaluate_criterion(c, {"acc": 0.89})["status"] == "borderline", "0.89 is within 0.018 of 0.90: borderline"
    assert evaluate_criterion(c, {"acc": 0.91})["status"] == "borderline", "a just-met result is borderline too"
    assert evaluate_criterion(c, {"acc": 0.87})["status"] == "missed", "0.87 is 0.03 below 0.90: outside the band"
    assert evaluate_criterion(c, {"acc": 0.87}, margin=0.05)["status"] == "borderline", "the margin argument widens the band"
    c2 = _crit("acc", 0.90, margin=0.0)
    assert evaluate_criterion(c2, {"acc": 0.899})["status"] == "missed", "a per-criterion 'margin' overrides the default"


def test_zero_threshold_has_no_band():
    """A zero-tolerance criterion (threshold 0) is never borderline"""
    c = _crit("pii_leaks", 0, "lower")
    assert evaluate_criterion(c, {"pii_leaks": 0})["status"] == "met", "0 leaks against <= 0 is met"
    assert evaluate_criterion(c, {"pii_leaks": 1})["status"] == "missed", "1 leak against <= 0 is missed, not borderline"


def test_not_measured():
    """A missing (or non-numeric) measurement is not_measured, never met"""
    r = evaluate_criterion(_crit("hours", 120, baseline=0), {})
    assert r and r["status"] == "not_measured" and r["measured"] is None and r["vs_baseline"] is None, f"got {r}"
    r = evaluate_criterion(_crit("hours", 120), {"hours": None})
    assert r["status"] == "not_measured", f"None is not a measurement: {r}"
    r = evaluate_criterion(_crit("hours", 120), {"hours": "TBD"})
    assert r["status"] == "not_measured" and r["measured"] is None, f"'TBD' is not a measurement: {r}"


def test_readout_decisions():
    """poc_readout() applies the decision rules in order: no-go, incomplete, conditional, go"""
    crit = [_crit("a", 0.9), _crit("b", 10, "lower"), _crit("c", 0.5, must_have=False)]
    go = poc_readout(crit, {"a": 0.95, "b": 5, "c": 0.2})
    assert go and go["decision"] == "go", f"all must-haves met: go (a missed nice-to-have doesn't block). Got {go and go['decision']}"
    assert go["watch"] == ["c"] and go["blocking"] == [], f"the missed nice-to-have goes on the watch list: {go}"
    cond = poc_readout(crit, {"a": 0.91, "b": 5, "c": 0.6})
    assert cond["decision"] == "conditional", f"a borderline must-have: conditional. Got {cond['decision']}"
    inc = poc_readout(crit, {"a": 0.95, "c": 0.6})
    assert inc["decision"] == "incomplete" and inc["blocking"] == ["b"], f"an unmeasured must-have: incomplete. Got {inc}"
    nogo = poc_readout(crit, {"a": 0.5, "c": 0.6})
    assert nogo["decision"] == "no-go" and nogo["blocking"] == ["a", "b"], \
        f"a missed must-have is a no-go even if another is unmeasured; both block. Got {nogo}"


def test_halvorsen_readout():
    """Halvorsen week 6: conditional, three items to watch, the demo score left unscored"""
    r = poc_readout(CRITERIA, RESULTS)
    assert r, "poc_readout returned nothing"
    statuses = [row["status"] for row in r["rows"]]
    assert statuses == ["borderline", "met", "met", "missed", "met", "not_measured"], f"got {statuses}"
    assert r["decision"] == "conditional", f"field accuracy 0.948 is inside the band around 0.95: got {r['decision']}"
    assert r["blocking"] == [], f"got {r['blocking']}"
    assert r["watch"] == ["field_accuracy", "straight_through_rate", "adjuster_hours_saved_per_week"], f"got {r['watch']}"
    assert r["unscored"] == ["demo_feedback_score"], \
        f"metrics nobody agreed to up front are listed, not scored: got {r['unscored']}"
    assert r["rows"][0]["vs_baseline"] == 0.018, f"0.948 - 0.93 = 0.018: got {r['rows'][0]['vs_baseline']}"
