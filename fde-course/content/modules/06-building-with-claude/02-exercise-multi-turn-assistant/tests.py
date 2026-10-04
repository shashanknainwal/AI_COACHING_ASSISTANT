import anthropic
from anthropic import _sim


def _fresh():
    _sim.calls.clear()
    _sim._queue.clear()


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
    assert [b["type"] for b in content] == ["thinking", "text"], f"keep the thinking block too; got {[b['type'] for b in content]}"
    assert chat.turns == 2 and len(chat.history) == 4


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


def test_trim_keeps_recent_pairs():
    """With max_turns=2, only the last 2 exchanges are kept and history starts with user"""
    _fresh()
    chat = SupportChat(anthropic.Anthropic(), max_turns=2)
    for q in ["wire?", "domestic?", "dispute?"]:
        chat.send(q)
    assert len(chat.history) == 4 and chat.turns == 2, f"expected 4 messages, got {len(chat.history)}"
    assert chat.history[0] == {"role": "user", "content": "domestic?"}, f"oldest pair should be dropped; first is {chat.history[0]}"
    chat.send("anything else?")
    assert _sim.last_request()["messages"][0] == {"role": "user", "content": "domestic?"}, \
        "the request is sent before trimming, so it still includes the 2 previous exchanges"


def test_reset_and_custom_system():
    """reset() clears history; a custom system prompt is used"""
    _fresh()
    chat = SupportChat(anthropic.Anthropic(), system="Custom rules.")
    chat.send("wire?")
    chat.reset()
    assert chat.history == [] and chat.turns == 0
    chat.send("dispute?")
    req = _sim.last_request()
    assert req["system"] == "Custom rules." and len(req["messages"]) == 1
