import json
import anthropic
from anthropic import _sim


def _fresh():
    _sim.calls.clear()
    _sim._queue.clear()


def _block(name, inp, id="tu_1"):
    return anthropic.ToolUseBlock(name, inp, id=id)


class Reviewer:
    def __init__(self, decision):
        self.decision, self.requests = decision, []

    def __call__(self, request):
        self.requests.append(request)
        return self.decision


def _tools(result):
    return [(a["tool"], a["is_error"]) for a in result["audit"]]


def test_notify_customer_guardrails():
    """notify_customer() blocks compensation promises and long messages"""
    assert notify_customer("NS-2001", "Your shipment is delayed by weather.") == {"status": "queued", "to": "ops@halvorsen.example"}
    for text, word in [("We'll REFUND you.", "refund"), ("A credit is on the way", "credit"), ("We guarantee Friday", "guarantee"),
                       ("Here's a discount code", "discount"), ("Compensation will follow", "compensation"), ("We'll credit you", "credit")]:
        try:
            notify_customer("NS-2001", text)
        except ValueError as e:
            assert str(e) == f"message must not promise compensation (found '{word}')", f"{text!r}: {e}"
        else:
            raise AssertionError(f"{text!r} should be blocked")
    try:
        notify_customer("NS-2001", "x" * 601)
    except ValueError as e:
        assert str(e) == "message is 601 characters; the limit is 600", f"got {e}"
    else:
        raise AssertionError("messages over 600 characters should be blocked")
    try:
        notify_customer("NS-0000", "hi")
    except KeyError as e:
        assert e.args[0] == "No shipment found with ID NS-0000."
    else:
        raise AssertionError("unknown shipments raise KeyError")


def test_guarded_execute_reads_and_errors():
    """guarded_execute() runs tools, audits them, and turns failures into is_error results"""
    audit = []
    ok = guarded_execute(_block("get_shipment", {"shipment_id": "NS-2003"}, "a"), Reviewer(False), audit)
    assert ok["tool_use_id"] == "a" and "is_error" not in ok and json.loads(ok["content"])["event_code"] == "DAMAGE"
    bad = guarded_execute(_block("notify_customer", {"shipment_id": "NS-2003", "message": "Refund coming"}, "b"), Reviewer(False), audit)
    assert bad == {"type": "tool_result", "tool_use_id": "b", "content": "message must not promise compensation (found 'refund')",
                   "is_error": True}, f"got {bad}"
    unknown = guarded_execute(_block("delete_shipment", {}, "c"), Reviewer(False), audit)
    assert unknown["is_error"] is True and unknown["content"] == "Unknown tool: delete_shipment"
    assert [(a["tool"], a["approval"], a["is_error"]) for a in audit] == [
        ("get_shipment", "not_required", False), ("notify_customer", "not_required", True), ("delete_shipment", "not_required", True)]
    assert audit[0]["input"] == {"shipment_id": "NS-2003"}


def test_reroute_needs_approval():
    """reroute_shipment runs only with an explicit True from the approver (fail closed)"""
    inp = {"shipment_id": "NS-2006", "carrier": "FastFreight"}
    yes, audit = Reviewer(True), []
    r = guarded_execute(_block("reroute_shipment", inp), yes, audit)
    assert yes.requests == [{"tool": "reroute_shipment", "input": inp}] and "is_error" not in r
    assert audit == [{"tool": "reroute_shipment", "input": inp, "approval": "approved", "is_error": False}]

    def broken(request):
        raise TimeoutError("approval service down")

    for approver in (Reviewer(False), Reviewer("yes"), broken):
        audit = []
        r = guarded_execute(_block("reroute_shipment", inp, "d"), approver, audit)
        assert r == {"type": "tool_result", "tool_use_id": "d", "content": DECLINED, "is_error": True}, f"got {r}"
        assert audit[0]["approval"] == "declined"
    reader = Reviewer(True)
    guarded_execute(_block("get_shipment", {"shipment_id": "NS-2001"}), reader, [])
    assert reader.requests == [], "reads never ask for approval"


def test_run_triage_platinum_delay():
    """A platinum delay: notify, P1 ticket, decision recorded"""
    _fresh()
    out = run_triage(anthropic.Anthropic(), "NS-2001", Reviewer(True))
    assert set(out) == {"decision", "steps", "audit"}, f"keys {set(out)}"
    assert out["decision"] == {"action": "notify_and_ticket", "priority": "P1", "reason": "Delay for a platinum customer."}
    assert _tools(out) == [("get_shipment", False), ("notify_customer", False), ("create_ops_ticket", False), ("record_decision", False)]
    assert out["steps"] == 5 and len(_sim.calls) == 5
    for c in _sim.calls:
        p = c["params"]
        assert p["model"] == MODEL and p["max_tokens"] >= 4096 and p.get("system") == SYSTEM_PROMPT and p.get("tools") == TOOLS


def test_run_triage_guardrail_recovery():
    """The blocked credit promise goes back as an error and Claude rewrites the message"""
    _fresh()
    out = run_triage(anthropic.Anthropic(), "NS-2005", Reviewer(True))
    assert _tools(out) == [("get_shipment", False), ("notify_customer", True), ("notify_customer", False), ("record_decision", False)]
    assert out["decision"]["action"] == "notify_only"


def test_run_triage_declined_reroute():
    """A declined reroute leads to a P1 ticket and an escalation"""
    _fresh()
    reviewer = Reviewer(False)
    out = run_triage(anthropic.Anthropic(), "NS-2006", reviewer)
    assert len(reviewer.requests) == 1
    assert _tools(out) == [("get_shipment", False), ("reroute_shipment", True), ("create_ops_ticket", False), ("record_decision", False)]
    assert out["decision"] == {"action": "escalate", "priority": "P1", "reason": "Reroute declined; a coordinator must act."}


def test_run_triage_no_decision_and_limit():
    """No record_decision means decision None; endless tool calls raise RuntimeError"""
    _fresh()
    _sim.queue(_sim.message(_sim.tool_use("get_shipment", {"shipment_id": "NS-2002"})), "All good.")
    out = run_triage(anthropic.Anthropic(), "NS-2002", Reviewer(True))
    assert out["decision"] is None and out["steps"] == 2
    _fresh()
    for i in range(4):
        _sim.queue(_sim.message(_sim.tool_use("get_shipment", {"shipment_id": "NS-2002"}, id=f"l{i}")))
    try:
        run_triage(anthropic.Anthropic(), "NS-2002", Reviewer(True), max_steps=3)
    except RuntimeError as e:
        assert str(e) == "triage did not finish within max_steps"
    else:
        raise AssertionError("raise RuntimeError after max_steps API calls")
    assert len(_sim.calls) == 3
