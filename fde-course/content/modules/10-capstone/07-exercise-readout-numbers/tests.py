import json
import anthropic
from anthropic import _sim

PM = {"per_day": 40.2, "automation_rate": 0.45, "avg_handle_minutes": 8.6, "ops_hours_per_day": 5.8, "cost_per_exception": 0.0185}
IMP = {"baseline_avg_minutes": 30.8, "hours_saved_per_month": 308.6, "labor_savings_per_month": 14812.8,
       "api_cost_per_month": 15.46, "net_savings_per_month": 14797.34, "payback_months": 2.6}


def test_pilot_metrics():
    """pilot_metrics() summarizes the pilot"""
    assert pilot_metrics(PILOT) == PM, f"got {pilot_metrics(PILOT)}"
    small = {"days": 2, "exceptions": 10, "auto_handled": 4, "assisted": 6, "avg_minutes_auto": 3.0,
             "avg_minutes_assisted": 10.0, "api_cost_usd": 0.5}
    assert pilot_metrics(small) == {"per_day": 5.0, "automation_rate": 0.4, "avg_handle_minutes": 7.2,
                                    "ops_hours_per_day": 0.6, "cost_per_exception": 0.05}


def test_impact():
    """impact() turns minutes saved into monthly money and payback"""
    assert impact(BASELINE, PM, ASSUMPTIONS) == IMP, f"got {impact(BASELINE, PM, ASSUMPTIONS)}"
    small = impact({"per_day": 10, "ops_hours_per_day": 5}, {"avg_handle_minutes": 10, "cost_per_exception": 0.02},
                   {"loaded_cost_per_hour": 60, "working_days_per_month": 20, "engagement_fee_usd": 10000})
    # baseline 30 min/exception, saves 20 min x 200 exceptions = 66.7 h; $4,002 - $4 API
    assert small == {"baseline_avg_minutes": 30.0, "hours_saved_per_month": 66.7, "labor_savings_per_month": 4002.0,
                     "api_cost_per_month": 4.0, "net_savings_per_month": 3998.0, "payback_months": 2.5}, f"got {small}"


def test_headlines():
    """headlines() formats the five readout sentences exactly"""
    assert headlines(BASELINE, PILOT, PM, IMP) == [
        "45% of exceptions were handled end to end",
        "309 coordinator hours saved per month",
        "SLA breaches fell from 20.7% to 8.2%",
        "Platinum breaches fell from 39% to 5%",
        "$14,797 net savings per month, paying back the engagement in 2.6 months",
    ], f"got {headlines(BASELINE, PILOT, PM, IMP)}"


def test_numbers_in():
    """numbers_in() finds and normalizes every number"""
    assert numbers_in("$14,797 saved, 8.2% breaches, 309 hours in 2.6 months.") == ["14797", "8.2%", "309", "2.6"]
    assert numbers_in("Up 1,200.50 from 3. Done") == ["1200.50", "3"], "drop a trailing sentence period"
    assert numbers_in("no numbers here") == []


def test_draft_summary_request():
    """draft_summary() sends the headlines in tags with a structured-output schema"""
    _sim.calls.clear(); _sim._queue.clear()
    lines = headlines(BASELINE, PILOT, PM, IMP)
    draft_summary(anthropic.Anthropic(), lines)
    p = _sim.last_request()
    assert p["model"] == MODEL and p["max_tokens"] >= 1024
    assert "<headlines>\n" + "\n".join(f"- {l}" for l in lines) + "\n</headlines>" in p["messages"][0]["content"], \
        "list each headline as '- <line>' inside <headlines> tags"
    assert (p.get("output_config") or {}).get("format") == {"type": "json_schema", "schema": SUMMARY_SCHEMA}


def test_draft_summary_flags_invented_numbers():
    """Numbers the model invented are flagged; supported ones are not"""
    _sim.calls.clear(); _sim._queue.clear()
    got = draft_summary(anthropic.Anthropic(), headlines(BASELINE, PILOT, PM, IMP))
    assert set(got) == {"summary", "unsupported_numbers"} and got["unsupported_numbers"] == ["2400"], f"got {got}"
    _sim.queue(json.dumps({"summary": "45% automated, saving $14,797 a month and 3,700 hours a year; 309 hours a month."}))
    got = draft_summary(anthropic.Anthropic(), headlines(BASELINE, PILOT, PM, IMP))
    assert got["unsupported_numbers"] == ["3700"], f"got {got['unsupported_numbers']}"
