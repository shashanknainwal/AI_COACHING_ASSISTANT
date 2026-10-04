import json
import anthropic
from anthropic import _sim


def _fresh():
    reset_data()
    _sim.calls.clear()
    _sim._queue.clear()


def _customers():
    """The learner's current CUSTOMERS dict (reset_data() rebinds it)."""
    return reset_data.__globals__["CUSTOMERS"]


def _raises(exc, fn, *args):
    try:
        fn(*args)
    except exc as e:
        return e.args[0]
    raise AssertionError(f"{fn.__name__}{args} should raise {exc.__name__}")


def test_read_tools():
    """lookup_order() and track_shipment() return compact dicts and clear errors"""
    _fresh()
    assert lookup_order(" b-1001 ") == {"order_id": "B-1001", "customer_id": "C-100", "status": "shipped",
                                         "shipment_id": "SHP-1003", "total": 89.0}, "normalize the ID and return the five fields"
    assert lookup_order("B-1003")["shipment_id"] is None
    msg = _raises(KeyError, lookup_order, "B-9999")
    assert msg == "No order found with ID B-9999.", f"message: {msg!r}"
    assert track_shipment("shp-1003") == {"shipment_id": "SHP-1003", "status": "exception", "eta": "2026-03-12",
                                           "last_event": "Delayed: weather at Denver hub"}
    msg = _raises(KeyError, track_shipment, "SHP-0000")
    assert msg == "No shipment found with ID SHP-0000.", f"message: {msg!r}"


def test_issue_store_credit_limits():
    """issue_store_credit() updates the balance and enforces the $50 limit"""
    _fresh()
    assert issue_store_credit("C-101", 20, "late_delivery") == {"customer_id": "C-101", "new_balance": 35.0}
    assert _customers()["C-101"]["store_credit"] == 35.0, "update the customer's store_credit"
    for bad in (0, -5, 50.01, 500):
        msg = _raises(ValueError, issue_store_credit, "C-101", bad, "goodwill")
        assert msg == "amount must be between 0 and 50", f"amount {bad}: {msg!r}"
    assert _customers()["C-101"]["store_credit"] == 35.0, "a rejected credit must not change the balance"
    assert issue_store_credit("C-102", 50, "goodwill")["new_balance"] == 50.0, "exactly $50 is allowed"
    msg = _raises(KeyError, issue_store_credit, "C-999", 10, "goodwill")
    assert msg == "No customer found with ID C-999.", f"message: {msg!r}"


def test_tool_definitions():
    """TOOLS has three strict, well-described definitions"""
    by_name = {t.get("name"): t for t in TOOLS}
    assert sorted(by_name) == ["issue_store_credit", "lookup_order", "track_shipment"], f"tool names: {sorted(by_name)}"
    expected = {"lookup_order": {"order_id": "string"}, "track_shipment": {"shipment_id": "string"},
                "issue_store_credit": {"customer_id": "string", "amount": "number", "reason": "string"}}
    for name, props in expected.items():
        t = by_name[name]
        s = t.get("input_schema", {})
        assert t.get("strict") is True and s.get("additionalProperties") is False, f"{name}: make it strict"
        assert {k: v.get("type") for k, v in s.get("properties", {}).items()} == props, f"{name} properties"
        assert sorted(s.get("required", [])) == sorted(props), f"{name}: every property is required"
        assert any(w in t.get("description", "").lower() for w in ("call this", "use this", "whenever", "when ")), \
            f"{name}: the description should say when to call it"
    assert by_name["issue_store_credit"]["input_schema"]["properties"]["reason"].get("enum") == CREDIT_REASONS, \
        "restrict reason with enum: CREDIT_REASONS"


def test_execute():
    """execute() returns JSON results, is_error results, and rejects unknown tools"""
    _fresh()
    ok = execute(anthropic.ToolUseBlock("track_shipment", {"shipment_id": "SHP-1007"}, id="t1"))
    assert ok["type"] == "tool_result" and ok["tool_use_id"] == "t1" and "is_error" not in ok, f"got {ok}"
    assert json.loads(ok["content"])["status"] == "in_transit", "content should be the JSON-encoded result"
    over = execute(anthropic.ToolUseBlock("issue_store_credit", {"customer_id": "C-100", "amount": 75, "reason": "goodwill"}, id="t2"))
    assert over == {"type": "tool_result", "tool_use_id": "t2", "content": "amount must be between 0 and 50", "is_error": True}, f"got {over}"
    missing = execute(anthropic.ToolUseBlock("lookup_order", {"order_id": "B-0"}, id="t3"))
    assert missing == {"type": "tool_result", "tool_use_id": "t3", "content": "No order found with ID B-0.", "is_error": True}, f"got {missing}"
    unknown = execute(anthropic.ToolUseBlock("refund_everything", {}, id="t4"))
    assert unknown == {"type": "tool_result", "tool_use_id": "t4", "content": "Unknown tool: refund_everything", "is_error": True}


def test_run_agent_late_delivery():
    """run_agent() chains three tools, credits $25, and returns answer, steps and trace"""
    _fresh()
    out = run_agent(anthropic.Anthropic(), "My lamp order B-1001 is late. Can you check what's going on and make it right?")
    assert isinstance(out, dict) and set(out) == {"answer", "steps", "trace"}, f"got {out!r}"
    assert [t["tool"] for t in out["trace"]] == ["lookup_order", "track_shipment", "issue_store_credit"], f"trace: {out['trace']}"
    assert out["trace"][2]["input"] == {"customer_id": "C-100", "amount": 25, "reason": "late_delivery"}
    assert all(t["is_error"] is False for t in out["trace"]), "record is_error for every call"
    assert out["steps"] == 4 and len(_sim.calls) == 4, f"steps should count API calls: {out['steps']}"
    assert "$25 in store credit" in out["answer"] and "Delayed: weather" in out["answer"], f"answer: {out['answer']!r}"
    assert _customers()["C-100"]["store_credit"] == 25.0


def test_every_request_is_well_formed():
    """Every request sends MODEL, SYSTEM_PROMPT, TOOLS and Claude's full turns"""
    _fresh()
    run_agent(anthropic.Anthropic(), "Where is order B-1004?")
    assert len(_sim.calls) == 3, f"expected 3 API calls, got {len(_sim.calls)}"
    for c in _sim.calls:
        p = c["params"]
        assert p["model"] == MODEL and p["max_tokens"] >= 4096, "use MODEL and max_tokens >= 4096"
        assert p.get("system") == SYSTEM_PROMPT and p.get("tools") == TOOLS, "send SYSTEM_PROMPT and TOOLS every time"
    first_turn = _sim.calls[1]["params"]["messages"][1]["content"]
    assert [b["type"] for b in first_turn] == ["thinking", "tool_use"], "append Claude's full turn, thinking included"


def test_tool_errors_are_recorded():
    """A failed lookup is sent back as is_error and marked in the trace"""
    _fresh()
    out = run_agent(anthropic.Anthropic(), "Where is my order B-4242?")
    assert out["trace"] == [{"tool": "lookup_order", "input": {"order_id": "B-4242"}, "is_error": True}], f"trace: {out['trace']}"
    assert "couldn't find" in out["answer"] and out["steps"] == 2


def test_parallel_results_in_one_message():
    """Two tool_use blocks in one turn get both results in ONE user message"""
    _fresh()
    _sim.queue(_sim.message(_sim.tool_use("lookup_order", {"order_id": "B-1001"}, id="p1"),
                            _sim.tool_use("lookup_order", {"order_id": "B-1004"}, id="p2")),
               "Both orders are on their way.")
    out = run_agent(anthropic.Anthropic(), "Check B-1001 and B-1004")
    assert out["answer"] == "Both orders are on their way." and out["steps"] == 2
    last = _sim.last_request()["messages"][-1]["content"]
    assert [r["tool_use_id"] for r in last] == ["p1", "p2"], "send every tool_result in a single user message"
    assert len(out["trace"]) == 2


def test_max_steps():
    """run_agent() stops with RuntimeError after max_steps API calls"""
    _fresh()
    for i in range(5):
        _sim.queue(_sim.message(_sim.tool_use("lookup_order", {"order_id": "B-1001"}, id=f"loop{i}")))
    msg = _raises(RuntimeError, run_agent, anthropic.Anthropic(), "Keep checking B-1001", 3)
    assert msg == "agent did not finish within max_steps", f"message: {msg!r}"
    assert len(_sim.calls) == 3, f"max_steps=3 should allow exactly 3 API calls, made {len(_sim.calls)}"
