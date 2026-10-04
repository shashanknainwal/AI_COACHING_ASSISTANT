---
title: "Exercise: A Multi-Turn Support Assistant"
type: exercise
minutes: 30
hints:
  - "In `__init__`, store the client, system prompt, model and max_turns, and start with `self.history = []`."
  - "`send`: append `{\"role\": \"user\", \"content\": text}` first, then call `self.client.messages.create(...)` with `messages=self.history`."
  - "On a refusal, `self.history.pop()` removes the user turn you just added, then return `REFUSAL_REPLY`."
  - "On success, append `{\"role\": \"assistant\", \"content\": response.content}` (the whole list), call `self.trim()`, and return the joined text blocks."
  - "`trim`: `if len(self.history) > 2 * self.max_turns: self.history = self.history[-2 * self.max_turns:]`. Slicing an even number of messages from the end keeps complete pairs that start with a user turn."
  - "`turns` is a property: `len(self.history) // 2`."
---

Harbor Bank's support agents will chat with an assistant while they handle customer calls. Your job is the conversation engine: it keeps history correctly, uses low effort for snappy replies, handles refusals without corrupting the conversation, and keeps long chats from growing forever.

## Your task

Complete the `SupportChat` class.

**`__init__(self, client, system=SYSTEM_PROMPT, model=MODEL, max_turns=10)`**: store everything; start with an empty `self.history` list.

**`send(self, text)`** sends one user message and returns Claude's reply text:
1. Append the user turn to `self.history`.
2. Call `messages.create` with `model`, `max_tokens` of at least 4096, `system`, `messages=self.history`, and `output_config={"effort": "low"}`.
3. If `stop_reason` is `"refusal"`: remove the user turn you just added (so the history stays a clean alternation) and return `REFUSAL_REPLY`.
4. Otherwise append `{"role": "assistant", "content": response.content}`, the **full content list** including thinking blocks. Then call `self.trim()` and return the text (all text blocks joined).

**`trim(self)`** keeps at most `max_turns` complete exchanges (user + assistant pairs), dropping the oldest. The history must still start with a user turn.

**`reset(self)`** clears the history.

**`turns`** is a read-only property: the number of completed exchanges in the history.

Press **Run** to hold a short conversation, then **Submit**. The tests inspect exactly what your class sends to the API on every turn.
