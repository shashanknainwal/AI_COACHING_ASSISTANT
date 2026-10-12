from anthropic import _sim
import fde_clock

_CASE = {c["id"]: c for c in CASES}


def _fresh():
    _sim.calls.clear()
    _sim._queue.clear()
    _sim._cache.clear()
    fde_clock.reset()


def test_bug1_system_prompt_is_stable():
    """Bug 1: the system prompt is byte-identical on every request, so the cache hits"""
    _fresh()
    run_suite(client, [_CASE["C1"], _CASE["C3"]])
    systems = [r.get("system") for r in _sim.requests()]
    assert len(systems) == 5, f"expected 5 API calls for C1 and C3, got {len(systems)}"
    assert all(s == systems[0] for s in systems), \
        "the system prompt changes between requests (a timestamp?), which invalidates the prompt cache every call"
    s0 = systems[0]
    text = s0 if isinstance(s0, str) else "".join(b.get("text", "") for b in s0)
    assert text == SYSTEM_PROMPT, "send the system prompt exactly, with nothing appended"
    reads = [c["response"]["usage"]["cache_read"] for c in _sim.calls]
    assert reads[0] == 0 and all(r > 0 for r in reads[1:]), f"every call after the first should read the cached prefix: {reads}"


def test_bug2_parallel_tool_results_in_one_message():
    """Bug 2: all tool results for one turn go back in a single user message"""
    _fresh()
    rows = run_suite(client, [_CASE["C2"]])
    assert rows == [{"id": "C2", "status": "completed", "grade": "pass"}], \
        f"C2 asks for two tools in one turn; splitting the results across two messages is a 400: got {rows}"
    last = _sim.requests()[-1]["messages"]
    results = last[2]["content"]
    assert [b["type"] for b in results] == ["tool_result", "tool_result"] and len(last) == 3, \
        "the two tool_result blocks belong in the one user message after the tool_use turn"


def test_bug3_history_is_append_only():
    """Bug 3: earlier turns are never edited, and thinking blocks go back unchanged"""
    _fresh()
    run_suite(client, [_CASE["C3"]])
    reqs = _sim.requests()
    assert len(reqs) == 3, f"C3 takes three calls, got {len(reqs)}"
    for prev, cur in zip(reqs, reqs[1:]):
        assert cur["messages"][:len(prev["messages"])] == prev["messages"], \
            "a later request rewrote an earlier message (trimmed tool results?). Keep the history append-only."
    for m in reqs[-1]["messages"]:
        if m["role"] == "assistant":
            assert m["content"][0]["type"] == "thinking", \
                "send each assistant turn back exactly as returned, thinking block included"
    full = reqs[-1]["messages"][2]["content"][0]["content"]
    assert "[trimmed]" not in full and len(full) > 120


def test_bug4_no_retry_storm():
    """Bug 4: overloads get at most the SDK's 3 attempts, and a 400 is never retried"""
    _fresh()
    rows = run_suite(client, [_CASE["C4"]])
    assert rows and rows[0]["status"] == "error", f"an overloaded API is an error row: got {rows}"
    assert len(_sim.calls) <= 3, \
        f"{len(_sim.calls)} attempts for one overloaded case: the SDK already retries twice, don't wrap it in another loop"
    _fresh()
    rows = run_suite(client, [_CASE["C5"]])
    assert rows and rows[0]["status"] == "error" and rows[0].get("error") == "BadRequestError", f"got {rows}"
    assert len(_sim.calls) == 1, f"a 400 can't succeed on retry, but it was attempted {len(_sim.calls)} times"


def test_suite_results():
    """The fixed harness completes the three answerable cases and reports two errors"""
    _fresh()
    rows = run_suite(client, CASES)
    assert [(r["id"], r["status"], r["grade"]) for r in rows] == [
        ("C1", "completed", "pass"), ("C2", "completed", "pass"), ("C3", "completed", "pass"),
        ("C4", "error", "error"), ("C5", "error", "error")], f"got {rows}"
    assert len(_sim.calls) <= 11, f"{len(_sim.calls)} attempts for five cases"
