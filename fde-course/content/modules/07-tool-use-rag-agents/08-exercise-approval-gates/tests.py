import anthropic
from anthropic import _sim


def _fresh():
    reset_data()
    _sim.calls.clear()
    _sim._queue.clear()


def _customers():
    """The learner's current CUSTOMERS dict (reset_data() rebinds it)."""
    return reset_data.__globals__["CUSTOMERS"]


def _block(name, tool_input, id="tu_1"):
    return anthropic.ToolUseBlock(name, tool_input, id=id)


class _Reviewer:
    """Records every request and answers with a fixed decision."""

    def __init__(self, decision):
        self.decision, self.requests = decision, []

    def __call__(self, request):
        self.requests.append(request)
        return self.decision


def test_needs_approval():
    """Only store credit above AUTO_APPROVE_LIMIT needs a human"""
    assert needs_approval("issue_store_credit", {"customer_id": "C-100", "amount": 75, "reason": "goodwill"}) is True
    assert needs_approval("issue_store_credit", {"customer_id": "C-100", "amount": 50, "reason": "goodwill"}) is False, \
        "exactly $50 is within the agent's own limit"
    assert needs_approval("issue_store_credit", {"customer_id": "C-100", "amount": 50.01, "reason": "goodwill"}) is True
    assert needs_approval("lookup_order", {"order_id": "B-1001"}) is False, "reads never need approval"
    assert needs_approval("track_shipment", {"shipment_id": "SHP-1003"}) is False


def test_describe_action():
    """describe_action() gives the reviewer the facts they need"""
    _fresh()
    _customers()["C-101"]["store_credit"] = 15.0
    got = describe_action("issue_store_credit", {"customer_id": "C-101", "amount": 80, "reason": "damaged_item"})
    assert got == "Issue $80.00 store credit to Ben Ito (C-101, standard) for damaged_item. Current balance: $15.00.", f"got {got!r}"
    got = describe_action("issue_store_credit", {"customer_id": "C-777", "amount": 60.5, "reason": "goodwill"})
    assert got == "Issue $60.50 store credit to unknown customer C-777 for goodwill.", f"got {got!r}"
    got = describe_action("lookup_order", {"order_id": "B-1001"})
    assert got == 'Run lookup_order with {"order_id": "B-1001"}', f"got {got!r}"


def test_reads_and_small_credits_skip_the_reviewer():
    """Reads and credits up to $50 run without asking, and are audited"""
    _fresh()
    reviewer, audit = _Reviewer(False), []
    r1 = guarded_execute(_block("lookup_order", {"order_id": "B-1002"}, "a"), reviewer, audit)
    r2 = guarded_execute(_block("issue_store_credit", {"customer_id": "C-102", "amount": 20, "reason": "late_delivery"}, "b"), reviewer, audit)
    assert reviewer.requests == [], "don't ask a human about reads or small credits"
    assert r1["tool_use_id"] == "a" and "is_error" not in r1 and '"delivered"' in r1["content"]
    assert r2["tool_use_id"] == "b" and _customers()["C-102"]["store_credit"] == 20.0
    assert audit == [
        {"tool": "lookup_order", "input": {"order_id": "B-1002"}, "approval": "not_required", "is_error": False},
        {"tool": "issue_store_credit", "input": {"customer_id": "C-102", "amount": 20, "reason": "late_delivery"},
         "approval": "auto", "is_error": False},
    ], f"audit: {audit}"


def test_approved_credit_runs():
    """An approved large credit runs, and the reviewer saw the summary"""
    _fresh()
    reviewer, audit = _Reviewer(True), []
    inp = {"customer_id": "C-100", "amount": 120, "reason": "damaged_item"}
    result = guarded_execute(_block("issue_store_credit", inp), reviewer, audit)
    assert reviewer.requests == [{"tool": "issue_store_credit", "input": inp,
                                  "summary": "Issue $120.00 store credit to Maya Okafor (C-100, gold) for damaged_item. Current balance: $0.00."}], \
        f"reviewer got {reviewer.requests}"
    assert "is_error" not in result and _customers()["C-100"]["store_credit"] == 120.0
    assert audit == [{"tool": "issue_store_credit", "input": inp, "approval": "approved", "is_error": False}], f"audit: {audit}"


def test_declined_credit_never_runs():
    """A declined credit returns DECLINED_MESSAGE as an error and changes nothing"""
    _fresh()
    audit = []
    inp = {"customer_id": "C-100", "amount": 75, "reason": "goodwill"}
    result = guarded_execute(_block("issue_store_credit", inp, "d"), _Reviewer(False), audit)
    assert result == {"type": "tool_result", "tool_use_id": "d", "content": DECLINED_MESSAGE, "is_error": True}, f"got {result}"
    assert _customers()["C-100"]["store_credit"] == 0.0, "a declined credit must not be issued"
    assert audit == [{"tool": "issue_store_credit", "input": inp, "approval": "declined", "is_error": True}], f"audit: {audit}"


def test_fail_closed():
    """Anything but an explicit True (errors, None, "yes") counts as declined"""
    def broken(request):
        raise TimeoutError("approval service down")

    for approver in (broken, _Reviewer(None), _Reviewer("yes"), _Reviewer(1)):
        _fresh()
        audit = []
        result = guarded_execute(_block("issue_store_credit", {"customer_id": "C-101", "amount": 90, "reason": "goodwill"}),
                                 approver, audit)
        assert result.get("is_error") is True and result["content"] == DECLINED_MESSAGE, f"approver {approver}: {result}"
        assert _customers()["C-101"]["store_credit"] == 15.0 and audit[0]["approval"] == "declined"


def test_hard_limit_still_applies():
    """Approval doesn't bypass the tool's own HARD_LIMIT check"""
    _fresh()
    audit = []
    result = guarded_execute(_block("issue_store_credit", {"customer_id": "C-100", "amount": 500, "reason": "goodwill"}),
                             _Reviewer(True), audit)
    assert result.get("is_error") is True and result["content"] == "amount must be between 0 and 200", f"got {result}"
    assert audit[0]["approval"] == "approved" and audit[0]["is_error"] is True
    assert _customers()["C-100"]["store_credit"] == 0.0


def test_agent_end_to_end():
    """In the full agent, a declined $75 request ends with a hand-off, not a credit"""
    _fresh()
    reviewer = _Reviewer(False)
    out = run_agent(anthropic.Anthropic(), "My rug B-1004 arrived damaged. I'd like $75 in store credit.", reviewer)
    assert out["answer"] == "I've sent your request to a teammate, who will follow up within one business day.", f"answer: {out['answer']!r}"
    assert [(e["tool"], e["approval"]) for e in out["audit"]] == [("lookup_order", "not_required"), ("issue_store_credit", "declined")], \
        f"audit: {out['audit']}"
    assert len(reviewer.requests) == 1 and _customers()["C-102"]["store_credit"] == 0.0
    result = _sim.last_request()["messages"][-1]["content"][0]
    assert result["is_error"] is True and result["content"] == DECLINED_MESSAGE, "Claude must be told about the decline"
