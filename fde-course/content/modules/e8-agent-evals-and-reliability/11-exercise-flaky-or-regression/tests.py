import copy

P, F, E = "pass", "fail", "error"


def test_rerun_policy():
    """rerun_policy() reruns regressions first and stops at the budget"""
    flips = {"regressions": ["r1", "r2", "r3"], "fixes": ["f1", "f2"], "missing": []}
    got = rerun_policy(flips, 5, 45)
    assert got == {"rerun": ["r1", "r2", "r3", "f1"], "calls": 40, "skipped": ["f2"]}, \
        f"each case costs 2 x k calls (both versions); regressions first: got {got}"
    assert rerun_policy(flips, 3, 10) == {"rerun": ["r1"], "calls": 6, "skipped": ["r2", "r3", "f1", "f2"]}


def test_case_rate_and_classify():
    """classify() separates regressions, fixes, flaky and stable cases"""
    assert case_rate([P, F, E, P]) == (2, 3), "errors are not trials"
    assert classify([P] * 5, [F, F, F, F, P]) == "regression"
    assert classify([F, P, F, F, P], [P] * 5) == "fix", "0.4 to 1.0 is a fix"
    assert classify([P, F, P, F, P], [F, P, F, P, F]) == "flaky", "0.6 to 0.4 is noise, not a regression"
    assert classify([P] * 5, [P] * 5) == "stable" and classify([F] * 5, [F] * 5) == "stable"
    assert classify([P] * 5, [F, F, F, E, F]) == "regression"
    assert classify([E, E], [P]) == "unknown"


def test_observations_and_clustered_rate():
    """clustered_rate() widens the SE when reruns pile observations on a few cases"""
    first = [{"id": "a", "category": "x", "status": P}, {"id": "b", "category": "x", "status": F},
             {"id": "c", "category": "x", "status": P}]
    obs = observations(first, {"b": {"candidate": [F, F, E, F]}}, "candidate")
    assert obs == {"a": [1], "b": [0, 0, 0, 0], "c": [1]}, f"first run plus reruns, errors dropped: got {obs}"
    got = clustered_rate({"a": [1, 1, 1], "b": [0, 0, 0], "c": [1, 1, 0], "d": [1, 1, 1]})
    assert got == {"rate": 0.667, "n_obs": 12, "n_cases": 4, "se_naive": 0.1361, "se_clustered": 0.2357, "design_effect": 3.0}, f"got {got}"


def test_paired_difference():
    """paired_difference() averages each case first, then uses the case-level spread"""
    base = {"a": [1, 1], "b": [1, 0], "c": [0], "d": [1], "e": []}
    cand = {"a": [1, 0], "b": [1, 1], "c": [0, 0, 1, 1], "d": [1], "e": [1]}
    got = paired_difference(base, cand)
    assert got == {"n": 4, "diff": 0.125, "se": 0.2394, "low": -0.637, "high": 0.887}, \
        f"d = (-0.5, +0.5, +0.5, 0); skip cases with no scored baseline trials: got {got}"


def test_verdict_on_gannet():
    """verdict() blocks on the critical regression even though the average barely moved"""
    reruns = copy.deepcopy(RERUNS)
    v = verdict(BASELINE_RUN, CANDIDATE_RUN, reruns, CONFIG)
    assert v, "verdict() returned nothing"
    assert v["decision"] == "block" and v["calls"] == 80
    assert v["reasons"] == [
        {"code": "regression", "severity": "review", "detail": "CRE-02 (credit): baseline 5/5, candidate 1/5 on rerun"},
        {"code": "critical_regression", "severity": "block", "detail": "VUL-05 (vulnerable): baseline 5/5, candidate 0/4 on rerun"},
    ], f"got {v['reasons']}"
    assert v["confirmed_regressions"] == ["CRE-02", "VUL-05"] and v["confirmed_fixes"] == ["CRE-07", "TAR-06"]
    assert v["flaky"] == ["BIL-01", "TAR-04", "VUL-08"], f"got {v['flaky']}"
    d = v["difference"]
    assert d["n"] == 40 and abs(d["diff"] + 0.0125) < 0.001 and (d["se"], d["low"], d["high"]) == (0.0483, -0.107, 0.082), \
        f"got {d}"
    assert reruns == RERUNS


def test_verdict_budget_and_ship():
    """A regression the budget couldn't rerun needs review; a clean candidate ships"""
    v = verdict(BASELINE_RUN, CANDIDATE_RUN, RERUNS, dict(CONFIG, max_calls=30))
    assert v and v["reasons"][-1] == {"code": "not_rerun", "severity": "review",
                                      "detail": "regressions not rerun within budget: TAR-04, VUL-05"}, f"got {v and v['reasons']}"
    assert v["decision"] == "review", "the regression it did rerun (CRE-02) isn't critical"
    same = verdict(BASELINE_RUN, [dict(r) for r in BASELINE_RUN], {}, CONFIG)
    assert same["decision"] == "ship" and same["reasons"] == [] and same["difference"]["diff"] == 0.0
