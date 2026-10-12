import json

# Recorded event streams from Tallowmere's order-desk assistant (simulated).
# Each stream is a list of (t_ms, chunk) pairs: t_ms is when the chunk arrived,
# measured from the moment the request was sent. Chunks are raw text and do not
# line up with events: one chunk can end mid-line, another can hold two events.


def _ev(t, name, data, crlf=False, comment=False):
    text = (": keep-alive\n" if comment else "") + f"event: {name}\ndata: {json.dumps(data)}\n\n"
    return t, text.replace("\n", "\r\n") if crlf else text


def _start(t, inp=2104):
    return _ev(t, "message_start", {"type": "message_start", "message": {
        "id": "msg_sim_stream", "type": "message", "role": "assistant", "model": "claude-sonnet-5-5",
        "content": [], "stop_reason": None, "stop_sequence": None,
        "usage": {"input_tokens": inp, "output_tokens": 1}}})


def _bstart(t, i, block):
    return _ev(t, "content_block_start", {"type": "content_block_start", "index": i, "content_block": block})


def _delta(t, i, delta, **kw):
    return _ev(t, "content_block_delta", {"type": "content_block_delta", "index": i, "delta": delta}, **kw)


def _text(t, i, s, **kw):
    return _delta(t, i, {"type": "text_delta", "text": s}, **kw)


def _bstop(t, i):
    return _ev(t, "content_block_stop", {"type": "content_block_stop", "index": i})


def _mdelta(t, stop, out, details=None):
    return _ev(t, "message_delta", {"type": "message_delta",
                                    "delta": {"stop_reason": stop, "stop_sequence": None, "stop_details": details},
                                    "usage": {"output_tokens": out}})


def _mstop(t):
    return _ev(t, "message_stop", {"type": "message_stop"})


def _ping(t):
    return _ev(t, "ping", {"type": "ping"})


def _thinking(t, i):
    return [_bstart(t, i, {"type": "thinking", "thinking": "", "signature": ""}),
            _delta(t + 5, i, {"type": "thinking_delta", "thinking": ""}),
            _delta(t + 2400, i, {"type": "signature_delta", "signature": "EqQBsim"}),
            _bstop(t + 2400, i)]


def _chunk(events):
    """Split events into network chunks: some events split mid-line, same-time events merged."""
    pieces = []
    for n, (t, text) in enumerate(events):
        if n % 2 == 0 and len(text) > 30:
            a, b = len(text) // 3, 2 * len(text) // 3
            pieces += [(t - 2, text[:a]), (t - 1, text[a:b]), (t, text[b:])]   # the event completes at t
        else:
            pieces.append((t, text))
    merged = []
    for t, text in pieces:
        if merged and merged[-1][0] == t:
            merged[-1] = (t, merged[-1][1] + text)
        else:
            merged.append((t, text))
    return merged


_EVENTS = {
    "answer": [_start(380), _ping(390)] + _thinking(400, 0) + [
        _bstart(2950, 1, {"type": "text", "text": ""}),
        _text(2950, 1, "Your order PO-4471 ", crlf=True),
        _text(3010, 1, "ships today. ", comment=True),
        _text(3070, 1, ""),
        _text(3130, 1, "Tracking follows by email."),
        _bstop(3140, 1), _mdelta(3140, "end_turn", 96), _mdelta(3150, "end_turn", 182), _mstop(3150)],
    "tool": [_start(300, 3311)] + _thinking(310, 0) + [
        _bstart(2800, 1, {"type": "text", "text": ""}),
        _text(2800, 1, "Let me check stock."),
        _bstop(2820, 1),
        _ev(2830, "content_block_annotation", {"type": "content_block_annotation", "index": 1, "note": "future event type"}),
        _bstart(2900, 2, {"type": "tool_use", "id": "toolu_sim_01", "name": "check_stock", "input": {}}),
        _delta(2900, 2, {"type": "input_json_delta", "partial_json": ""}),
        _delta(3000, 2, {"type": "input_json_delta", "partial_json": "{\"sk"}),
        _delta(3100, 2, {"type": "input_json_delta", "partial_json": "u\": \"TS-CB-3C25\", "}),
        _delta(3200, 2, {"type": "input_json_delta", "partial_json": "\"qty\": 150}"}),
        _bstop(3210, 2), _mdelta(3220, "tool_use", 77), _mstop(3220)],
    "overloaded": [_start(350)] + _thinking(360, 0) + [
        _bstart(2700, 1, {"type": "text", "text": ""}),
        _text(2700, 1, "Cut-to-length cable "),
        _text(2760, 1, "can't be returned unless "),
        _ev(2900, "error", {"type": "error", "error": {"type": "overloaded_error", "message": "Overloaded"}})],
    "refusal": [_start(340)] + _thinking(350, 0) + [
        _bstart(2600, 1, {"type": "text", "text": ""}),
        _text(2600, 1, "Here is how to bypass the "),
        _text(2660, 1, "credit check on "),
        _bstop(2700, 1),
        _mdelta(2700, "refusal", 40, {"type": "refusal", "category": "general_harms", "explanation": "Declined by safety classifier."}),
        _mstop(2700)],
    "truncated": [_start(330)] + [
        _bstart(500, 0, {"type": "tool_use", "id": "toolu_sim_02", "name": "create_return", "input": {}}),
        _delta(600, 0, {"type": "input_json_delta", "partial_json": "{\"order\": \"PO-4471\", \"lines\": [{\"sku\": \"TS-CB"}),
        _bstop(650, 0), _mdelta(650, "max_tokens", 64), _mstop(650)],
    "cited": [_start(300)] + [
        _bstart(1200, 0, {"type": "text", "text": "", "citations": []}),
        _text(1200, 0, "Restocking is free for unopened items"),
        _delta(1260, 0, {"type": "citations_delta", "citation": {
            "type": "char_location", "cited_text": "Restocking is free for unopened stock items.",
            "document_index": 0, "document_title": "Returns policy v7", "start_char_index": 64, "end_char_index": 108}}),
        _bstop(1270, 0), _mdelta(1280, "end_turn", 30), _mstop(1280)],
    "dropped": [_start(320)] + [
        _bstart(900, 0, {"type": "text", "text": ""}),
        _text(900, 0, "Your delivery window is "),
        _text(960, 0, "Tuesday between ")],
    "long": [_start(310), _bstart(1500, 0, {"type": "text", "text": ""})] + [
        _text(1500 + 40 * i, 0, f"word{i} ") for i in range(60)] + [
        _bstop(4000, 0), _mdelta(4000, "end_turn", 120), _mstop(4000)],
}

STREAMS = {name: _chunk(events) for name, events in _EVENTS.items()}

_consumed = {}
_closed = {}


def stream_source(name):
    """A live-looking stream: yields (t_ms, chunk) and records how far it was read."""
    _consumed[name] = 0
    _closed[name] = False
    try:
        for item in STREAMS[name]:
            _consumed[name] += 1
            yield item
    finally:
        _closed[name] = True
