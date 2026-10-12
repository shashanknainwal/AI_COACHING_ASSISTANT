import json


def test_strip_cache_control():
    """strip_cache_control() removes markers at every depth and leaves the input untouched"""
    a, _ = PAIRS["growing"]
    out = strip_cache_control(a)
    assert "cache_control" not in json.dumps(out), "every cache_control key should be gone"
    assert "cache_control" in json.dumps(a), "don't modify the original body: return a copy"
    assert out["messages"][-1]["content"][0] == {"type": "text", "text": "And the cable line?"}


def test_segments_order_and_bytes():
    """segments() lists tools, then system blocks, then messages, serialized without sorting keys"""
    a, _ = PAIRS["growing"]
    segs = segments(a)
    paths = [p for p, _ in segs]
    assert paths[:4] == ["tools[0]", "tools[1]", "tools[2]", "system[0]"], f"cache order is tools, system, messages: {paths[:4]}"
    assert paths[4:] == [f"messages[{k}]" for k in range(5)], paths[4:]
    assert segs[0][1] == json.dumps(TOOLS[0], ensure_ascii=False, separators=(",", ":")), \
        "serialize with json.dumps(x, ensure_ascii=False, separators=(',', ':')) and keep the key order as sent"
    assert "cache_control" not in segs[3][1], "strip markers before serializing"
    s = segments({"model": "m", "system": "Plain string prompt", "messages": []})
    assert s == [("system", '"Plain string prompt"')], f"a string system prompt is one 'system' segment: {s}"


def test_no_divergence_cases():
    """first_divergence() returns None for a growing conversation and a moved marker"""
    assert first_divergence(*PAIRS["growing"]) is None, "b only appends turns after a's prefix: that's a cache hit"
    assert first_divergence(*PAIRS["marker_moved"]) is None, "a cache_control marker moving isn't a prefix change"


def test_timestamp_in_system():
    """first_divergence() finds the exact character where the system prompt changed"""
    a, b = PAIRS["timestamp"]
    d = first_divergence(a, b)
    text = json.dumps(strip_cache_control(a["system"][0]), ensure_ascii=False, separators=(",", ":"))
    expected = text.index("09:14:03") + 6
    assert d and d["section"] == "system" and d["path"] == "system[0]", d
    assert d["offset"] == expected, f"offset should point at the first differing character ({expected}), got {d['offset']}"
    assert d["a"].startswith("03Z") and d["b"].startswith("41Z"), f"snippets are 20 characters from the offset: {d}"
    assert diagnose(a, b) == "system_changed"


def test_tool_problems():
    """diagnose() tells tool order, key order and a changed tool set apart"""
    a, b = PAIRS["key_order"]
    assert a == b, "(Python dicts compare equal here: that's why == can't find this bug)"
    d = first_divergence(a, b)
    assert d and d["path"] == "tools[1]", f"key order changes the bytes of tools[1]: {d}"
    assert diagnose(*PAIRS["key_order"]) == "key_order"
    assert first_divergence(*PAIRS["tool_order"])["path"] == "tools[0]"
    assert diagnose(*PAIRS["tool_order"]) == "tool_order"
    assert diagnose(*PAIRS["tools_changed"]) == "tools_changed"


def test_history_and_model():
    """diagnose() spots an edited earlier turn and a model switch"""
    d = first_divergence(*PAIRS["history_trim"])
    assert d and d["path"] == "messages[2]" and d["section"] == "messages", d
    assert d["b"].startswith("...[trimmed]"), d
    assert diagnose(*PAIRS["history_trim"]) == "history_edited"
    m = first_divergence(*PAIRS["model_switch"])
    assert m == {"section": "model", "path": "model", "offset": 0, "a": "claude-sonnet-5-5", "b": "claude-haiku-5-5"}, m
    assert diagnose(*PAIRS["model_switch"]) == "model_switch"
    assert diagnose(*PAIRS["growing"]) == "none"


def test_shorter_second_request():
    """first_divergence() reports a request that dropped earlier messages"""
    a, _ = PAIRS["growing"]
    b = dict(a, messages=a["messages"][:2])
    d = first_divergence(a, b)
    assert d and d["path"] == "messages[2]" and d["offset"] == 0 and d["b"] == "", d
