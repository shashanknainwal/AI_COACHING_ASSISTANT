import anthropic
from anthropic import _sim

_NOTES = "Customer: Acme Freight\nGoals: reduce detention fees\nRisks: no API docs\n"


def _call(reply=None):
    _sim.reset()
    if reply is not None:
        _sim.queue(reply)
    else:
        _sim.queue(_sim.message(_sim.thinking(""), _sim.text("  Acme wants lower detention fees.  ")))
    out = summarize_for_exec(anthropic.Anthropic(), _NOTES)
    assert _sim.calls, "summarize_for_exec() never called client.messages.create"
    return out, _sim.last_request()


def test_system_prompt():
    """SYSTEM_PROMPT is a real prompt aimed at an executive"""
    assert isinstance(SYSTEM_PROMPT, str) and len(SYSTEM_PROMPT.strip()) >= 30, \
        "SYSTEM_PROMPT should be a descriptive string (at least a sentence)"
    assert "executive" in SYSTEM_PROMPT.lower(), "SYSTEM_PROMPT should mention the executive audience"


def test_request_parameters():
    """Calls messages.create with the right model, max_tokens and system prompt"""
    _, req = _call()
    assert req["model"] == "claude-opus-5-5", f"model should be 'claude-opus-5-5', got {req['model']!r}"
    assert req["max_tokens"] >= 1024, f"max_tokens should be at least 1024, got {req['max_tokens']}"
    assert req.get("system") == SYSTEM_PROMPT, "pass SYSTEM_PROMPT as the system= parameter"


def test_single_user_message_with_notes():
    """Sends one user message that contains the notes"""
    _, req = _call()
    msgs = req["messages"]
    assert len(msgs) == 1, f"expected exactly 1 message, got {len(msgs)}"
    assert msgs[0]["role"] == "user", f"the message role should be 'user', got {msgs[0]['role']!r}"
    content = msgs[0]["content"]
    text = content if isinstance(content, str) else " ".join(b.get("text", "") for b in content)
    assert _NOTES.strip() in text, "the user message should include the full notes text"


def test_returns_text_not_thinking():
    """Returns the text blocks' content (skipping the thinking block), stripped"""
    out, _ = _call()
    assert out == "Acme wants lower detention fees.", \
        f"expected the stripped text block, got {out!r}. Are you reading content[0]? It's a thinking block."


def test_joins_multiple_text_blocks():
    """Joins all text blocks in order"""
    out, _ = _call(_sim.message(_sim.thinking(""), _sim.text("Part one. "), _sim.text("Part two.")))
    assert out == "Part one. Part two.", f"expected 'Part one. Part two.', got {out!r}"


def test_refusal_returns_none():
    """Returns None when stop_reason is 'refusal'"""
    out, _ = _call(_sim.refusal())
    assert out is None, f"expected None for a refusal, got {out!r}"


def test_estimate_cost_default_prices():
    """estimate_cost() uses $4 / $20 per million tokens by default"""
    usage = anthropic.Usage(input_tokens=2000, output_tokens=500)
    got = estimate_cost(usage)
    assert got == 0.018, f"2,000 in + 500 out at $4/$20 per MTok should be 0.018, got {got!r}"


def test_estimate_cost_custom_prices_and_rounding():
    """estimate_cost() accepts custom prices and rounds to 6 decimals"""
    usage = anthropic.Usage(input_tokens=1234, output_tokens=567)
    got = estimate_cost(usage, input_price=2.0, output_price=10.0)
    assert got == 0.008138, f"expected 0.008138, got {got!r}"
