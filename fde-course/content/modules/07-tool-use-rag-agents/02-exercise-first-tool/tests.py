import json
import anthropic
from anthropic import _sim


def _fresh():
    _sim.calls.clear()
    _sim._queue.clear()


def test_tool_definition():
    """LOOKUP_ORDER_TOOL is a strict, well-described tool"""
    t = LOOKUP_ORDER_TOOL
    assert t.get("name") == "lookup_order", "name it lookup_order"
    assert "order ID" in t.get("description", ""), "the description should mention the order ID"
    assert any(w in t["description"].lower() for w in ("call this", "use this", "whenever", "when the")), "say WHEN to call the tool"
    s = t.get("input_schema", {})
    assert s.get("type") == "object" and s.get("properties", {}).get("order_id", {}).get("type") == "string"
    assert s.get("required") == ["order_id"] and s.get("additionalProperties") is False
    assert t.get("strict") is True, "set strict: True"


def test_lookup_order():
    """lookup_order() normalizes IDs and returns a compact summary"""
    assert lookup_order(" b-1001 ") == {"order_id": "B-1001", "status": "shipped", "total": 89.0,
                                         "items": ["Arc floor lamp"], "shipment_id": "SHP-1003"}
    try:
        lookup_order("B-9999")
    except KeyError as e:
        assert e.args[0] == "No order found with ID B-9999.", f"message: {e.args[0]!r}"
    else:
        raise AssertionError("unknown orders should raise KeyError")


def test_run_tool_success_and_errors():
    """run_tool() returns tool_result dicts, with is_error for failures"""
    ok = run_tool(anthropic.ToolUseBlock("lookup_order", {"order_id": "B-1002"}, id="toolu_a"))
    assert ok["type"] == "tool_result" and ok["tool_use_id"] == "toolu_a" and "is_error" not in ok
    assert json.loads(ok["content"])["status"] == "delivered", "content should be the JSON-encoded result"
    bad = run_tool(anthropic.ToolUseBlock("lookup_order", {"order_id": "B-0"}, id="toolu_b"))
    assert bad == {"type": "tool_result", "tool_use_id": "toolu_b", "content": "No order found with ID B-0.", "is_error": True}, f"got {bad}"
    unknown = run_tool(anthropic.ToolUseBlock("delete_everything", {}, id="toolu_c"))
    assert unknown == {"type": "tool_result", "tool_use_id": "toolu_c", "content": "Unknown tool: delete_everything", "is_error": True}


def test_answer_full_cycle():
    """answer() calls Claude twice with a valid tool_use/tool_result history"""
    _fresh()
    got = answer(anthropic.Anthropic(), "Where is my order B-1001?")
    assert got == "Order B-1001 (Arc floor lamp, $89.00) is currently shipped. Its shipment ID is SHP-1003.", f"got {got!r}"
    assert len(_sim.calls) == 2, f"expected 2 API calls, got {len(_sim.calls)}"
    first, second = _sim.calls[0]["params"], _sim.calls[1]["params"]
    for req in (first, second):
        assert req["model"] == "claude-opus-5-5" and req["max_tokens"] >= 4096 and req.get("system") == SYSTEM_PROMPT
        assert req.get("tools") == [LOOKUP_ORDER_TOOL], "send the same tools on both requests"
    roles = [m["role"] for m in second["messages"]]
    assert roles == ["user", "assistant", "user"], f"second request roles: {roles}"
    assert [b["type"] for b in second["messages"][1]["content"]] == ["thinking", "text", "tool_use"], "append Claude's full turn"


def test_answer_error_and_no_tool():
    """Unknown orders produce an is_error result; questions without an order skip tools"""
    _fresh()
    got = answer(anthropic.Anthropic(), "Status of B-9999?")
    assert "couldn't find" in got, f"got {got!r}"
    result = _sim.last_request()["messages"][-1]["content"][0]
    assert result.get("is_error") is True
    _fresh()
    got = answer(anthropic.Anthropic(), "Hi there")
    assert got.startswith("Happy to help") and len(_sim.calls) == 1, "no tool_use means one call and return the text"


def test_parallel_tool_calls_answered_together():
    """Two tool_use blocks in one turn get two results in ONE user message"""
    _fresh()
    _sim.queue(_sim.message(_sim.tool_use("lookup_order", {"order_id": "B-1001"}, id="t1"),
                            _sim.tool_use("lookup_order", {"order_id": "B-1004"}, id="t2")),
               "Both orders are on their way.")
    got = answer(anthropic.Anthropic(), "Check B-1001 and B-1004")
    assert got == "Both orders are on their way."
    last = _sim.last_request()["messages"][-1]["content"]
    assert [r["tool_use_id"] for r in last] == ["t1", "t2"], "send every tool_result in a single user message"
