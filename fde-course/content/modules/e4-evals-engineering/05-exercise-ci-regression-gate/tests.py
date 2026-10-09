def _row(i, cat, status):
    return {"id": i, "category": cat, "status": status}


_CFG = {"category_floors": {}, "max_category_drop": 0.10, "min_category_n": 3, "max_error_rate": 0.05, "alpha": 0.05}


def test_pass_rates():
    """pass_rates() scores only non-error rows and keeps error-only categories"""
    rows = [_row("a", "x", "pass"), _row("b", "x", "fail"), _row("c", "x", "pass"), _row("d", "y", "error")]
    got = pass_rates(rows)
    assert got == {"total": 4, "errors": 1, "overall": {"n": 3, "passes": 2, "rate": 0.667},
                   "by_category": {"x": {"n": 3, "passes": 2, "rate": 0.667}, "y": {"n": 0, "passes": 0, "rate": None}}}, \
        f"got {got}"


def test_paired_flips():
    """paired_flips() lists regressions, fixes and missing IDs in baseline order"""
    base = [_row("a", "x", "pass"), _row("b", "x", "fail"), _row("c", "x", "pass"), _row("d", "x", "pass"), _row("e", "x", "fail")]
    cand = [_row("e", "x", "pass"), _row("c", "x", "fail"), _row("a", "x", "fail"), _row("b", "x", "error")]
    got = paired_flips(base, cand)
    assert got == {"regressions": ["a", "c"], "fixes": ["e"], "missing": ["d"]}, \
        f"error rows are not flips, and order follows the baseline: got {got}"


def test_sign_test_p():
    """sign_test_p() is the one-sided exact binomial tail"""
    assert sign_test_p(6, 0) == 0.0156, f"6 regressions, 0 fixes: 1/64 = 0.0156, got {sign_test_p(6, 0)}"
    assert sign_test_p(4, 0) == 0.0625, f"4 regressions, 0 fixes: 1/16 = 0.0625, got {sign_test_p(4, 0)}"
    assert sign_test_p(7, 2) == 0.0898, f"P(X >= 7 | n=9) = 46/512 = 0.0898, got {sign_test_p(7, 2)}"
    assert sign_test_p(2, 5) == 0.9375, f"P(X >= 2 | n=7) = 120/128 = 0.9375, got {sign_test_p(2, 5)}"
    assert sign_test_p(0, 0) == 1.0, "no discordant pairs means no evidence of change: 1.0"


def test_gate_ship():
    """A clean candidate ships with no reasons"""
    base = [_row(f"k{i}", "x", "pass") for i in range(4)]
    got = gate(base, [dict(r) for r in base], _CFG)
    assert got == {"decision": "ship", "reasons": [], "p_value": 1.0}, f"got {got}"


def test_gate_run_health():
    """Missing cases and a high error rate block before anything else"""
    base = [_row(f"k{i}", "x", "pass") for i in range(10)]
    cand = [_row(f"k{i}", "x", "error" if i == 0 else "pass") for i in range(9)]
    got = gate(base, cand, _CFG)
    assert got and got["decision"] == "block", f"got {got}"
    assert got["reasons"][:2] == [
        {"code": "incomplete_run", "severity": "block", "detail": "1 baseline cases missing from candidate: k9"},
        {"code": "error_rate", "severity": "block", "detail": "candidate error rate 0.111 above 0.050"},
    ], f"got {got['reasons']}"


def test_gate_floor_and_drop():
    """Floors block; a drop blocks with enough cases and needs review with too few"""
    base = [_row("a1", "big", "pass"), _row("a2", "big", "pass"), _row("a3", "big", "pass"),
            _row("s1", "small", "pass"), _row("s2", "small", "pass")]
    cand = [_row("a1", "big", "pass"), _row("a2", "big", "pass"), _row("a3", "big", "fail"),
            _row("s1", "small", "pass"), _row("s2", "small", "fail")]
    cfg = dict(_CFG, category_floors={"small": 0.9, "zzz": 0.5})
    got = gate(base, cand, cfg)
    assert got and got["reasons"] == [
        {"code": "below_floor", "severity": "block", "detail": "small pass rate 0.500 below floor 0.900"},
        {"code": "no_data", "severity": "block", "detail": "zzz has no scored cases in the candidate run"},
        {"code": "category_drop", "severity": "block", "detail": "big dropped 1.000 -> 0.667 (n=3)"},
        {"code": "category_drop", "severity": "review", "detail": "small dropped 1.000 -> 0.500 (n=2)"},
        {"code": "net_regression", "severity": "review", "detail": "2 regressions vs 0 fixes (sign test p=0.2500)"},
    ], f"got {got and got['reasons']}"
    assert got["decision"] == "block" and got["p_value"] == 0.25


def test_gate_significant_regression():
    """Many more regressions than fixes is a block on its own"""
    base = [_row(f"k{i}", "x", "pass") for i in range(40)]
    cand = [_row(f"k{i}", "x", "fail" if i < 6 else "pass") for i in range(40)]
    cfg = dict(_CFG, max_category_drop=0.2)
    got = gate(base, cand, cfg)
    assert got and got["reasons"] == [{"code": "significant_regression", "severity": "block",
                                       "detail": "6 regressions vs 0 fixes (sign test p=0.0156)"}], f"got {got}"
    assert got["decision"] == "block"


def test_gate_kestrel():
    """Kestrel v4: the headline rises to 0.872, yet the gate blocks it"""
    assert pass_rates(CANDIDATE_RUN)["overall"]["rate"] == 0.872
    got = gate(BASELINE_RUN, CANDIDATE_RUN, GATE_CONFIG)
    assert got == {"decision": "block", "p_value": 0.9375, "reasons": [
        {"code": "below_floor", "severity": "block", "detail": "cancel pass rate 0.750 below floor 1.000"},
        {"code": "category_drop", "severity": "review", "detail": "cancel dropped 1.000 -> 0.750 (n=4)"},
        {"code": "category_drop", "severity": "review", "detail": "roaming dropped 0.667 -> 0.333 (n=3)"},
    ]}, f"got {got}"
