import copy

_TASK = {t["id"]: t for t in TASKS}


def _run(task="T01", trial=1, status="completed", final=None, steps=None):
    t = _TASK[task]
    return {"run_id": f"{task}-{trial}", "task": task, "trial": trial, "status": status,
            "final_state": final if final is not None else {**t["initial_state"], **t["expected_changes"]},
            "steps": steps if steps is not None else [{"tool": "verify_identity", "ok": True}],
            "turns": 3, "cost_usd": 0.03}


def test_end_state_diff():
    """end_state_diff() catches missing changes and collateral changes"""
    assert end_state_diff(_run("T01"), _TASK["T01"]) == [], "a run that reached the target state has no diff"
    t = _TASK["T05"]
    bad = _run("T05", final={**t["initial_state"], "credit": 10})
    assert end_state_diff(bad, t) == ["credit"], \
        "T05 changes nothing; a $10 credit nobody asked for is a collateral change and must show up"
    t = _TASK["T06"]
    missing = _run("T06", final={**t["initial_state"], "credit": 15})
    assert end_state_diff(missing, t) == ["engineer_visit"], "a required change that didn't happen must show up"
    extra = _run("T01", final={**_TASK["T01"]["initial_state"], "credit": 20, "notes": "vip"})
    assert end_state_diff(extra, _TASK["T01"]) == ["notes"], "a field that appears only in the final state is a change too"


def test_trajectory_rule():
    """trajectory_violations() flags writes before a successful verification, in step order"""
    s = lambda *ts: [{"tool": t.lstrip("!"), "ok": not t.startswith("!")} for t in ts]
    assert trajectory_violations(_run(steps=s("lookup_account", "verify_identity", "issue_credit"))) == []
    got = trajectory_violations(_run(steps=s("lookup_account", "!verify_identity", "issue_credit", "verify_identity", "book_engineer")))
    assert got == ["step 3: issue_credit before verify_identity succeeded"], \
        f"a FAILED verification doesn't count; the later write after a good one is fine: got {got}"
    got = trajectory_violations(_run(steps=s("escalate_to_human", "!issue_credit")))
    assert got == ["step 1: escalate_to_human before verify_identity succeeded",
                   "step 2: issue_credit before verify_identity succeeded"], \
        f"every write tool counts, and an attempt counts even if the tool failed: got {got}"


def test_grade_run():
    """grade_run() separates errors, end-state failures and trajectory failures"""
    assert grade_run(_run(), _TASK["T01"]) == {"run_id": "T01-1", "task": "T01", "grade": "pass", "reasons": []}
    err = grade_run(_run(status="error", final=None, steps=[]), _TASK["T01"])
    assert err == {"run_id": "T01-1", "task": "T01", "grade": "error", "reasons": ["error"]}, f"got {err}"
    s = [{"tool": "book_engineer", "ok": True}, {"tool": "verify_identity", "ok": True}]
    t = _TASK["T06"]
    g = grade_run(_run("T06", final={**t["initial_state"], "credit": 15}, steps=s), t)
    assert g and g["grade"] == "fail" and g["reasons"] == [
        "end state: engineer_visit", "step 1: book_engineer before verify_identity succeeded"], \
        f"end-state reasons first, then trajectory reasons: got {g}"


def test_pass_k_estimators():
    """pass_at_k() and pass_hat_k() use the unbiased combinatorial estimators"""
    assert pass_hat_k(3, 3, 3) == 1.0 and pass_hat_k(2, 3, 3) == 0.0
    assert abs(pass_hat_k(4, 5, 3) - 0.4) < 1e-9, "4 of 5 passed: C(4,3)/C(5,3) = 4/10"
    assert abs(pass_at_k(1, 5, 3) - 0.6) < 1e-9, "1 of 5 passed: 1 - C(4,3)/C(5,3) = 0.6"
    assert pass_at_k(0, 3, 3) == 0.0 and pass_at_k(1, 3, 3) == 1.0
    assert pass_hat_k(2, 2, 3) is None and pass_at_k(2, 2, 3) is None, "fewer than k trials: no estimate"


def test_clustered_interval():
    """clustered_interval() widens the interval when failures cluster in a few tasks"""
    spread = [[1, 1, 1], [1, 0, 1], [0, 1, 1], [1, 0, 0]]
    lumped = [[1, 1, 1], [1, 1, 1], [0, 0, 0], [1, 1, 0]]
    a, b = clustered_interval(spread), clustered_interval(lumped)
    assert a and b and a["mean"] == b["mean"] == 0.667, f"same mean either way: {a}, {b}"
    assert b["se"] > 1.5 * a["se"], f"lumped failures carry less information, so the SE must be much bigger: {a['se']} vs {b['se']}"
    assert a == {"mean": 0.667, "se": 0.1361, "low": 0.234, "high": 1.0}, f"t with G-1 df, clipped to [0, 1]; got {a}"
    assert b == {"mean": 0.667, "se": 0.2357, "low": 0.0, "high": 1.0}, f"got {b}"
    assert clustered_interval([[1, 0], [], [1, 1]])["se"] == clustered_interval([[1, 0], [1, 1]])["se"], \
        "empty clusters (all runs errored) are skipped"


def test_report_on_gannet_runs():
    """report() on the 30 Gannet runs gives the headline numbers"""
    runs = copy.deepcopy(RUNS)
    r = report(runs, TASKS)
    assert r, "report() returned nothing"
    assert (r["runs"], r["errors"], r["scored"], r["passes"]) == (30, 1, 29, 21), \
        f"runs/errors/scored/passes: got {r['runs']}, {r['errors']}, {r['scored']}, {r['passes']}"
    assert r["per_run"] == {"rate": 0.724, "se_naive": 0.083, "se_clustered": 0.1104, "low": 0.474, "high": 0.974}, \
        f"per_run: got {r['per_run']}"
    assert r["pass_hat_k"] == {"k": 3, "tasks": 9, "value": 0.444, "low": 0.039, "high": 0.85}, \
        f"pass_hat_k: got {r['pass_hat_k']}"
    assert r["pass_at_k"] == 0.889 and r["insufficient"] == ["T09"], \
        f"pass@3 {r['pass_at_k']}, insufficient {r['insufficient']}: T09 has only 2 scored trials"
    assert r["mean_turns"] == 4.0 and r["cost_per_success"] == 0.0587, \
        f"turns and cost use scored runs only: got {r['mean_turns']}, {r['cost_per_success']}"
    assert [f["run_id"] for f in r["failures"]] == ["T02-2", "T03-3", "T05-3", "T06-1", "T06-2", "T06-3", "T08-1", "T08-2"], \
        f"failures in run order: got {[f['run_id'] for f in r['failures']]}"
    assert runs == RUNS, "report() must not modify the runs"
