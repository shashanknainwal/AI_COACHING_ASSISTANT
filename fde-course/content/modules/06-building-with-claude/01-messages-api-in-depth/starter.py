import anthropic

client = anthropic.Anthropic()
SYSTEM = "You are Harbor Bank's support assistant. Be accurate and brief."

history = [{"role": "user", "content": "What's the fee for an international wire?"}]
first = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=16000,
    system=SYSTEM,
    messages=history,
    output_config={"effort": "low"},
)

print("Blocks:     ", [b.type for b in first.content])
print("Stop reason:", first.stop_reason)
print("Usage:      ", first.usage)
print("Request ID: ", first._request_id)
print("Answer:     ", "".join(b.text for b in first.content if b.type == "text"))

# Continue the conversation: append the FULL content list, then the next user turn.
history.append({"role": "assistant", "content": first.content})
history.append({"role": "user", "content": "And for a domestic one?"})
second = client.messages.create(model="claude-opus-5-5", max_tokens=16000, system=SYSTEM, messages=history)
print("\nTurn 2 sent", len(history), "messages. Input tokens:", second.usage.input_tokens)

# Try it: change effort to "huge" and see the API's error message.
