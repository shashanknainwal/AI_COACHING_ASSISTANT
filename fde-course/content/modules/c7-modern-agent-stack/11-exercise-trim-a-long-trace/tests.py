import copy
import json


def _req():
    return next_request(copy.deepcopy(PREV_REQUEST), copy.deepcopy(LAST_RESPONSE_CONTENT), NEW_USER_TEXT, NEW_RULE)


def _same(a, b):
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_auditor_catches_history_edits():
    """audit_append_only flags every kind of history edit"""
    good = naive_next_request()
    assert audit_append_only(PREV_REQUEST, good) == [], "An append-only request should give no problems."
    variants = {}
    v = copy.deepcopy(good); v["system"] = SYSTEM + " Escalate big shipments."; variants["edited system prompt"] = v
    v = copy.deepcopy(good); v["tools"] = TOOLS[:-1]; variants["tool removed from tools"] = v
    v = copy.deepcopy(good); v["messages"][4]["content"][0]["content"] = "[trimmed]"; variants["old tool result trimmed"] = v
    v = copy.deepcopy(good); v["messages"][7]["content"] = [b for b in v["messages"][7]["content"] if b["type"] != "thinking"]
    variants["thinking block removed mid-history"] = v
    v = copy.deepcopy(good); v["messages"] = v["messages"][:1] + v["messages"][21:]; variants["middle turns snipped"] = v
    v = copy.deepcopy(good); v["messages"][0]["content"] += " (reminder: be brief)"; variants["reminder injected into turn 1"] = v
    for label, req in variants.items():
        assert audit_append_only(PREV_REQUEST, req), f"Your auditor missed: {label}."


def test_request_is_append_only():
    """The next request keeps system, tools and every earlier message byte-identical"""
    req = _req()
    assert _same(req.get("system"), PREV_REQUEST["system"]), "Don't touch the top-level system prompt mid-session."
    assert _same(req.get("tools"), PREV_REQUEST["tools"]), "Don't change the tools array mid-session."
    n = len(PREV_REQUEST["messages"])
    assert _same(req["messages"][:n], PREV_REQUEST["messages"]), \
        "Every earlier message, including each thinking block and its signature, must be sent back unchanged."
    assert req.get("model") == MODEL, "Stay on the same model: switching models drops the thinking blocks and the cache."


def test_new_turns_appended_in_order():
    """The response, the user's turn and the new rule are appended in a valid order"""
    req = _req()
    tail = req["messages"][len(PREV_REQUEST["messages"]):]
    assert len(tail) == 3, f"Append exactly three messages: the assistant response, the user turn, the system rule. Got {len(tail)}."
    assert tail[0]["role"] == "assistant" and _same(tail[0]["content"], LAST_RESPONSE_CONTENT), \
        "Append the full response content (thinking block included), not just its text."
    assert tail[1]["role"] == "user" and NEW_USER_TEXT in json.dumps(tail[1]["content"]), "Then the user's new turn."
    assert tail[2]["role"] == "system" and NEW_RULE in json.dumps(tail[2]["content"]), \
        "Then the rule as a role 'system' message. It must follow a user message and be last (or be followed by an assistant turn)."


def test_server_side_clearing_requested():
    """Context editing is requested with the documented beta and strategy"""
    req = _req()
    assert "context-management-2025-06-27" in (req.get("betas") or []), "Context editing needs the context-management-2025-06-27 beta."
    types = [e.get("type") for e in (req.get("context_management") or {}).get("edits", [])]
    assert "clear_tool_uses_20250919" in types, "Ask the API to clear old tool results: context_management.edits with clear_tool_uses_20250919."


def test_token_reduction():
    """The model reads at least 60% fewer tokens than the naive request"""
    before, after = seen_tokens(naive_next_request()), seen_tokens(_req())
    assert after <= 0.4 * before, f"Cut at least 60%: naive {before:,} tokens, yours {after:,} ({1 - after / before:.0%} less)."


def test_edit_choices():
    """Each proposed edit is correctly marked use or avoid"""
    assert set(EDIT_CHOICES) == set(CANDIDATE_EDITS), "Give a decision for every key in CANDIDATE_EDITS."
    expected_use = {"server_side_tool_result_clearing", "append_role_system_message", "server_side_compaction"}
    wrong = sorted(k for k, v in EDIT_CHOICES.items() if v != ("use" if k in expected_use else "avoid"))
    assert not wrong, f"{len(wrong)} decision(s) wrong. Re-read the reading's append-only table. First: {wrong[0]}"
