import json
import anthropic
from anthropic import _sim

EVENT_T = "Air traffic control strike affecting Lisbon (LIS), 2 to 3 November 2026."
_ORIGINAL = dict(TOOL_FUNCTIONS)


def _fresh():
    TOOL_FUNCTIONS.clear()
    TOOL_FUNCTIONS.update(_ORIGINAL)
    _sim.calls.clear()
    _sim._queue.clear()


def _spy():
    ran = []
    for name, fn in _ORIGINAL.items():
        def wrapper(*args, _name=name, _fn=fn, **kwargs):
            ran.append(_name)
            return _fn(*args, **kwargs)
        TOOL_FUNCTIONS[name] = wrapper
    return ran


def _worker_calls():
    return [c for c in _sim.calls if c["params"]["model"] == WORKER_MODEL]


def _lead_calls():
    return [c for c in _sim.calls if c["params"]["model"] == LEAD_MODEL]


def test_worker_completes_with_a_report():
    """run_worker() runs the tool loop and returns the parsed report"""
    _fresh()
    out = run_worker(anthropic.Anthropic(), EVENT_T, "FW7Q2K")
    assert isinstance(out, dict), f"return a dict, got {out!r}"
    assert set(out) == {"booking_ref", "status", "report", "error", "iterations", "usage"}, f"keys: {sorted(out)}"
    assert out["status"] == "ok" and out["error"] is None, f"got status={out['status']!r} error={out['error']!r}"
    assert out["report"]["status"] == "cancelled" and out["report"]["affected"] == "yes", f"report: {out['report']}"
    assert len(out["report"]["options"]) == 2, "the worker should have looked up alternatives for a cancelled flight"
    assert out["iterations"] == 4 == len(_sim.calls), f"expected 4 worker calls, got {len(_sim.calls)}"


def test_worker_requests_are_configured_for_a_cheap_worker():
    """Workers use WORKER_MODEL, explicit low effort, the report schema and no forced tool_choice"""
    _fresh()
    run_worker(anthropic.Anthropic(), EVENT_T, "FW7Q2K")
    assert _sim.calls, "run_worker() made no API calls"
    for c in _sim.calls:
        p = c["params"]
        assert p["model"] == WORKER_MODEL and p["max_tokens"] == WORKER_MAX_TOKENS, "use WORKER_MODEL and WORKER_MAX_TOKENS"
        assert p.get("system") == WORKER_SYSTEM and p.get("tools") == WORKER_TOOLS, "send WORKER_SYSTEM and WORKER_TOOLS"
        cfg = p.get("output_config") or {}
        assert cfg.get("effort") == "low", "set effort explicitly: Haiku 5.5 thinks at medium by default, and thinking is billed as output"
        assert cfg.get("format", {}).get("schema") == REPORT_SCHEMA, "ask for the final report with output_config.format and REPORT_SCHEMA"
        tc = p.get("tool_choice")
        assert tc is None or tc.get("type") == "auto", "don't force tool_choice"
    second = _sim.calls[1]["params"]["messages"]
    assert [b["type"] for b in second[1]["content"]] == ["thinking", "tool_use"], "append response.content unchanged"


def test_tool_failure_is_not_a_worker_failure():
    """A failed tool inside a worker becomes an 'unknown' report, not a crash"""
    _fresh()
    out = run_worker(anthropic.Anthropic(), EVENT_T, "RT5V1C")
    assert out and out["status"] == "ok", f"the worker should still report: {out!r}"
    assert out["report"]["status"] == "unknown", f"report: {out and out['report']}"


def test_worker_failures_are_contained():
    """API errors, refusals, truncation and wrong-booking reports fail the worker without raising"""
    _fresh()
    out = run_worker(anthropic.Anthropic(max_retries=0), EVENT_T, "KM2B7Y")
    assert out and out["status"] == "failed" and out["error"] == "OverloadedError", f"API errors: got {out!r}"
    assert out["report"] is None
    _fresh()
    _sim.queue(_sim.refusal())
    out = run_worker(anthropic.Anthropic(), EVENT_T, "FW7Q2K")
    assert out and (out["status"], out["error"]) == ("failed", "refused"), f"refusal: got {out!r}"
    _fresh()
    _sim.queue(_sim.message(_sim.text('{"booking_ref": "FW7Q'), stop_reason="max_tokens"))
    out = run_worker(anthropic.Anthropic(), EVENT_T, "FW7Q2K")
    assert out and (out["status"], out["error"]) == ("failed", "max_tokens"), f"truncation: got {out!r}"
    _fresh()
    wrong = {"booking_ref": "LX4N2D", "traveler": "Marta Ilić", "affected": "yes", "status": "delayed", "options": [], "rationale": "x"}
    _sim.queue(_sim.message(_sim.text(json.dumps(wrong))))
    out = run_worker(anthropic.Anthropic(), EVENT_T, "FW7Q2K")
    assert out and (out["status"], out["error"]) == ("failed", "bad_report"), \
        f"a report about a different booking must be rejected, got {out!r}"


def test_worker_budgets_stop_runaway_work():
    """The iteration cap and the output-token budget stop a worker before it runs more tools"""
    _fresh()
    ran = _spy()
    out = run_worker(anthropic.Anthropic(), EVENT_T, "BX8C3J", max_iterations=3)
    assert out and (out["status"], out["error"]) == ("failed", "max_iterations"), f"got {out!r}"
    assert len(_sim.calls) == 3 and ran == ["get_booking", "get_booking"], \
        f"3 calls allowed, and tools from the capped turn must not run (calls={len(_sim.calls)}, ran={ran})"
    _fresh()
    ran = _spy()
    out = run_worker(anthropic.Anthropic(), EVENT_T, "FW7Q2K", max_output_tokens=1)
    assert out and (out["status"], out["error"]) == ("failed", "budget"), f"got {out!r}"
    assert len(_sim.calls) == 1 and ran == [], "over budget: stop without running that turn's tools"


def test_workers_see_only_their_own_booking():
    """Each worker starts a fresh conversation about one booking (context isolation)"""
    _fresh()
    refs = ["FW7Q2K", "LX4N2D", "PQ9T6W"]
    orchestrate(anthropic.Anthropic(), EVENT_T, refs)
    firsts = [c["params"] for c in _worker_calls() if len(c["params"]["messages"]) == 1]
    assert len(firsts) == 3, f"expected one fresh worker conversation per booking, found {len(firsts)}"
    for ref, p in zip(refs, firsts):
        text = json.dumps(p["messages"])
        assert ref in text and EVENT_T in text, f"the worker brief needs the event and its booking ({ref})"
        others = [r for r in refs if r != ref]
        assert not any(o in text for o in others), f"worker for {ref} must not see other bookings: {others}"
    for c in _worker_calls():
        text = json.dumps(c["params"]["messages"])
        assert sum(r in text for r in refs) == 1, "no worker conversation may carry another worker's context"


def test_lead_gets_reports_not_transcripts():
    """The lead makes one call over the compact reports and is told what wasn't checked"""
    _fresh()
    out = orchestrate(anthropic.Anthropic(), EVENT_T, ["FW7Q2K", "RT5V1C", "KM2B7Y"])
    assert isinstance(out, dict) and set(out) == {"answer", "reports", "failed", "usage"}, f"got {out!r}"
    leads = _lead_calls()
    assert len(leads) == 1, f"make exactly one lead call, made {len(leads)}"
    p = leads[0]["params"]
    assert p["max_tokens"] == LEAD_MAX_TOKENS and p.get("system") == LEAD_SYSTEM
    assert (p.get("output_config") or {}).get("effort") == "medium", "set the lead's effort explicitly"
    assert len(p["messages"]) == 1, "the lead gets one user message, not the workers' conversations"
    sent = json.dumps(p["messages"])
    assert "tool_result" not in sent and "tool_use" not in sent, "send reports, not worker transcripts"
    assert "KM2B7Y" in sent, "tell the lead which bookings nobody could check"
    assert [r["booking_ref"] for r in out["reports"]] == ["FW7Q2K", "RT5V1C"], f"reports: {out['reports']}"
    assert out["failed"] == [{"booking_ref": "KM2B7Y", "error": "OverloadedError"}], f"failed: {out['failed']}"
    assert "Ana Souza" in out["answer"] and "KM2B7Y" in out["answer"], f"answer: {out['answer']!r}"


def test_usage_rolls_up_across_workers_and_lead():
    """usage totals every worker call plus the lead call"""
    _fresh()
    out = orchestrate(anthropic.Anthropic(), EVENT_T, ["FW7Q2K", "LX4N2D", "KM2B7Y"])
    def total(calls, key):
        return sum(c["response"]["usage"][key] for c in calls if "response" in c)
    want_w = {"input_tokens": total(_worker_calls(), "input"), "output_tokens": total(_worker_calls(), "output")}
    want_l = {"input_tokens": total(_lead_calls(), "input"), "output_tokens": total(_lead_calls(), "output")}
    assert out and out["usage"]["workers"] == want_w, f"workers usage should be {want_w}, got {out and out['usage']['workers']}"
    assert out["usage"]["lead"] == want_l, f"lead usage should be {want_l}, got {out['usage']['lead']}"
    want_t = {k: want_w[k] + want_l[k] for k in want_w}
    assert out["usage"]["total"] == want_t, f"total should be {want_t}, got {out['usage']['total']}"


def test_no_lead_call_when_every_worker_failed():
    """If no worker produced a report, skip the lead call and hand off"""
    _fresh()
    out = orchestrate(anthropic.Anthropic(), EVENT_T, ["KM2B7Y"])
    assert out and out["answer"] == HANDOFF_MESSAGE, f"got {out!r}"
    assert not _lead_calls(), "don't pay for a lead call with nothing to summarize"
    assert out["usage"]["lead"] == {"input_tokens": 0, "output_tokens": 0}
