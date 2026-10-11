---
title: "Exercise: Cut a 40-Turn Trace Without Touching History"
type: exercise
minutes: 45
hints:
  - "The auditor compares three things: `system`, `tools`, and the shared prefix of `messages`. Serialise with `json.dumps(..., sort_keys=True)` and compare strings. A shorter `messages` list is a problem in itself."
  - "Build request 41 from a deep copy of request 40. Append, in order: the assistant turn with the full `LAST_RESPONSE_CONTENT` (thinking block included), the user's new text, then a `{\"role\": \"system\", \"content\": NEW_RULE}` message."
  - "The token cut comes from the server, not from you. Add `betas=[\"context-management-2025-06-27\"]` and `context_management={\"edits\": [{\"type\": \"clear_tool_uses_20250919\"}]}`. Call `seen_tokens` on your request to check."
  - "For `EDIT_CHOICES`: anything that changes bytes you already sent (system prompt, tools array, old tool results, thinking blocks in the middle, keep-tail summaries that replay thinking) is 'avoid'. Server-side clearing, server-side compaction and appended system messages are 'use'."
---

Rhea forwards an incident. "Our disruption agent on Opus 5.5 ran 40 turns during the Rotterdam strike. By the end, each request carried about 46,000 input tokens, most of them stale status dumps. Someone 'fixed' it by trimming old tool results in our harness and got a wall of 400 errors. Then ops asked for a new rule mid-session, and another engineer edited the system prompt. Same result. I need the next request built properly, and a checker we can put in CI so this never ships again."

On Opus 5.5, each thinking block's signature is bound to everything sent before it: the system prompt, the tools and every earlier message. On enforced accounts, editing any of that and replaying a later thinking block returns a 400. The fix is an append-only history plus server-side context management. `PREV_REQUEST` (the body of request 40), `LAST_RESPONSE_CONTENT`, `NEW_USER_TEXT`, `NEW_RULE`, `CANDIDATE_EDITS`, `seen_tokens(request)` (a simulated count of what the model reads after the server applies context editing) and `naive_next_request()` are given.

## Your task

**1. `audit_append_only(prev, new)`** returns a list of problems, empty if `new` is a pure extension of `prev`:

- `"system changed"` if the top-level `system` differs;
- `"tools changed"` if `tools` differs;
- `"messages removed"` if `new` has fewer messages;
- `"message <i> changed"` for the first earlier message that isn't byte-identical.

**2. `next_request(prev, last_response_content, user_text, new_rule)`** returns request 41:

- same `model`, `system`, `tools` and every earlier message, unchanged;
- appended: the assistant turn (full content), the user turn, then the new rule as a `role: "system"` message;
- `betas` with `context-management-2025-06-27` and `context_management.edits` with `clear_tool_uses_20250919`.

It must pass your own auditor and cut what the model reads (per `seen_tokens`) by at least 60% compared with `naive_next_request()`.

**3. `EDIT_CHOICES`** maps every key in `CANDIDATE_EDITS` to `"use"` or `"avoid"`.

## Example

```text
Append-only problems: none
Tokens the model reads: 45,920 -> 6,990 (85% less)
Editing the system prompt instead: ['system changed']
```

## Why it's built this way

- **The server's edited copy isn't checked; what you send is.** Server-side clearing and compaction don't count as history edits, because the check compares the conversation as you sent it. Client-side trimming of the same results does count.
- **Mid-session instructions are appended.** A `role: "system"` message carries operator authority, keeps the cached prefix intact and becomes part of the prefix later blocks bind to. On Opus 5.5 it needs no beta header.
- **Tools change by message, too.** To take `issue_credit` away mid-session, the append-only form is a `tool_removal` block in a system message (beta `mid-conversation-tool-changes-2026-07-01`), not editing the `tools` array.
- **The same habits keep the prompt cache warm.** Every edit that breaks preserved thinking also breaks the cache prefix, so the fix pays twice.
- **Put the auditor in CI.** Capture consecutive request bodies from a test session and run the check on each pair. The real-API version of this check is to send `thinking.block_binding.prefix_mismatch_behavior: "error"` under the `thinking-binding-controls-2026-08-01` beta in CI, so any edit fails the run.

In a debrief, expect: "Half our requests started returning 400 after we moved to Opus 5.5, and nothing in our prompts changed. What do you check?"
