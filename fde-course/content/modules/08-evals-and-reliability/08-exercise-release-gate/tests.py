def _rows(spec):
    """spec: list of (id, category, passed)."""
    return [{"id": i, "category": c, "pass": p} for i, c, p in spec]


def test_wilson_interval():
    """wilson_interval() matches the Wilson score formula"""
    assert wilson_interval(14, 20) == (0.481, 0.855), f"got {wilson_interval(14, 20)}"
    assert wilson_interval(15, 20) == (0.531, 0.888)
    assert wilson_interval(90, 100) == (0.826, 0.945)
    assert wilson_interval(20, 20) == (0.839, 1.0), "the interval stays inside [0, 1] even at 100%"
    assert wilson_interval(0, 10) == (0.0, 0.278)
    assert wilson_interval(0, 0) == (0.0, 1.0), "with no data, anything is possible"


def test_interval_narrows_with_more_cases():
    """The same pass rate is more certain with more cases"""
    small, big = wilson_interval(7, 10), wilson_interval(700, 1000)
    assert (small[1] - small[0]) > 5 * (big[1] - big[0])


def test_diff_runs():
    """diff_runs() lists regressions and fixes in candidate order"""
    got = diff_runs(BASELINE, CANDIDATE)
    assert got == {"regressions": ["T-03", "T-05"], "fixes": ["T-12", "T-13", "T-17"]}, f"got {got}"
    base = _rows([("a", "x", True), ("b", "x", False)])
    cand = _rows([("b", "x", True), ("c", "x", False), ("a", "x", False)])
    assert diff_runs(base, cand) == {"regressions": ["a"], "fixes": ["b"]}, "ignore cases missing from the baseline"


def test_gate_blocks_the_candidate():
    """The candidate scores higher but must not ship"""
    got = gate(BASELINE, CANDIDATE, MUST_PASS, CRITICAL_CATEGORIES)
    assert got == {"ship": False, "reasons": ["must-pass case T-07 failed",
                                              "regression in critical category damaged_item: T-05"]}, f"got {got}"


def test_gate_rules():
    """Each rule works on its own, in order, and a clean candidate ships"""
    base = _rows([("a", "billing", True), ("b", "billing", True), ("c", "fraud", True), ("d", "other", False)])
    clean = _rows([("a", "billing", True), ("b", "billing", True), ("c", "fraud", True), ("d", "other", True)])
    assert gate(base, clean, ["c"], ["fraud"]) == {"ship": True, "reasons": []}
    worse = _rows([("a", "billing", False), ("b", "billing", True), ("c", "fraud", False), ("d", "other", False)])
    got = gate(base, worse, ["c", "zz"], ["fraud"])
    assert got == {"ship": False, "reasons": ["must-pass case c failed", "must-pass case zz failed",
                                              "pass rate dropped from 0.750 to 0.250",
                                              "regression in critical category fraud: c"]}, f"got {got}"


def test_gate_tolerance():
    """Small drops within the tolerance don't block a release"""
    base = _rows([(str(i), "x", i < 90) for i in range(100)])          # 0.90
    cand = _rows([(str(i), "x", i < 89) for i in range(100)])          # 0.89
    assert gate(base, cand, [], [])["ship"] is True, "a 0.01 drop is within the default 0.02 tolerance"
    assert gate(base, cand, [], [], tolerance=0.005)["reasons"] == ["pass rate dropped from 0.900 to 0.890"]


def test_consistency():
    """consistency() separates pass@k from pass^k and lists flaky cases"""
    got = consistency(AGENT_TRIALS)
    assert got == {"pass_at_k": 0.8, "pass_all_k": 0.4, "flaky": ["A-2", "A-4"]}, f"got {got}"
    assert consistency({"x": [True, True], "y": [True, True]}) == {"pass_at_k": 1.0, "pass_all_k": 1.0, "flaky": []}
