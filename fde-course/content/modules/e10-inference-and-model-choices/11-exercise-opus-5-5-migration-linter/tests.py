OK = {"model": "claude-opus-5-5", "max_tokens": 16000, "output_config": {"effort": "medium"},
      "messages": [{"role": "user", "content": "hi"}]}


def body(**kw):
    b = {k: v for k, v in OK.items()}
    b.update(kw)
    return b


def rules(findings):
    assert findings is not None, "lint() returned None"
    return [(f["rule"], f["severity"]) for f in findings]


def test_clean_body_has_no_findings():
    """A body with explicit effort, adaptive (or no) thinking and auto tool choice is clean"""
    assert lint(OK) == [], f"expected no findings, got {lint(OK)}"
    assert lint(body(thinking={"type": "adaptive"}, tool_choice={"type": "auto"})) == [], \
        "adaptive thinking and tool_choice auto are fine on Opus 5.5"
    assert lint(body(tool_choice={"type": "none"})) == [], "tool_choice none is unchanged"


def test_thinking_rules():
    """Disabled thinking and thinking budgets are errors"""
    assert rules(lint(body(thinking={"type": "disabled"}))) == [("THINKING_DISABLED", "error")]
    assert rules(lint(body(thinking={"type": "enabled", "budget_tokens": 8000}))) == [("THINKING_BUDGET", "error")]
    f = lint(body(thinking={"type": "disabled"}))[0]
    assert f["path"] == "thinking.type" and f["fix"], "every finding has a path and a fix"


def test_forced_tool_choice():
    """tool_choice any or tool is an error"""
    for tc in ({"type": "any"}, {"type": "tool", "name": "x"}):
        assert rules(lint(body(tool_choice=tc))) == [("FORCED_TOOL_CHOICE", "error")], f"{tc} returns a 400"


def test_prefill_and_pause_turn():
    """A final assistant turn is a prefill error, except re-sending a paused server-tool turn"""
    pre = body(messages=[{"role": "user", "content": "x"}, {"role": "assistant", "content": "{\"a\": "}])
    got = lint(pre)
    assert rules(got) == [("PREFILL", "error")] and got[0]["path"] == "messages.1", f"got {got}"
    paused = body(messages=[{"role": "user", "content": "search"},
                            {"role": "assistant", "content": [{"type": "server_tool_use", "id": "srvtoolu_1",
                                                               "name": "web_search", "input": {}}]}])
    assert lint(paused) == [], "re-sending a pause_turn response (server_tool_use) is how you resume; not a prefill"
    few_shot = body(messages=[{"role": "user", "content": "a"}, {"role": "assistant", "content": "b"},
                              {"role": "user", "content": "c"}])
    assert lint(few_shot) == [], "assistant turns earlier in the conversation are fine"


def test_sampling_params():
    """temperature, top_p and top_k are each an error, in that order"""
    got = lint(body(top_k=5, temperature=0.2))
    assert rules(got) == [("SAMPLING_PARAM", "error"), ("SAMPLING_PARAM", "error")]
    assert [f["path"] for f in got] == ["temperature", "top_k"], "report sampling params in the order temperature, top_p, top_k"


def test_computer_tool_by_platform():
    """The old computer tool is an error on the Claude API and Vertex, a warning on Bedrock"""
    b = body(tools=[{"name": "notes", "input_schema": {"type": "object"}},
                    {"type": "computer_20251124", "name": "computer", "display_width_px": 1024, "display_height_px": 768}])
    got = lint(b)
    assert rules(got) == [("COMPUTER_TOOL", "error")] and got[0]["path"] == "tools.1.type", f"got {got}"
    assert rules(lint(b, "vertex")) == [("COMPUTER_TOOL", "error")]
    assert rules(lint(b, "bedrock")) == [("COMPUTER_TOOL", "warning")], "Bedrock still accepts computer_20251124"
    assert lint(body(tools=[{"type": "computer_toolset_20260801"}])) == [], "the toolset is the new form"


def test_warnings():
    """Deprecated output_format, unset effort and a small max_tokens are warnings, not errors"""
    b = {"model": "claude-opus-5-5", "max_tokens": 1024, "output_format": {"type": "json_schema", "schema": {}},
         "messages": [{"role": "user", "content": "x"}]}
    assert rules(lint(b)) == [("OUTPUT_FORMAT", "warning"), ("EFFORT_UNSET", "warning"), ("MAX_TOKENS_LOW", "warning")]
    assert will_400(b) is False, "warnings alone don't make a request fail"
    assert lint(body(max_tokens=4000)) == [], "exactly 4,000 is enough under the team rule"


def test_order_and_will_400():
    """Findings come in rule order and will_400 reflects errors"""
    b = {"model": "claude-opus-5-5", "max_tokens": 500, "temperature": 0, "tool_choice": {"type": "any"},
         "thinking": {"type": "disabled"}, "messages": [{"role": "user", "content": "x"}]}
    assert [f["rule"] for f in lint(b)] == ["THINKING_DISABLED", "FORCED_TOOL_CHOICE", "SAMPLING_PARAM",
                                            "EFFORT_UNSET", "MAX_TOKENS_LOW"]
    assert will_400(b) is True and will_400(OK) is False


def test_check_history():
    """Editing earlier turns, the system prompt or the tools is an error once thinking blocks are in history"""
    prev = {"system": "You tag articles.", "tools": [{"name": "t"}],
            "messages": [{"role": "user", "content": "q1"},
                         {"role": "assistant", "content": [{"type": "thinking", "thinking": "", "signature": "s1"},
                                                           {"type": "text", "text": "a1"}]}]}
    appended = {**prev, "messages": prev["messages"] + [{"role": "user", "content": "q2"}]}
    assert check_history(prev, appended) is None, "appending is always fine"
    trimmed = {**prev, "messages": [{"role": "user", "content": "q1 (edited)"}] + prev["messages"][1:]
               + [{"role": "user", "content": "q2"}]}
    f = check_history(prev, trimmed)
    assert f is not None and f["rule"] == "HISTORY_EDITED" and f["severity"] == "error" and f["path"] == "messages.0", f"got {f}"
    sys_changed = {**appended, "system": "You tag articles. Today is Monday."}
    assert check_history(prev, sys_changed)["path"] == "system", "a changed system prompt breaks the prefix"
    tools_changed = {**appended, "tools": [{"name": "t"}, {"name": "u"}]}
    assert check_history(prev, tools_changed)["path"] == "tools"
    no_thinking = {**prev, "messages": [{"role": "user", "content": "q1"}, {"role": "assistant", "content": "a1"}]}
    assert check_history(no_thinking, {**no_thinking, "messages": [{"role": "user", "content": "q2"}]}) is None, \
        "without thinking blocks in history there is nothing to invalidate"


def test_report():
    """report() counts findings by rule and how many bodies would 400"""
    got = report([OK, body(temperature=1), body(tool_choice={"type": "any"}, top_p=0.9), {**OK, "max_tokens": 10}])
    assert got == {"blocked": 2, "SAMPLING_PARAM": 2, "FORCED_TOOL_CHOICE": 1, "MAX_TOKENS_LOW": 1}, f"got {got}"
