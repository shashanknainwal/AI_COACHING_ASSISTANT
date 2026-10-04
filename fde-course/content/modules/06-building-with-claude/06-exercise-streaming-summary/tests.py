import anthropic
from anthropic import _sim


def _fresh():
    _sim.calls.clear()
    _sim._queue.clear()


def test_make_collector():
    """make_collector() returns a callback and the list it fills"""
    result = make_collector()
    assert isinstance(result, tuple) and len(result) == 2, "return a tuple (on_text, chunks)"
    on_text, chunks = result
    on_text("a")
    on_text("b")
    assert chunks == ["a", "b"], f"got {chunks}"
    other_fn, other_chunks = make_collector()
    assert other_chunks == [], "each collector gets its own list"


def test_uses_streaming_with_right_params():
    """stream_summary() uses messages.stream with a large max_tokens and the transcript in tags"""
    _fresh()
    on_text, _ = make_collector()
    stream_summary(anthropic.Anthropic(), "Leo: ATM is down.", on_text)
    call = _sim.calls[-1]
    assert call["stream"] is True, "use client.messages.stream(...), not create()"
    req = call["params"]
    assert req["model"] == "claude-opus-5-5" and req["max_tokens"] >= 32000, f"max_tokens should be at least 32000, got {req['max_tokens']}"
    assert req.get("system") == SYSTEM_PROMPT
    assert req["messages"] == [{"role": "user", "content": "<transcript>\nLeo: ATM is down.\n</transcript>"}]


def test_callback_gets_every_piece():
    """on_text receives every piece, and the pieces add up to the final text"""
    _fresh()
    on_text, chunks = make_collector()
    result = stream_summary(anthropic.Anthropic(), TRANSCRIPT, on_text)
    assert len(chunks) > 5, f"expected many streamed pieces, got {len(chunks)}"
    assert "".join(chunks) == result["text"], "the streamed pieces should add up to the final text"
    assert result["text"].startswith("Stand-up summary (Mar 12)."), f"text: {result['text'][:40]!r}"


def test_result_fields():
    """The result reports stop_reason, output tokens and truncated"""
    _fresh()
    on_text, _ = make_collector()
    result = stream_summary(anthropic.Anthropic(), TRANSCRIPT, on_text)
    assert set(result) == {"text", "stop_reason", "output_tokens", "truncated"}, f"keys: {sorted(result)}"
    assert result["stop_reason"] == "end_turn" and result["truncated"] is False
    assert isinstance(result["output_tokens"], int) and result["output_tokens"] > 0


def test_truncated_stream_is_flagged():
    """A stream that ends with max_tokens is flagged as truncated"""
    _fresh()
    _sim.queue(_sim.message(_sim.text("Stand-up summary: the backlog"), stop_reason="max_tokens"))
    on_text, chunks = make_collector()
    result = stream_summary(anthropic.Anthropic(), TRANSCRIPT, on_text)
    assert result["truncated"] is True and result["stop_reason"] == "max_tokens", f"got {result}"
    assert "".join(chunks) == "Stand-up summary: the backlog"
