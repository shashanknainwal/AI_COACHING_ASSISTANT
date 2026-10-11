def _events(name):
    return list(iter_sse(stream_source(name)))


def test_iter_sse_reassembles_events():
    """iter_sse() rebuilds events across chunk boundaries, with CRLF and comment lines"""
    evs = _events("answer")
    names = [n for _, n, _ in evs]
    assert names[:3] == ["message_start", "ping", "content_block_start"], f"first events: {names[:3]}"
    assert names[-1] == "message_stop" and len(evs) == 15, f"expected 15 events ending in message_stop, got {len(evs)}: {names}"
    t, name, data = evs[0]
    assert t == 380 and data["message"]["usage"]["input_tokens"] == 2104, "an event's time is the time of the chunk that completed it"
    texts = [d["delta"].get("text") for _, n, d in evs if n == "content_block_delta" and d["delta"]["type"] == "text_delta"]
    assert texts == ["Your order PO-4471 ", "ships today. ", "", "Tracking follows by email."], f"text deltas: {texts}"


def test_iter_sse_is_lazy():
    """iter_sse() yields each event as soon as it completes, without reading ahead"""
    src = stream_source("long")
    gen = iter_sse(src)
    next(gen)
    assert _consumed["long"] <= 3, f"after the first event, only its chunks should be read (read {_consumed['long']})"


def test_consume_text_answer():
    """consume() rebuilds text and thinking blocks, cumulative usage and TTFT"""
    seen = []
    r = consume(stream_source("answer"), on_text=seen.append)
    assert r["status"] == "complete" and r["stop_reason"] == "end_turn", f"status {r['status']}, stop {r['stop_reason']}"
    assert r["text"] == "Your order PO-4471 ships today. Tracking follows by email.", r["text"]
    assert r["blocks"] == [
        {"type": "thinking", "thinking": "", "signature": "EqQBsim"},
        {"type": "text", "text": "Your order PO-4471 ships today. Tracking follows by email.", "citations": []},
    ], r["blocks"]
    assert r["usage"] == {"input_tokens": 2104, "output_tokens": 182}, f"usage in message_delta is cumulative: take the last value, {r['usage']}"
    assert r["ttft_ms"] == 2950, f"TTFT is the first non-empty text delta, not message_start or thinking: {r['ttft_ms']}"
    assert seen == ["Your order PO-4471 ", "ships today. ", "Tracking follows by email."], f"on_text gets each non-empty delta: {seen}"


def test_consume_tool_input():
    """consume() parses tool input JSON at block stop and ignores unknown event types"""
    r = consume(stream_source("tool"))
    assert r["status"] == "tool_use", r["status"]
    tool = r["blocks"][-1]
    assert tool == {"type": "tool_use", "id": "toolu_sim_01", "name": "check_stock",
                    "input": {"sku": "TS-CB-3C25", "qty": 150}}, tool
    assert len(r["blocks"]) == 3


def test_consume_truncated_tool():
    """consume() leaves a truncated tool input as None and reports max_tokens"""
    r = consume(stream_source("truncated"))
    assert r["status"] == "max_tokens", r["status"]
    assert r["blocks"][0]["input"] is None, "never hand a half-parsed tool input to your code"


def test_consume_error_and_drop():
    """consume() keeps partial text on an error event and flags a stream that just stops"""
    r = consume(stream_source("overloaded"))
    assert r["status"] == "error" and r["error"] == {"type": "overloaded_error", "message": "Overloaded"}, r
    assert r["text"] == "Cut-to-length cable can't be returned unless ", "keep partial text so you can resume"
    d = consume(stream_source("dropped"))
    assert d["status"] == "error" and d["error"]["type"] == "incomplete_stream", f"no message_stop means incomplete: {d['status']}, {d['error']}"
    assert d["text"] == "Your delivery window is Tuesday between "


def test_consume_refusal_discards_text():
    """consume() discards partial text on a refusal and keeps stop_details"""
    r = consume(stream_source("refusal"))
    assert r["status"] == "refusal", r["status"]
    assert r["text"] == "" and all(b["type"] != "text" for b in r["blocks"]), "treat partial output before a refusal as incomplete: discard it"
    assert r["stop_details"]["category"] == "general_harms", r["stop_details"]


def test_consume_citations():
    """consume() appends citations_delta citations to their text block"""
    r = consume(stream_source("cited"))
    block = r["blocks"][0]
    assert block["text"] == "Restocking is free for unopened items"
    assert [c["cited_text"] for c in block["citations"]] == ["Restocking is free for unopened stock items."], block


def test_consume_cancellation():
    """consume() stops reading and closes the stream when should_cancel says so"""
    r = consume(stream_source("long"), should_cancel=lambda text: len(text) > 40)
    assert r["status"] == "cancelled", r["status"]
    assert r["text"] == "word0 word1 word2 word3 word4 word5 word6 ", f"stop right after the delta that tripped the check: {r['text']!r}"
    assert _consumed["long"] < len(STREAMS["long"]) // 3, f"you kept reading after cancelling ({_consumed['long']} of {len(STREAMS['long'])} chunks)"
    assert _closed["long"], "close the source stream when you cancel"
