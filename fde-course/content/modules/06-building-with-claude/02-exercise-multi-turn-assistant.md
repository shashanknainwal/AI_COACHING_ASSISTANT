---
title: "Exercise: A Multi-Turn Support Assistant"
type: exercise
minutes: 35
hints:
  - "In `__init__`, store the client, system prompt, model and max_turns, and start with `self.history = []` and `self.summary = None`."
  - "`send`: first `if self.turns >= self.max_turns: self.compact()`. Then append the user turn and call `self.client.messages.create(...)` with `messages=self.history`."
  - "The user turn is a plain string, except right after a compaction (history empty, summary set): then it is a list of two text blocks, `SUMMARY_PREFIX + self.summary` first and the new message second."
  - "On a refusal, `self.history.pop()` removes only the user turn you just added. On success, append `{\"role\": \"assistant\", \"content\": response.content}` (the whole list) and return the joined text blocks."
  - "`compact`: call the API with `self.history + [{\"role\": \"user\", \"content\": COMPACT_PROMPT}]` (a new list, so `self.history` is untouched), store the joined text in `self.summary`, then set `self.history = []`."
---

Harbor Bank's support agents will chat with an assistant while they handle customer calls. Your job is the conversation engine: it keeps history correctly, uses low effort for snappy replies, handles refusals without corrupting the conversation, and keeps long chats from growing forever without ever editing an earlier turn.

That last part matters on Claude Opus 5.5. Its thinking blocks are bound to everything before them (system prompt, tools and every earlier message). If you drop the oldest turns and replay newer ones with their thinking, the binding check fails: by default that is a 400 on accounts created since 31 August 2026, and older accounts silently lose the reasoning. The prompt cache misses on every trim too. So instead of trimming, you **compact**: ask Claude for a summary, then start a fresh, append-only history whose first turn carries that summary. No earlier thinking block is ever replayed after its history changed.

## Your task

Complete the `SupportChat` class.

**`__init__(self, client, system=SYSTEM_PROMPT, model=MODEL, max_turns=10)`**: store everything; start with `self.history = []` and `self.summary = None`.

**`send(self, text)`** sends one user message and returns Claude's reply text:
1. If the history already holds `max_turns` complete exchanges, call `self.compact()` first.
2. Build the user turn. Normally its content is `text`. If the history is empty and `self.summary` is set (you just compacted), its content is a list of two text blocks: `SUMMARY_PREFIX + self.summary`, then `text`.
3. Append the user turn and call `messages.create` with `model`, `max_tokens` of at least 4096, `system`, `messages=self.history` and `output_config={"effort": "low"}`.
4. If `stop_reason` is `"refusal"`: remove the user turn you just added (the newest turn only) and return `REFUSAL_REPLY`.
5. Otherwise append `{"role": "assistant", "content": response.content}`, the **full content list** including thinking blocks, and return the text (all text blocks joined).

**`compact(self)`** sends one request with the same model, system and effort, whose messages are the current history unchanged plus one final user turn, `COMPACT_PROMPT`. Build that as a new list; don't append to `self.history`. Store the reply text in `self.summary`, then set `self.history = []`.

**`reset(self)`** clears the history and the summary.

**`turns`** is a read-only property: the number of completed exchanges in the history.

## Example

With `max_turns=2`: two questions go out as a growing history. On the third question, `compact()` sends the four-message history plus `COMPACT_PROMPT`, and the third question goes out as a single user turn whose first block is the summary.

## Why not the other options?

- **Rolling truncation** (keep the last N turns) edits the start of the history, so every kept thinking block fails the binding check.
- **Stripping thinking blocks from the kept turns** is a documented alternative, but you lose that reasoning and still miss the cache.
- **Server-side compaction and context editing** (both beta on the Claude API) run on Anthropic's side and are designed to keep retained blocks valid. In production, prefer them where your platform supports them; check the current docs for the beta header. This exercise builds the client-side version so you see exactly what goes over the wire.

Press **Run** to hold a short conversation, then **Submit**. The tests inspect exactly what your class sends to the API on every turn. The simulator doesn't enforce the binding check itself, so the tests check that the history is append-only.
