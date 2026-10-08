def _cases():
    return [
        {"id": "a1", "expected": "billing", "text": "t1"},
        {"id": "a2", "expected": "billing", "text": "t2"},
        {"id": "a3", "expected": "cancel", "text": "t3"},
        {"id": "a4", "expected": "cancel", "text": "t4"},
    ]


def _fake_system(text):
    answers = {"t1": " BILLING", "t2": "cancel", "t3": "cancel"}
    if text == "t4":
        raise ConnectionError("reset by peer")
    return answers[text]


def test_wilson_interval():
    """wilson_interval() matches the Wilson formula, rounded to 3 decimals"""
    assert wilson_interval(9, 10) == (0.596, 0.982), f"9/10 should give (0.596, 0.982), got {wilson_interval(9, 10)}"
    assert wilson_interval(45, 50) == (0.786, 0.957), f"45/50 should give (0.786, 0.957), got {wilson_interval(45, 50)}"
    assert wilson_interval(0, 4) == (0.0, 0.49), f"0/4 should give (0.0, 0.49), got {wilson_interval(0, 4)}"
    assert wilson_interval(0, 0) == (0.0, 1.0), "with no scored cases the interval is (0.0, 1.0)"


def test_cases_needed():
    """cases_needed() returns the smallest n for a given margin"""
    assert cases_needed(0.05) == 385, f"+/-5 points at p=0.5 needs 385 cases, got {cases_needed(0.05)}"
    assert cases_needed(0.10) == 97, f"+/-10 points needs 97 cases, got {cases_needed(0.10)}"
    assert cases_needed(0.05, p=0.9) == 139, f"at p=0.9 a +/-5 point margin needs 139 cases, got {cases_needed(0.05, p=0.9)}"
    assert cases_needed(0.03) == 1068, f"+/-3 points needs 1068 cases, got {cases_needed(0.03)}"


def test_run_golden_set_rows():
    """run_golden_set() grades each case and normalizes case and whitespace"""
    rows = run_golden_set(_cases(), _fake_system)
    assert isinstance(rows, list) and len(rows) == 4, f"expected 4 rows, got {rows!r}"
    assert rows[0] == {"id": "a1", "expected": "billing", "actual": " BILLING", "status": "pass", "error": None}, \
        f"' BILLING' should pass after strip() and lower(), and actual keeps the raw output: {rows[0]}"
    assert rows[1]["status"] == "fail" and rows[1]["actual"] == "cancel", f"wrong label is a fail: {rows[1]}"
    assert rows[2]["status"] == "pass", f"got {rows[2]}"


def test_run_golden_set_errors():
    """An exception becomes status "error" and does not stop the run"""
    rows = run_golden_set(_cases(), _fake_system)
    assert rows and rows[3] == {"id": "a4", "expected": "cancel", "actual": None, "status": "error",
                                "error": "ConnectionError: reset by peer"}, f"got {rows[3] if rows else rows}"
    odd = run_golden_set([{"id": "x", "expected": "billing", "text": "t"}], lambda t: None)
    assert odd and odd[0]["status"] == "fail", "a non-string output is the system's answer, so it is a fail, not an error"


def test_summarize_overall():
    """summarize() leaves errors out of the denominator"""
    s = summarize(run_golden_set(_cases(), _fake_system))
    assert s, "summarize returned nothing"
    got = {k: s.get(k) for k in ("n", "passes", "pass_rate", "ci", "errors")}
    assert got == {"n": 3, "passes": 2, "pass_rate": 0.667, "ci": (0.208, 0.939), "errors": 1}, \
        f"3 scored cases (the error is excluded), 2 passes: got {got}"


def test_summarize_by_category():
    """summarize() reports each category with n, rate, interval and a low_n flag"""
    s = summarize(run_golden_set(_cases(), _fake_system), min_n=2)
    assert s and list(s["by_category"]) == ["billing", "cancel"], "categories come from expected labels, sorted"
    assert s["by_category"]["billing"] == {"n": 2, "passes": 1, "pass_rate": 0.5, "ci": (0.095, 0.905), "low_n": False}, \
        f"got {s['by_category']['billing']}"
    assert s["by_category"]["cancel"] == {"n": 1, "passes": 1, "pass_rate": 1.0, "ci": (0.207, 1.0), "low_n": True}, \
        f"cancel has one scored case (the other errored), so n=1 < min_n=2: got {s['by_category']['cancel']}"
    only_err = summarize([{"id": "z", "expected": "roaming", "actual": None, "status": "error", "error": "X: y"}])
    assert only_err["by_category"]["roaming"]["pass_rate"] is None and only_err["pass_rate"] is None, \
        "with no scored cases, pass_rate is None"


def test_traffic_report():
    """traffic_report() weights by traffic and lists coverage gaps by traffic share"""
    summary = {"by_category": {
        "a": {"n": 10, "passes": 9, "pass_rate": 0.9, "ci": (0, 1), "low_n": False},
        "b": {"n": 3, "passes": 1, "pass_rate": 0.333, "ci": (0, 1), "low_n": True},
        "c": {"n": 8, "passes": 4, "pass_rate": 0.5, "ci": (0, 1), "low_n": False},
    }}
    mix = {"a": 0.5, "b": 0.2, "c": 0.2, "d": 0.1}
    got = traffic_report(summary, mix, min_n=5)
    # (0.5*0.9 + 0.2*0.333 + 0.2*0.5) / 0.9 = 0.6851
    assert got == {"weighted_pass_rate": 0.685, "gaps": ["b", "d"], "untested_share": 0.1}, f"got {got}"


def test_kestrel_end_to_end():
    """The Kestrel golden set: 18/23, one error, 0.781 traffic-weighted"""
    s = summarize(run_golden_set(GOLDEN_SET, kestrel_router))
    assert s and (s["n"], s["passes"], s["errors"], s["ci"]) == (23, 18, 1, (0.581, 0.903)), \
        f"got n={s and s['n']}, passes={s and s['passes']}, errors={s and s['errors']}, ci={s and s['ci']}"
    t = traffic_report(s, TRAFFIC_MIX)
    assert t == {"weighted_pass_rate": 0.781,
                 "gaps": ["device_support", "plan_change", "cancel", "roaming", "sim_swap_fraud"],
                 "untested_share": 0.03}, f"got {t}"
