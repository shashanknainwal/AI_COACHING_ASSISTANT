import copy
import anthropic
from anthropic import _sim

SMALL = "Booking RT5V1C: my flight moved by 9 hours. Please refund the $150 change fee I paid."
BIG = "Booking FW7Q2K: the airline cancelled my flight. Please refund the full fare."
MIXED = "Please cancel booking HX3M8P and refund the $45 seat upgrade I never got."


def _fresh():
    reset_data()
    _sim.calls.clear()
    _sim._queue.clear()


def _start(question):
    audit = []
    out = start(anthropic.Anthropic(), question, audit)
    assert isinstance(out, tuple) and len(out) == 2 and isinstance(out[0], dict), f"start() should return (outcome, state), got {out!r}"
    return out[0], out[1], audit


def _pending_id(outcome):
    assert outcome.get("status") == "awaiting_approval" and outcome.get("pending"), \
        f"expected the run to pause with a pending call, got status {outcome.get('status')!r}"
    return outcome["pending"][0]["id"]


def test_requires_approval_policy():
    """requires_approval() flags cancellations and refunds over $200, nothing else"""
    cases = [
        ("get_booking", {"booking_ref": "FW7Q2K"}, False),
        ("issue_refund", {"booking_ref": "FW7Q2K", "amount": 150, "reason": "goodwill"}, False),
        ("issue_refund", {"booking_ref": "FW7Q2K", "amount": 200, "reason": "goodwill"}, False),
        ("issue_refund", {"booking_ref": "FW7Q2K", "amount": 200.01, "reason": "goodwill"}, True),
        ("issue_refund", {"booking_ref": "FW7Q2K", "amount": 612, "reason": "airline_cancellation"}, True),
        ("cancel_booking", {"booking_ref": "FW7Q2K"}, True),
    ]
    for name, inp, want in cases:
        got = requires_approval(name, inp)
        assert got is want, f"requires_approval({name!r}, {inp}) should be {want}, got {got!r}"


def test_small_refund_runs_without_pausing():
    """A $150 refund completes in one go and is audited as 'auto'"""
    _fresh()
    outcome, state, audit = _start(SMALL)
    assert outcome["status"] == "completed", f"status: {outcome['status']!r}"
    assert "$150.00" in (outcome.get("answer") or ""), f"answer: {outcome['answer']!r}"
    assert [(r["booking_ref"], r["amount"]) for r in REFUNDS] == [("RT5V1C", 150.0)], f"ledger: {REFUNDS}"
    assert [(a["tool"], a["decision"], a["approver"], a["is_error"]) for a in audit] == [
        ("get_booking", "auto", None, False), ("issue_refund", "auto", None, False)], f"audit: {audit}"


def test_big_refund_pauses_before_running():
    """A $612 refund pauses for approval and no money moves"""
    _fresh()
    outcome, state, audit = _start(BIG)
    assert outcome["status"] == "awaiting_approval", f"status: {outcome['status']!r}"
    assert REFUNDS == [], "the refund ran without approval"
    assert len(outcome["pending"]) == 1, f"pending: {outcome['pending']}"
    p = outcome["pending"][0]
    assert p["tool"] == "issue_refund" and p["input"]["amount"] == 612.0 and p["id"].startswith("toolu_"), f"pending entry: {p}"
    assert p["summary"] == "Refund $612.00 to Ana Souza (FW7Q2K, fare paid $612.00) for airline_cancellation.", \
        f"use describe() for the summary: {p['summary']!r}"
    assert len(_sim.calls) == 2, "pause right after the turn that asked for the risky call"
    assert state["messages"][-1]["role"] == "assistant", "while paused, the conversation ends with Claude's tool_use turn"
    assert [a["tool"] for a in audit] == ["get_booking"], f"only resolved calls go in the audit log: {audit}"


def test_approve_then_continue():
    """resume() with approved=True runs the refund, audits the approver, and finishes"""
    _fresh()
    outcome, state, audit = _start(BIG)
    pid = _pending_id(outcome)
    final = resume(anthropic.Anthropic(), state, {pid: {"approved": True, "approver": "maria.chen"}}, audit)
    assert final and final["status"] == "completed", f"got {final!r}"
    assert [(r["amount"], r["idempotency_key"]) for r in REFUNDS] == [(612.0, pid)], f"ledger: {REFUNDS}"
    assert audit[-1] == {"tool": "issue_refund", "input": {"booking_ref": "FW7Q2K", "amount": 612.0, "reason": "airline_cancellation"},
                         "decision": "approved", "approver": "maria.chen", "is_error": False}, f"audit: {audit[-1]}"
    assert "$612.00" in final["answer"], f"answer: {final['answer']!r}"


def test_fail_closed():
    """Anything but approved=True (missing, 'yes', None, False) declines the call"""
    for decisions in ({}, {"X": {"approved": True}}, "yes", None, False):
        _fresh()
        outcome, state, audit = _start(BIG)
        pid = _pending_id(outcome)
        d = decisions if isinstance(decisions, dict) else {pid: {"approved": decisions, "approver": "bot"}}
        final = resume(anthropic.Anthropic(), state, d, audit)
        assert REFUNDS == [], f"decisions {d} must not move money"
        sent = _sim.calls[-1]["params"]["messages"][-1]["content"]
        assert sent == [{"type": "tool_result", "tool_use_id": pid, "content": DECLINED_MESSAGE, "is_error": True}], \
            f"a declined call goes back as an is_error tool_result with DECLINED_MESSAGE: {sent}"
        assert audit[-1]["decision"] == "declined" and audit[-1]["is_error"] is True, f"audit: {audit[-1]}"
        assert final["status"] == "completed" and "teammate" in final["answer"]


def test_parallel_turn_with_one_risky_call():
    """Safe calls in the same turn run now; all results go back together, in order, after the decision"""
    _fresh()
    outcome, state, audit = _start(MIXED)
    assert outcome["status"] == "awaiting_approval", f"status: {outcome['status']!r}"
    assert [p["tool"] for p in outcome["pending"]] == ["cancel_booking"], f"only the cancellation needs approval: {outcome['pending']}"
    assert [r["amount"] for r in REFUNDS] == [45.0], "the $45 refund is under the limit: run it now"
    assert BOOKINGS["HX3M8P"]["status"] == "confirmed", "the cancellation ran without approval"
    turn = state["messages"][-1]["content"]
    ids = [b.id for b in turn if b.type == "tool_use"]
    pid = _pending_id(outcome)
    final = resume(anthropic.Anthropic(), state, {pid: {"approved": True, "approver": "maria.chen"}}, audit)
    sent = _sim.calls[-1]["params"]["messages"][-1]["content"]
    assert [r["tool_use_id"] for r in sent] == ids, "send ALL results for that turn in one user message, in tool_use order"
    assert BOOKINGS["HX3M8P"]["status"] == "cancelled" and final["status"] == "completed"
    assert [(a["tool"], a["decision"]) for a in audit] == [
        ("get_booking", "auto"), ("issue_refund", "auto"), ("cancel_booking", "approved")], f"audit: {audit}"


def test_no_double_execution():
    """Resuming twice can't run a refund twice"""
    _fresh()
    outcome, state, audit = _start(BIG)
    pid = _pending_id(outcome)
    approve = {pid: {"approved": True, "approver": "maria.chen"}}
    replay = copy.deepcopy(state)          # e.g. a retried webhook holding an old copy of the state
    resume(anthropic.Anthropic(), state, approve, audit)
    try:
        resume(anthropic.Anthropic(), state, approve, audit)
    except ValueError as exc:
        assert str(exc) == "no pending approvals", f"message: {exc}"
    else:
        raise AssertionError("resume() on a state with nothing pending should raise ValueError('no pending approvals')")
    resume(anthropic.Anthropic(), replay, approve, [])
    assert len(REFUNDS) == 1, f"the refund ran {len(REFUNDS)} times; run it through execute() with the original tool_use id"


def test_requests_are_well_formed():
    """Every request sends MODEL, SYSTEM_PROMPT, TOOLS and the shared conversation"""
    _fresh()
    outcome, state, audit = _start(BIG)
    resume(anthropic.Anthropic(), state, {_pending_id(outcome): {"approved": True, "approver": "m"}}, audit)
    assert len(_sim.calls) == 3, f"expected 3 API calls across start and resume, got {len(_sim.calls)}"
    for c in _sim.calls:
        p = c["params"]
        assert p["model"] == MODEL and p.get("system") == SYSTEM_PROMPT and p.get("tools") == TOOLS
        tc = p.get("tool_choice")
        assert tc is None or tc.get("type") == "auto", "don't force tool_choice"
    assert state["iterations"] == 3, "count API calls in state['iterations'] across pauses"


def test_iteration_cap_survives_pauses():
    """The loop stops at MAX_ITERATIONS with status 'max_iterations'"""
    _fresh()
    for i in range(MAX_ITERATIONS + 2):
        _sim.queue(_sim.message(_sim.tool_use("get_booking", {"booking_ref": "FW7Q2K"}, id=f"cap{i}")))
    outcome, state, audit = _start("Check FW7Q2K forever")
    assert outcome["status"] == "max_iterations", f"status: {outcome['status']!r}"
    assert len(_sim.calls) == MAX_ITERATIONS, f"made {len(_sim.calls)} API calls; the cap is {MAX_ITERATIONS}"
