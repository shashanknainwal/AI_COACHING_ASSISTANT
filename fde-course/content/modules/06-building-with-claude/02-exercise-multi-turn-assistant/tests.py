import anthropic
from anthropic import _sim


def _fresh():
    _sim.calls.clear()
    _sim._queue.clear()


def _types(content):
    return [b["type"] for b in content] if isinstance(content, list) else ["str"]


def test_first_request():
    """send() calls the API with the system prompt, low effort and the user turn"""
    _fresh()
    chat = SupportChat(anthropic.Anthropic())
    reply = chat.send("What does an international wire cost?")
    assert reply == "International wires cost $35 to send and $15 to receive. Domestic wires are $25.", f"got {reply!r}"
    req = _sim.last_request()
    assert req["model"] == "claude-opus-5-5" and req["max_tokens"] >= 4096
    assert req.get("system") == SYSTEM_PROMPT, "pass the system prompt"
    assert req.get("output_config") == {"effort": "low"}, f"use output_config={{'effort': 'low'}}, got {req.get('output_config')}"
    assert req["messages"] == [{"role": "user", "content": "What does an international wire cost?"}]


def test_history_includes_full_assistant_content():
    """The second request resends history with the assistant's full content list"""
    _fresh()
    chat = SupportChat(anthropic.Anthropic())
    chat.send("What does an international wire cost?")
    chat.send("And a domestic one?")
    msgs = _sim.last_request()["messages"]
    assert [m["role"] for m in msgs] == ["user", "assistant", "user"], f"roles sent: {[m['role'] for m in msgs]}"
    content = msgs[1]["content"]
    assert isinstance(content, list), "append response.content (the list of blocks), not just the text"
    assert _types(content) == ["thinking", "text"], f"keep the thinking block too; got {_types(content)}"
    assert chat.turns == 2 and len(chat.history) == 4


def test_history_is_append_only():
    """Each request starts with exactly the messages the previous request sent"""
    _fresh()
    chat = SupportChat(anthropic.Anthropic())
    for q in ["wire?", "domestic?", "dispute?", "anything else?"]:
        chat.send(q)
    reqs = _sim.requests()
    assert len(reqs) == 4, f"expected 4 requests with max_turns=10 (no compaction yet), got {len(reqs)}"
    for prev, nxt in zip(reqs, reqs[1:]):
        n = len(prev["messages"])
        assert nxt["messages"][:n] == prev["messages"], \
            "an earlier turn changed between requests; on Opus 5.5 that breaks preserved thinking and the cache"


def test_refusal_keeps_history_clean():
    """A refusal returns REFUSAL_REPLY and leaves the history unchanged"""
    _fresh()
    chat = SupportChat(anthropic.Anthropic())
    chat.send("What does an international wire cost?")
    before = list(chat.history)
    got = chat.send("Can you reset my neighbor's password?")
    assert got == REFUSAL_REPLY, f"expected REFUSAL_REPLY, got {got!r}"
    assert chat.history == before, "remove the refused user turn so history still alternates user/assistant"
    chat.send("How do I dispute a card charge?")
    roles = [m["role"] for m in _sim.last_request()["messages"]]
    assert roles == ["user", "assistant", "user"], f"after a refusal the next request should be clean; got {roles}"


def test_compaction_asks_for_a_summary():
    """At max_turns, compact() sends the full history plus COMPACT_PROMPT, then starts a fresh history"""
    _fresh()
    chat = SupportChat(anthropic.Anthropic(), max_turns=2)
    chat.send("wire?")
    chat.send("domestic?")
    chat.send("dispute?")
    reqs = _sim.requests()
    assert len(reqs) == 4, f"expected 2 sends, 1 compaction request, 1 send; got {len(reqs)} requests (trimming is not compaction)"
    summary_req = reqs[2]["messages"]
    assert len(summary_req) == 5, f"the compaction request should carry the whole history plus COMPACT_PROMPT (5 messages), got {len(summary_req)}"
    assert summary_req[:3] == reqs[1]["messages"], "send the history unchanged"
    assert _types(summary_req[3]["content"]) == ["thinking", "text"], "keep the last assistant turn's thinking block in the compaction request"
    assert summary_req[-1] == {"role": "user", "content": COMPACT_PROMPT}, "end the compaction request with COMPACT_PROMPT"
    assert chat.summary and "wire" in chat.summary, f"store the summary text in self.summary; got {chat.summary!r}"


def test_after_compaction_no_old_thinking():
    """After compaction the next request is one user turn: summary block, then the new question"""
    _fresh()
    chat = SupportChat(anthropic.Anthropic(), max_turns=2)
    for q in ["wire?", "domestic?", "dispute?"]:
        chat.send(q)
    msgs = _sim.last_request()["messages"]
    assert len(msgs) == 1 and msgs[0]["role"] == "user", f"start a fresh history after compaction; sent {len(msgs)} messages"
    content = msgs[0]["content"]
    assert _types(content) == ["text", "text"], f"the first user turn should hold two text blocks; got {_types(content)}"
    assert content[0]["text"] == SUMMARY_PREFIX + chat.summary, "first block: SUMMARY_PREFIX + the summary"
    assert content[1]["text"] == "dispute?", "second block: the learner's new message"
    assert chat.turns == 1 and len(chat.history) == 2


def test_reset_and_custom_system():
    """reset() clears history and summary; a custom system prompt is used"""
    _fresh()
    chat = SupportChat(anthropic.Anthropic(), system="Custom rules.", max_turns=1)
    chat.send("wire?")
    chat.send("dispute?")
    chat.reset()
    assert chat.history == [] and chat.turns == 0 and chat.summary is None
    chat.send("dispute?")
    req = _sim.last_request()
    assert req["system"] == "Custom rules." and req["messages"] == [{"role": "user", "content": "dispute?"}]
