def _c():
    return StreamClient()


def _ev(t, d, i=None):
    return {"type": t, "data": d, "id": i}


# Level 1 ----------------------------------------------------------------
def test_l1_single_event():
    """A data line and a blank line dispatch one message event"""
    c = _c()
    assert c.feed(1, "data: hello\n") == [], "nothing until the blank line"
    assert c.feed(2, "\n") == [_ev("message", "hello")]


def test_l1_multiline_data_and_event_type():
    """Several data lines join with newlines; 'event' sets the type"""
    c = _c()
    out = c.feed(1, "event: update\ndata: line one\ndata: line two\n\ndata: next\n\n")
    assert out == [_ev("update", "line one\nline two"), _ev("message", "next")], "the type resets after each event"


def test_l1_chunks_split_anywhere():
    """Chunks can split lines and field names at any byte"""
    c = _c()
    stream = "event: a\ndata: xyz\n\ndata:  two spaces\n\n"
    out = []
    for i, ch in enumerate(stream):
        out += c.feed(i, ch)
    assert out == [_ev("a", "xyz"), _ev("message", " two spaces")], "only one leading space is removed"


def test_l1_all_three_line_endings():
    """CRLF, LF and bare CR all end lines, including a CRLF split across chunks"""
    c = _c()
    out = c.feed(1, "data: a\r\n\r\ndata: b\r\rdata: c\r")
    out += c.feed(2, "\n")
    out += c.feed(3, "\n")
    assert out == [_ev("message", "a"), _ev("message", "b"), _ev("message", "c")], \
        "a \\r at the end of a chunk followed by \\n at the start of the next is one line ending"


def test_l1_comments_unknown_fields_and_bare_field_names():
    """Comments and unknown fields are ignored; a line with no colon is a field with an empty value"""
    c = _c()
    out = c.feed(1, ": keep-alive\nfoo: bar\ndata\ndata\n\n")
    assert out == [_ev("message", "\n")], "two empty data lines give one newline"


def test_l1_no_data_no_event():
    """A blank line with no data buffered dispatches nothing and resets the type"""
    c = _c()
    assert c.feed(1, "event: ping\n\n\n") == []
    assert c.feed(2, "data: x\n\n") == [_ev("message", "x")], "the earlier 'event: ping' was reset"


def test_l1_byte_order_mark_is_skipped():
    """A BOM at the very start of the stream is ignored"""
    c = _c()
    assert c.feed(1, "﻿data: hi\n\n") == [_ev("message", "hi")]


# Level 2 ----------------------------------------------------------------
def test_l2_ids_persist_across_events():
    """An id applies to its event and to later events until a new id arrives"""
    c = _c()
    out = c.feed(1, "id: 1\ndata: a\n\ndata: b\n\nid: 2\ndata: c\n\n")
    assert out == [_ev("message", "a", "1"), _ev("message", "b", "1"), _ev("message", "c", "2")]
    assert c.last_event_id(2) == "2"


def test_l2_id_commits_at_blank_line():
    """An id line takes effect at the next blank line, even with no data"""
    c = _c()
    assert c.last_event_id(0) is None
    c.feed(1, "id: abc\n")
    assert c.last_event_id(2) is None, "not committed yet"
    c.feed(3, "\n")
    assert c.last_event_id(4) == "abc", "committed even though nothing was dispatched"


def test_l2_bad_id_and_empty_id():
    """An id containing NUL is ignored; an empty id resets to the empty string"""
    c = _c()
    c.feed(1, "id: 5\ndata: a\n\n")
    out = c.feed(2, "id: x\0y\ndata: b\n\n")
    assert out == [_ev("message", "b", "5")]
    out = c.feed(3, "id\ndata: c\n\n")
    assert out == [_ev("message", "c", "")]
    assert c.last_event_id(4) == ""


def test_l2_retry_field():
    """retry sets the reconnection delay only when it is all digits"""
    c = _c()
    assert c.retry_ms(0) == 3000
    c.feed(1, "retry: 1500\n")
    assert c.retry_ms(2) == 1500, "retry takes effect immediately"
    c.feed(3, "retry: 2s\nretry: -1\nretry:\n\n")
    assert c.retry_ms(4) == 1500


# Level 3 ----------------------------------------------------------------
def test_l3_disconnect_drops_partial_event():
    """A disconnect discards the partial line, data and uncommitted id"""
    c = _c()
    c.feed(1, "id: 1\ndata: ok\n\n")
    c.feed(2, "id: 2\ndata: half\nda")
    c.disconnect(3)
    assert c.last_event_id(3) == "1", "id 2 was never committed"
    assert c.feed(4, "ta: zombie\n\n") == [], "a closed connection delivers nothing"
    assert c.connect(3003) is True
    assert c.feed(3004, "data: fresh\n\n") == [_ev("message", "fresh", "1")]


def test_l3_reconnect_waits_retry():
    """disconnect returns when reconnecting is allowed; connect refuses earlier"""
    c = _c()
    c.feed(1, "retry: 1000\ndata: a\n\n")
    assert c.disconnect(10) == 1010
    assert c.connect(1009) is False
    assert c.connect(1010) is True
    assert c.connect(1011) is False, "already connected"


def test_l3_backoff_doubles_on_empty_connections():
    """Connections that deliver nothing double the delay, capped at 30000"""
    c = _c()
    c.feed(1, "retry: 4000\ndata: a\n\n")
    assert c.disconnect(2) == 4002, "this connection delivered an event: 4000"
    c.connect(4002)
    assert c.disconnect(4002) == 12002, "empty: 4000 * 2"
    c.connect(12002)
    assert c.disconnect(12002) == 28002, "second empty in a row: 4000 * 4"
    c.connect(28002)
    assert c.disconnect(28002) == 58002, "4000 * 8 = 32000 is capped at 30000"
    c.connect(58002)
    c.feed(58003, "data: back\n\n")
    assert c.disconnect(58004) == 62004, "an event resets the backoff"


def test_l3_headers_carry_last_event_id():
    """headers sends Last-Event-ID only when there is a non-empty id"""
    c = _c()
    assert c.headers(0) == {}
    c.feed(1, "id: 41\ndata: a\n\n")
    assert c.headers(2) == {"Last-Event-ID": "41"}
    c.feed(3, "id\ndata: b\n\n")
    assert c.headers(4) == {}


def test_l3_replayed_events_are_dropped():
    """After a reconnect, events whose own numeric id was already delivered are dropped"""
    c = _c()
    c.feed(1, "id: 1\ndata: a\n\nid: 2\ndata: b\n\n")
    c.disconnect(2)
    c.connect(3002)
    out = c.feed(3003, "id: 2\ndata: b\n\nid: 3\ndata: c\n\ndata: d\n\n")
    assert out == [_ev("message", "c", "3"), _ev("message", "d", "3")], "id 2 is a replay; 'd' has no id line of its own"
    assert c.last_event_id(3004) == "3"


def test_l3_dropped_replay_does_not_move_last_id_back():
    """A dropped replay leaves last_event_id alone"""
    c = _c()
    c.feed(1, "id: 7\ndata: a\n\n")
    c.feed(2, "id: 5\ndata: old\n\n")
    assert c.last_event_id(3) == "7"
    assert c.headers(4) == {"Last-Event-ID": "7"}


# Level 4 ----------------------------------------------------------------
def test_l4_assembles_a_message():
    """start, delta and stop events build a message"""
    c = _c()
    c.feed(1, 'event: start\ndata: {"msg": "m1"}\n\n')
    c.feed(2, 'event: delta\ndata: {"msg": "m1", "text": "Hel"}\n\nevent: delta\ndata: {"msg": "m1", "text": "lo"}\n\n')
    assert c.message(3, "m1") == {"text": "Hello", "done": False}
    c.feed(4, 'event: stop\ndata: {"msg": "m1"}\n\n')
    assert c.message(5, "m1") == {"text": "Hello", "done": True}
    assert c.completed(6) == ["m1"]
    assert c.message(7, "nope") is None


def test_l4_bad_events_are_counted_not_fatal():
    """Bad JSON, unknown messages and deltas after stop count as errors"""
    c = _c()
    c.feed(1, 'event: delta\ndata: {"msg": "ghost", "text": "x"}\n\n')
    c.feed(2, "event: delta\ndata: {not json\n\n")
    c.feed(3, 'event: start\ndata: {"msg": "m"}\n\nevent: stop\ndata: {"msg": "m"}\n\n')
    c.feed(4, 'event: delta\ndata: {"msg": "m", "text": "late"}\n\n')
    c.feed(5, 'event: start\ndata: {"msg": "m"}\n\n')
    c.feed(6, "event: ping\ndata: {}\n\n")
    assert c.errors(7) == 4, "ghost delta, bad JSON, delta after stop, duplicate start; ping is not an error"
    assert c.message(8, "m") == {"text": "", "done": True}


def test_l4_interleaved_messages():
    """Two messages can stream at once; completed lists them in stop order"""
    c = _c()
    c.feed(1, 'event: start\ndata: {"msg": "a"}\n\nevent: start\ndata: {"msg": "b"}\n\n')
    c.feed(2, 'event: delta\ndata: {"msg": "b", "text": "B"}\n\nevent: delta\ndata: {"msg": "a", "text": "A"}\n\n')
    c.feed(3, 'event: stop\ndata: {"msg": "b"}\n\nevent: stop\ndata: {"msg": "a"}\n\n')
    assert c.completed(4) == ["b", "a"]
    assert c.message(5, "a")["text"] == "A"


def test_l4_resume_after_reconnect_without_double_text():
    """A message survives a disconnect and the replayed deltas aren't applied twice"""
    c = _c()
    c.feed(1, 'id: 1\nevent: start\ndata: {"msg": "m"}\n\n')
    c.feed(2, 'id: 2\nevent: delta\ndata: {"msg": "m", "text": "The "}\n\n')
    c.feed(3, 'id: 3\nevent: delta\ndata: {"msg": "m", "text": "cat"}\r\n')
    c.disconnect(4)
    assert c.headers(5) == {"Last-Event-ID": "2"}
    assert c.message(5, "m") == {"text": "The ", "done": False}, "the half-received delta was discarded"
    c.connect(3004)
    stream = 'id: 2\nevent: delta\ndata: {"msg": "m", "text": "The "}\r\n\r\nid: 3\nevent: delta\ndata: {"msg": "m", "text": "cat"}\r\n\r\nid: 4\nevent: stop\ndata: {"msg": "m"}\r\n\r\n'
    for i in range(0, len(stream), 7):
        c.feed(3005 + i, stream[i:i + 7])
    assert c.message(4000, "m") == {"text": "The cat", "done": True}
    assert c.errors(4001) == 0
    assert c.last_event_id(4002) == "4"
