import json
import anthropic
from anthropic import _sim

_ORIGINAL = dict(TOOL_FUNCTIONS)
CANCELLED = "Booking FW7Q2K: I just got a cancellation email. What are my options?"


def _fresh():
    TOOL_FUNCTIONS.clear()
    TOOL_FUNCTIONS.update(_ORIGINAL)
    _sim.calls.clear()
    _sim._queue.clear()


def _spy():
    """Wrap every tool so the test can see which ones actually ran."""
    ran = []
    for name, fn in _ORIGINAL.items():
        def wrapper(*args, _name=name, _fn=fn, **kwargs):
            ran.append(_name)
            return _fn(*args, **kwargs)
        TOOL_FUNCTIONS[name] = wrapper
    return ran


def _block(name, inp, id):
    return anthropic.ToolUseBlock(name, inp, id=id)


def test_execute_tool_success():
    """execute_tool() returns a JSON tool_result for a good call"""
    _fresh()
    r = execute_tool(_block("get_booking", {"booking_ref": "fw7q2k"}, "t1"))
    assert isinstance(r, dict), f"return a tool_result dict, got {r!r}"
    assert r.get("type") == "tool_result" and r.get("tool_use_id") == "t1", f"got {r}"
    assert not r.get("is_error"), "a successful call must not set is_error"
    assert json.loads(r["content"])["flight"] == "FW 212", "content should be json.dumps() of the tool's return value"


def test_execute_tool_errors_become_results():
    """execute_tool() turns ToolError, unknown tools and crashes into is_error results"""
    _fresh()
    bad = execute_tool(_block("get_booking", {"booking_ref": "ZZ0000"}, "t2"))
    assert bad == {"type": "tool_result", "tool_use_id": "t2", "is_error": True,
                   "content": "No booking found with reference ZZ0000. References look like FW7Q2K."}, f"ToolError: got {bad}"
    unknown = execute_tool(_block("issue_voucher", {}, "t3"))
    assert unknown == {"type": "tool_result", "tool_use_id": "t3", "is_error": True, "content": "Unknown tool: issue_voucher"}, f"unknown tool: got {unknown}"
    crash = execute_tool(_block("get_flight_status", {"flight": "FW 404", "date": "2026-11-04"}, "t4"))
    assert crash.get("is_error") is True and crash.get("tool_use_id") == "t4", f"a crashing tool must become an is_error result: {crash}"
    assert crash["content"] == "get_flight_status failed unexpectedly (ConnectionError). Try again later or tell the traveler.", \
        f"unexpected errors get the generic message: {crash['content']!r}"
    wrong_args = execute_tool(_block("get_flight_status", {"flight": "FW 88"}, "t5"))
    assert wrong_args.get("is_error") is True and "TypeError" in wrong_args["content"], \
        f"missing arguments raise TypeError inside the tool; return it as a result: {wrong_args}"


def test_internal_details_never_reach_the_model():
    """Unexpected exceptions don't leak internal hosts or stack details"""
    _fresh()
    crash = execute_tool(_block("get_flight_status", {"flight": "FW 404", "date": "2026-11-04"}, "t6"))
    assert crash and "10.0.3.7" not in crash.get("content", "") and "ops-db" not in crash.get("content", ""), \
        "don't put str(exc) from unexpected errors into the tool_result: it can leak internals"


def test_happy_path_with_parallel_calls():
    """run_agent() completes, batching parallel tool_results into one user message"""
    _fresh()
    out = run_agent(anthropic.Anthropic(), CANCELLED)
    assert isinstance(out, dict), f"return a dict, got {out!r}"
    assert set(out) == {"status", "answer", "iterations", "tool_calls", "usage"}, f"keys: {sorted(out)}"
    assert out["status"] == "completed", f"status: {out['status']!r}"
    assert out["iterations"] == 3 and len(_sim.calls) == 3, f"expected 3 API calls, got {len(_sim.calls)}"
    assert [c["name"] for c in out["tool_calls"]] == ["get_booking", "get_flight_status", "find_alternatives"], f"tool_calls: {out['tool_calls']}"
    assert out["tool_calls"][1] == {"name": "get_flight_status", "input": {"flight": "FW 212", "date": "2026-11-02"}, "is_error": False}
    assert "FW 214" in out["answer"] and "cancelled" in out["answer"], f"answer: {out['answer']!r}"
    last = _sim.calls[2]["params"]["messages"]
    assert len(last) == 5, f"the third request should hold 5 messages (user, assistant, user, assistant, user), got {len(last)}"
    batch = last[-1]
    assert batch["role"] == "user" and [b["type"] for b in batch["content"]] == ["tool_result", "tool_result"], \
        "both parallel results go in ONE user message, as tool_result blocks"
    ids = [b["id"] for b in last[3]["content"] if b["type"] == "tool_use"]
    assert [b["tool_use_id"] for b in batch["content"]] == ids, "keep the results in the same order as the tool_use blocks"


def test_every_request_is_well_formed():
    """Every request sends MODEL, MAX_TOKENS, SYSTEM_PROMPT, TOOLS, full assistant turns and no forced tool_choice"""
    _fresh()
    run_agent(anthropic.Anthropic(), CANCELLED)
    assert _sim.calls, "run_agent() made no API calls"
    for c in _sim.calls:
        p = c["params"]
        assert p["model"] == MODEL and p["max_tokens"] == MAX_TOKENS, "use MODEL and MAX_TOKENS"
        assert p.get("system") == SYSTEM_PROMPT and p.get("tools") == TOOLS, "send SYSTEM_PROMPT and TOOLS on every call"
        tc = p.get("tool_choice")
        assert tc is None or tc.get("type") == "auto", "don't force tool_choice: Opus 5.5 rejects 'any' and 'tool'"
    turn = _sim.calls[1]["params"]["messages"][1]
    assert turn["role"] == "assistant" and [b["type"] for b in turn["content"]] == ["thinking", "tool_use"], \
        "append response.content unchanged, thinking blocks included"


def test_tool_failures_do_not_crash_the_loop():
    """A crashing tool is reported to Claude and the run still completes"""
    _fresh()
    out = run_agent(anthropic.Anthropic(), "Is my flight on booking RT5V1C on time?")
    assert out and out["status"] == "completed", f"got {out!r}"
    assert out["tool_calls"][-1]["is_error"] is True, "mark the failed call in tool_calls"
    sent = _sim.calls[-1]["params"]["messages"][-1]["content"][0]
    assert sent.get("is_error") is True, "send the failure back with is_error: True"
    assert "couldn't reach" in out["answer"], f"answer: {out['answer']!r}"


def test_iteration_cap_hands_off():
    """At max_iterations the loop stops, runs no more tools and returns the handoff message"""
    _fresh()
    ran = _spy()
    for i in range(6):
        _sim.queue(_sim.message(_sim.tool_use("get_booking", {"booking_ref": "FW7Q2K"}, id=f"loop{i}")))
    out = run_agent(anthropic.Anthropic(), "Check FW7Q2K again and again", max_iterations=3)
    assert out is not None, "return a result instead of raising"
    assert len(_sim.calls) == 3, f"max_iterations=3 allows exactly 3 API calls, made {len(_sim.calls)}"
    assert out["status"] == "max_iterations" and out["answer"] == HANDOFF_MESSAGE, f"got {out['status']!r} / {out['answer']!r}"
    assert out["iterations"] == 3
    assert ran == ["get_booking", "get_booking"], f"tools requested in the capped turn must not run; ran {ran}"


def test_refusal_runs_no_tools():
    """stop_reason 'refusal' ends the run without executing that turn's tools"""
    _fresh()
    ran = _spy()
    _sim.queue(_sim.message(_sim.tool_use("get_booking", {"booking_ref": "FW7Q2K"}, id="r1"), stop_reason="refusal"))
    out = run_agent(anthropic.Anthropic(), CANCELLED)
    assert out and out["status"] == "refusal" and out["answer"] == REFUSAL_MESSAGE, f"got {out!r}"
    assert ran == [] and out["tool_calls"] == [] and len(_sim.calls) == 1, "never run tools from a refused turn"


def test_truncated_turn_runs_no_tools():
    """stop_reason 'max_tokens' ends the run: a cut-off tool_use may have partial input"""
    _fresh()
    ran = _spy()
    _sim.queue(_sim.message(_sim.text("Let me look for other flights."),
                            _sim.tool_use("find_alternatives", {"flight": "FW 212"}, id="m1"), stop_reason="max_tokens"))
    out = run_agent(anthropic.Anthropic(), CANCELLED)
    assert out and out["status"] == "max_tokens", f"got {out!r}"
    assert out["answer"] == "Let me look for other flights.", "return the text you did get"
    assert ran == [] and len(_sim.calls) == 1, "don't run a tool_use from a truncated turn"


def test_usage_is_totalled():
    """usage sums input and output tokens across every call"""
    _fresh()
    out = run_agent(anthropic.Anthropic(), CANCELLED)
    want_in = sum(c["response"]["usage"]["input"] for c in _sim.calls)
    want_out = sum(c["response"]["usage"]["output"] for c in _sim.calls)
    assert out and out["usage"] == {"input_tokens": want_in, "output_tokens": want_out}, \
        f"usage should be {{'input_tokens': {want_in}, 'output_tokens': {want_out}}}, got {out and out['usage']}"
