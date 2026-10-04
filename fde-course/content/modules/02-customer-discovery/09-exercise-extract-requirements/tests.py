import json
import anthropic
from anthropic import _sim


def _schema_props(node):
    return node.get("properties", {}) if isinstance(node, dict) else {}


def test_schema_top_level():
    """Schema: an object with requirements and open_questions arrays"""
    s = REQUIREMENTS_SCHEMA
    assert s.get("type") == "object", "the top-level schema should have type 'object'"
    assert set(_schema_props(s)) == {"requirements", "open_questions"}, f"top-level properties should be requirements and open_questions, got {sorted(_schema_props(s))}"
    assert sorted(s.get("required", [])) == ["open_questions", "requirements"], "both top-level properties should be required"
    assert s.get("additionalProperties") is False, "set additionalProperties to False on the top-level object"
    oq = _schema_props(s)["open_questions"]
    assert oq.get("type") == "array" and oq.get("items", {}).get("type") == "string", "open_questions should be an array of strings"


def test_schema_requirement_item():
    """Schema: each requirement has title, type, priority, evidence with enums"""
    req = _schema_props(REQUIREMENTS_SCHEMA)["requirements"]
    assert req.get("type") == "array", "requirements should be an array"
    item = req.get("items", {})
    assert item.get("type") == "object", "requirements items should be objects"
    assert set(_schema_props(item)) == {"title", "type", "priority", "evidence"}, f"item properties: got {sorted(_schema_props(item))}"
    assert sorted(item.get("required", [])) == ["evidence", "priority", "title", "type"], "all four item properties should be required"
    assert item.get("additionalProperties") is False, "set additionalProperties to False on the requirement object"
    assert _schema_props(item)["type"].get("enum") == REQUIREMENT_TYPES, "type should use enum REQUIREMENT_TYPES"
    assert _schema_props(item)["priority"].get("enum") == PRIORITY_ORDER, "priority should use enum PRIORITY_ORDER"


def _run(reply=None):
    _sim.reset()
    _sim.queue(reply if reply is not None else json.dumps({"requirements": [], "open_questions": ["q?"]}))
    out = extract_requirements(anthropic.Anthropic(), "Customer wants X.")
    return out, _sim.last_request()


def test_request_parameters():
    """Calls Claude with the model, max_tokens, system prompt and one user message"""
    _, req = _run()
    assert req["model"] == "claude-opus-5-5", f"model should be MODEL, got {req['model']!r}"
    assert req["max_tokens"] >= 4096, f"max_tokens should be at least 4096, got {req['max_tokens']}"
    assert req.get("system") == SYSTEM_PROMPT, "pass SYSTEM_PROMPT as system="
    assert len(req["messages"]) == 1 and req["messages"][0]["role"] == "user", "send exactly one user message"
    assert "Customer wants X." in str(req["messages"][0]["content"]), "the user message should contain the notes"


def test_request_uses_structured_outputs():
    """Passes the schema via output_config.format"""
    _, req = _run()
    fmt = (req.get("output_config") or {}).get("format")
    assert fmt is not None, "pass output_config={'format': {...}}"
    assert fmt.get("type") == "json_schema", "output_config.format.type should be 'json_schema'"
    assert fmt.get("schema") == REQUIREMENTS_SCHEMA, "output_config.format.schema should be REQUIREMENTS_SCHEMA"


def test_returns_parsed_dict():
    """Returns the parsed JSON as a dict"""
    out, _ = _run(json.dumps({"requirements": [{"title": "A", "type": "data", "priority": "must", "evidence": "e"}], "open_questions": []}))
    assert isinstance(out, dict), f"expected a dict, got {type(out).__name__}"
    assert out["requirements"][0]["title"] == "A", "parsed content doesn't match the response"


def test_finds_text_block_after_thinking():
    """Finds the text block even if a thinking block comes first"""
    payload = json.dumps({"requirements": [], "open_questions": ["first?"]})
    out, _ = _run(_sim.message(_sim.thinking(""), _sim.text(payload)))
    assert out == {"requirements": [], "open_questions": ["first?"]}, "read the block whose type is 'text', not content[0]"


def test_truncated_raises():
    """Raises ValueError('truncated') when stop_reason is max_tokens"""
    try:
        _run(_sim.message(_sim.text('{"requirements": [{"title": "A'), stop_reason="max_tokens"))
    except ValueError as e:
        assert str(e) == "truncated", f"expected ValueError('truncated'), got ValueError({str(e)!r})"
    else:
        raise AssertionError("expected ValueError('truncated') for a max_tokens response")


def test_refusal_raises():
    """Raises ValueError('refused') on a refusal"""
    try:
        _run(_sim.refusal())
    except ValueError as e:
        assert str(e) == "refused", f"expected ValueError('refused'), got ValueError({str(e)!r})"
    else:
        raise AssertionError("expected ValueError('refused') for a refusal")


def _req(title, priority):
    return {"title": title, "type": "functional", "priority": priority, "evidence": "e"}


def test_prioritized_order_is_stable():
    """prioritized() orders must, should, could and keeps order within a priority"""
    result = {"requirements": [_req("C1", "could"), _req("M1", "must"), _req("S1", "should"), _req("M2", "must")], "open_questions": []}
    got = prioritized(result)
    assert got == ["M1", "M2", "S1", "C1"], f"expected ['M1', 'M2', 'S1', 'C1'], got {got!r}"


def test_prioritized_dedupes():
    """prioritized() drops duplicate titles (ignoring case and spaces), keeping the first after sorting"""
    result = {"requirements": [_req("export csv ", "should"), _req("Export CSV", "must"), _req("SSO", "could")], "open_questions": []}
    got = prioritized(result)
    assert got == ["Export CSV", "SSO"], f"expected ['Export CSV', 'SSO'], got {got!r}"
