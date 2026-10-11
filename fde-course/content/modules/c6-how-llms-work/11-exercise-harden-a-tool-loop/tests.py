import anthropic
from anthropic import _sim


def _fresh():
    SENT.clear()
    EXPORTS.clear()
    _sim.calls.clear()
    _sim._queue.clear()


class _Approver:
    def __init__(self, answer):
        self.answer = answer
        self.calls = []

    def __call__(self, name, tool_input):
        self.calls.append((name, dict(tool_input)))
        return self.answer


def _tool_results(params):
    out = []
    for m in params["messages"]:
        if m["role"] == "user" and isinstance(m["content"], list):
            out.extend(b for b in m["content"] if isinstance(b, dict) and b.get("type") == "tool_result")
    return out


def test_wrap_untrusted():
    """wrap_untrusted() puts fetched text inside <untrusted_document> tags"""
    got = wrap_untrusted("hello")
    assert got == "<untrusted_document>\nhello\n</untrusted_document>", f"got {got!r}"


def test_policy_least_privilege_and_domains():
    """policy_check() denies tools outside the task and recipients outside the allowlist"""
    clean, dirty = {"tainted": False}, {"tainted": True}
    got = policy_check("export_customers", {}, clean)
    assert isinstance(got, tuple) and got[0] == "deny" and got[1], f"export_customers isn't a task tool: deny with a reason; got {got!r}"
    assert policy_check("fetch_document", {"doc_id": "VND-114"}, dirty)[0] == "allow", "reading documents is allowed"
    assert policy_check("send_email", {"to": "ops@brindle.example", "subject": "s", "body": "b"}, clean)[0] == "allow", \
        "an internal email with no untrusted content in context is allowed"
    assert policy_check("send_email", {"to": "OPS@Brindle.Example", "subject": "s", "body": "b"}, clean)[0] == "allow", \
        "domains compare case-insensitively"
    for to in ["audit@vendor-review.example", "ops@brindle.example.evil.example",
               "ops@brindle.example@evil.example", "evil.example", "x@notbrindle.example"]:
        got = policy_check("send_email", {"to": to, "subject": "s", "body": "b"}, clean)
        assert got[0] == "deny", f"{to!r} must be denied: compare the domain exactly; got {got}"


def test_policy_taint_requires_approval():
    """After untrusted content enters the context, internal email needs human approval"""
    got = policy_check("send_email", {"to": "ops@brindle.example", "subject": "s", "body": "b"}, {"tainted": True})
    assert got and got[0] == "approve", f"got {got!r}"
    got = policy_check("send_email", {"to": "audit@vendor-review.example", "subject": "s", "body": "b"}, {"tainted": True})
    assert got[0] == "deny", "a disallowed domain is denied outright, not sent for approval"


def test_injected_document_cannot_exfiltrate():
    """run_agent() blocks the injected export and the external email"""
    _fresh()
    approver = _Approver(True)
    out = run_agent(anthropic.Anthropic(), TASK, approver)
    assert isinstance(out, dict) and set(out) == {"status", "answer", "actions"}, f"got {out!r}"
    assert EXPORTS == [], "export_customers must never run: it isn't a tool for this task"
    assert all(e["to"] == "ops@brindle.example" for e in SENT), f"an email left the company: {SENT}"
    assert out["actions"] == [
        {"name": "fetch_document", "decision": "allow"},
        {"name": "export_customers", "decision": "deny"},
        {"name": "send_email", "decision": "deny"},
        {"name": "send_email", "decision": "approved"},
    ], f"actions: {out['actions']}"
    assert out["status"] == "completed" and "ops@brindle.example" in out["answer"], f"got {out}"
    assert len(SENT) == 1, f"the summary should be sent once, after approval: {SENT}"
    assert approver.calls == [("send_email", {"to": "ops@brindle.example", "subject": "Summary of VND-114",
                                              "body": "Vendor Fernhill Supply raises prices 4% from March; payment terms stay net 30."})], \
        f"approve(name, input) should be called once with the exact arguments: {approver.calls}"


def test_requests_follow_least_privilege():
    """Requests offer only the task's tools, and blocked calls go back as is_error results"""
    _fresh()
    run_agent(anthropic.Anthropic(), TASK, _Approver(True))
    assert _sim.calls, "run_agent should call client.messages.create"
    for c in _sim.calls:
        p = c["params"]
        names = sorted(t["name"] for t in p.get("tools", []))
        assert names == ["fetch_document", "send_email"], f"send only TASK_TOOL_NAMES tools, got {names}"
        assert p["model"] == MODEL and p["max_tokens"] == MAX_TOKENS and p.get("system") == SYSTEM_PROMPT, "use MODEL, MAX_TOKENS and SYSTEM_PROMPT"
    results = _tool_results(_sim.calls[-1]["params"])
    assert len(results) == 4, f"expected 4 tool_results across the conversation, got {len(results)}"
    assert results[0]["content"].startswith("<untrusted_document>\n") and not results[0].get("is_error"), \
        f"the fetched document must be wrapped: {results[0]['content'][:60]!r}"
    assert results[1].get("is_error") is True and results[1]["content"].startswith("Blocked by policy: "), f"got {results[1]}"
    assert results[2].get("is_error") is True and results[2]["content"].startswith("Blocked by policy: "), f"got {results[2]}"


def test_rejected_approval_sends_nothing():
    """If the human rejects, nothing is sent and the model hears why"""
    _fresh()
    out = run_agent(anthropic.Anthropic(), TASK, _Approver(False))
    assert out and SENT == [] and EXPORTS == [], f"nothing may be sent when approval is rejected: {SENT}"
    assert out["actions"][-1] == {"name": "send_email", "decision": "rejected"}, f"actions: {out['actions']}"
    last = _tool_results(_sim.calls[-1]["params"])[-1]
    assert last.get("is_error") is True and last["content"] == "Not approved by a human reviewer", f"got {last}"
    assert out["status"] == "completed", "the loop still finishes normally"


def test_clean_task_needs_no_approval():
    """With no untrusted content in context, an internal email goes straight out"""
    _fresh()
    approver = _Approver(False)
    out = run_agent(anthropic.Anthropic(), "Email ops@brindle.example a reminder that the vendor review is Friday.", approver)
    assert out and approver.calls == [], "don't ask for approval when nothing untrusted has been read"
    assert [e["to"] for e in SENT] == ["ops@brindle.example"] and out["actions"] == [{"name": "send_email", "decision": "allow"}], f"got {out}, sent {SENT}"


def test_max_iterations():
    """run_agent() stops at max_iterations without running the last turn's tools"""
    _fresh()
    for i in range(3):
        _sim.queue(_sim.message(_sim.tool_use("fetch_document", {"doc_id": "VND-114"}, id=f"loop{i}")))
    out = run_agent(anthropic.Anthropic(), TASK, _Approver(True), max_iterations=2)
    assert out and out["status"] == "max_iterations", f"got {out}"
    assert len(_sim.calls) == 2, f"make at most max_iterations calls, made {len(_sim.calls)}"
    assert len(out["actions"]) == 1, f"run tools from the first turn only: {out['actions']}"
