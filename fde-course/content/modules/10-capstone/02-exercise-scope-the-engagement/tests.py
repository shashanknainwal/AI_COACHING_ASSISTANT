import json
import anthropic
from anthropic import _sim
from fde_datasets import northstar

H = lambda date, t, tier, minutes, breached: {"id": "x", "date": date, "type": t, "tier": tier, "handle_minutes": minutes,
                                             "first_response_hours": 1.0, "sla_hours": 4, "breached": breached}


def test_baseline_small():
    """baseline() computes volume, handling time and SLA breaches"""
    hist = [H("d1", "DELAY", "gold", 10, False), H("d1", "DELAY", "gold", 30, True), H("d2", "DAMAGE", "standard", 20, False),
            H("d2", "DELAY", "standard", 40, False), H("d2", "DAMAGE", "gold", 60, False)]
    got = baseline(hist)
    assert got == {"per_day": 2.5, "median_handle_minutes": 30, "p90_handle_minutes": 60, "ops_hours_per_day": 1.3,
                   "breach_rate": 0.2, "breach_rate_by_tier": {"gold": 0.333, "standard": 0.0},
                   "by_type": {"DELAY": 3, "DAMAGE": 2}}, f"got {got}"
    assert baseline(hist[:4])["median_handle_minutes"] == 25, "with an even count, the median is the mean of the middle two"


def test_baseline_real():
    """baseline() on NorthStar's 30 days of history"""
    got = baseline(northstar.EXCEPTION_HISTORY)
    assert got["per_day"] == 39.8 and got["median_handle_minutes"] == 25 and got["p90_handle_minutes"] == 63
    assert got["ops_hours_per_day"] == 20.4 and got["breach_rate"] == 0.207
    assert got["breach_rate_by_tier"] == {"gold": 0.098, "standard": 0.197, "platinum": 0.39}
    assert got["by_type"]["DELAY"] == 567 and sum(got["by_type"].values()) == 1194


def test_prioritize():
    """prioritize() keeps must-haves, then fills the budget by value per day"""
    got = prioritize(northstar.ASKS, 20)
    assert got == {"in_scope": ["A1", "A2", "A5", "A6", "A8"], "out_of_scope": ["A3", "A4", "A7"],
                   "days_used": 19, "days_left": 1}, f"got {got}"
    assert prioritize(northstar.ASKS, 13)["in_scope"] == ["A1", "A2", "A5"]


def test_prioritize_ties_and_overflow():
    """Ties go to the smaller ask; impossible must-haves raise ValueError"""
    asks = [{"id": "X", "value": 4, "effort_days": 4, "must_have": False},
            {"id": "Y", "value": 2, "effort_days": 2, "must_have": False},
            {"id": "Z", "value": 5, "effort_days": 6, "must_have": True}]
    assert prioritize(asks, 8) == {"in_scope": ["Z", "Y"], "out_of_scope": ["X"], "days_used": 8, "days_left": 0}
    try:
        prioritize(asks, 5)
    except ValueError as e:
        assert str(e) == "must-haves need 6 days but the budget is 5", f"message: {e}"
    else:
        raise AssertionError("must-haves over budget should raise ValueError")


def test_success_metrics():
    """success_metrics() sets the three targets from the baseline"""
    got = success_metrics({"median_handle_minutes": 25, "breach_rate": 0.207})
    assert got == [{"metric": "median_handle_minutes", "baseline": 25, "target": 12.5},
                   {"metric": "sla_breach_rate", "baseline": 0.207, "target": 0.103},
                   {"metric": "automation_rate", "baseline": 0.0, "target": 0.4}], f"got {got}"


def test_draft_brief():
    """draft_brief() sends the facts in tags with a structured-output schema"""
    _sim.calls.clear(); _sim._queue.clear()
    facts = {"baseline": {"per_day": 39.8, "breach_rate": 0.207}, "budget_days": 20}
    got = draft_brief(anthropic.Anthropic(), facts)
    assert set(got) == {"problem_statement", "executive_summary", "risks", "open_questions"}, f"got {got}"
    assert "39.8" in got["problem_statement"]
    p = _sim.last_request()
    assert p["model"] == MODEL and p["max_tokens"] >= 1024
    content = p["messages"][0]["content"]
    assert f"<engagement_facts>\n{json.dumps(facts, indent=2, sort_keys=True)}\n</engagement_facts>" in content, \
        "put json.dumps(facts, indent=2, sort_keys=True) inside <engagement_facts> tags"
    assert (p.get("output_config") or {}).get("format") == {"type": "json_schema", "schema": BRIEF_SCHEMA}


def test_draft_brief_refusal():
    """A refusal raises RuntimeError instead of returning garbage"""
    _sim.calls.clear(); _sim._queue.clear()
    _sim.queue(_sim.refusal())
    try:
        draft_brief(anthropic.Anthropic(), {"baseline": {"per_day": 1, "breach_rate": 0}, "budget_days": 1})
    except RuntimeError:
        pass
    else:
        raise AssertionError("raise RuntimeError on a refusal")
