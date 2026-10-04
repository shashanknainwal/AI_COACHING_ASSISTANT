import anthropic
from anthropic import _sim

ALL_OK = {"decided": True, "action": True, "priority": True, "notified": True, "no_forbidden": True}


def _run(decision, calls, steps=4, cost=0.01):
    audit = [{"tool": t, "input": {}, "approval": "not_required", "is_error": err} for t, err in calls]
    return {"decision": decision, "steps": steps, "audit": audit, "cost_usd": cost}


def _rows():
    _sim.calls.clear(); _sim._queue.clear()
    return run_suite(anthropic.Anthropic(), EVAL_CASES, approve_reroutes)


def test_grade_checks():
    """grade() checks decision, action, priority, notification and forbidden tools"""
    case = EVAL_CASES[1]   # platinum delay: notify_and_ticket, P1, must notify
    good = _run({"action": "notify_and_ticket", "priority": "P1", "reason": ""},
                [("get_shipment", False), ("notify_customer", False), ("create_ops_ticket", False), ("record_decision", False)])
    assert grade(case, good) == {"checks": ALL_OK, "pass": True}
    blocked = _run({"action": "notify_and_ticket", "priority": "P2", "reason": ""},
                   [("get_shipment", False), ("notify_customer", True), ("record_decision", False)])
    assert grade(case, blocked) == {"checks": dict(ALL_OK, priority=False, notified=False), "pass": False}, \
        "a blocked notify_customer doesn't count as notifying"
    assert grade(case, None) == {"checks": {k: False for k in ALL_OK}, "pass": False}
    undecided = grade(case, _run(None, [("get_shipment", False)]))["checks"]
    assert undecided["decided"] is False and undecided["action"] is False and list(undecided) == CHECKS


def test_grade_forbidden_and_optional_notify():
    """Forbidden tools fail even when the call errored; must_notify False never requires a message"""
    case = EVAL_CASES[11]  # delivered: no_action, nothing may be sent
    quiet = _run({"action": "no_action", "priority": "P3", "reason": ""}, [("get_shipment", False), ("record_decision", False)])
    assert grade(case, quiet)["pass"] is True
    noisy = _run({"action": "no_action", "priority": "P3", "reason": ""},
                 [("get_shipment", False), ("notify_customer", True), ("record_decision", False)])
    assert grade(case, noisy)["checks"]["no_forbidden"] is False, "attempting a forbidden tool fails the check"


def test_run_suite():
    """run_suite() runs every case and records crashes instead of stopping"""
    rows = _rows()
    assert [r["id"] for r in rows] == [c["id"] for c in EVAL_CASES]
    assert set(rows[0]) == {"id", "type", "expected_priority", "run", "error", "grades"}
    assert rows[0]["type"] == "CUSTOMS_HOLD" and rows[0]["expected_priority"] == "P1" and rows[0]["error"] is None
    assert [r["id"] for r in rows if not r["grades"]["pass"]] == ["E-04", "E-10"]
    _sim.calls.clear(); _sim._queue.clear()
    _sim.queue(_sim.overloaded(), _sim.overloaded(), _sim.overloaded())
    crashed = run_suite(anthropic.Anthropic(max_retries=0), EVAL_CASES[:2], approve_reroutes)
    assert crashed[0]["run"] is None and crashed[0]["error"].startswith("OverloadedError") and crashed[0]["grades"]["pass"] is False
    assert crashed[1]["error"] is not None or crashed[1]["run"] is not None, "the second case still runs"


def test_report():
    """report() summarizes pass rate, failures by check and type, P1 recall, cost and steps"""
    rep = report(_rows())
    assert {k: rep[k] for k in ("n", "pass_rate", "failed_checks", "p1_recall", "avg_steps")} == {
        "n": 13, "pass_rate": 0.846, "failed_checks": {"action": 1, "priority": 1, "notified": 1},
        "p1_recall": 0.75, "avg_steps": 4.31}, f"got {rep}"
    assert rep["by_type"] == {"CUSTOMS_HOLD": 1.0, "DELAY": 0.75, "PICKUP_MISSED": 1.0, "DAMAGE": 0.5,
                              "ADDRESS_ISSUE": 1.0, "DELIVERED": 1.0, "UNKNOWN": 1.0}
    assert 0.01 < rep["avg_cost_usd"] < 0.03, f"avg cost {rep['avg_cost_usd']}"


def test_ship_decision():
    """ship_decision() blocks on pass rate, P1 recall and cost"""
    rep = {"pass_rate": 0.846, "p1_recall": 0.75, "avg_cost_usd": 0.0175}
    assert ship_decision(rep) == {"ship": False, "reasons": ["pass rate 0.846 is below 0.900", "P1 recall 0.750 is below 1.000"]}
    assert ship_decision({"pass_rate": 0.95, "p1_recall": 1.0, "avg_cost_usd": 0.02}) == {"ship": True, "reasons": []}
    assert ship_decision({"pass_rate": 0.95, "p1_recall": 1.0, "avg_cost_usd": 0.06}) == \
        {"ship": False, "reasons": ["average cost $0.0600 is above $0.0500"]}
    assert ship_decision(rep, min_pass_rate=0.8, min_p1_recall=0.7)["ship"] is True
