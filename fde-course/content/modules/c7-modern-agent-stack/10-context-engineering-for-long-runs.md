---
title: "Context Engineering for Long-Running Agents"
type: reading
minutes: 18
---

> **By the end of this lesson you will be able to:**
> - Choose between context editing, compaction and the memory tool for a long-running agent.
> - Use tool search and programmatic tool calling to keep tool schemas and intermediate data out of context.
> - Change instructions mid-session without breaking the prompt cache.
> - Keep a history append-only so Opus 5.5's preserved thinking stays valid.

A short agent fits in its context window without thought. A long one, forty turns of status dumps during a depot strike, does not. Context engineering is deciding what the model reads on each turn. Get it wrong and you pay for stale tokens, lose the cache, and on the newest models start getting 400 errors.

## Three tools for growing context

| Pattern | What it does | Use when |
|---|---|---|
| **Context editing** (beta) | Clears stale tool results or thinking blocks before the model sees them. Prunes; doesn't summarise | Old tool outputs are no longer relevant but the conversation structure matters |
| **Compaction** (beta) | Summarises earlier context server-side into a compaction block when you near a threshold | The conversation will reach or exceed the context window |
| **Memory tool** | Claude reads and writes files in a `/memories` directory you host | State must survive across sessions, not just within one |

Context editing uses the `context-management-2025-06-27` beta with strategies such as `clear_tool_uses_20250919` (old tool results) and `clear_thinking_20251015` (thinking blocks); when it triggers and how much it keeps are configurable, so check the context-editing docs. Compaction uses the `compact-2026-01-12` beta, and has one critical rule: append the full `response.content` back to your messages every turn, not just the text, or you silently lose the compaction state.

The memory tool (`memory_20250818`) is client-side: you implement storage, so you own the security. Never store secrets in memory files, be careful with personal data, and give each user their own memory directory in a multi-user system. Many long-running agents use all three: editing and compaction within a session, memory across sessions.

## Keep tool schemas and intermediate data out

- **Tool search.** With dozens of tools but only a few relevant per request, mark most of them `defer_loading: true` and add a tool search tool. Claude searches and loads only the schemas it needs, and discovered schemas are *appended*, so the cached prefix survives. Never defer every tool: at least one must stay loaded.
- **Programmatic tool calling.** Claude writes a script that calls your tools from inside code execution. Intermediate results go back to the running script, not into Claude's context, and only the script's final output returns. Use it for long chains of calls or large intermediate data. It isn't available on Bedrock or Vertex.

## Change instructions without breaking the cache

Editing the top-level `system` prompt mid-session changes the start of the prompt prefix and invalidates the whole cache. Instead, append a `{"role": "system", "content": "..."}` message to `messages`. On Opus 5.5, Sonnet 5.5 and Haiku 5.5 this needs no beta header. It carries operator authority, keeps the cached prefix intact, and is a safer channel than putting operator text in a user turn. It must follow a user message and be either the last message or followed by an assistant turn.

To add or remove a tool mid-session, declare the full set up front and send `tool_addition` or `tool_removal` blocks in a system message (beta `mid-conversation-tool-changes-2026-07-01`), rather than editing the `tools` array.

## Preserved thinking: why append-only is mandatory

On Opus 5.5, a thinking block's signature is bound to everything sent before it: the `system` prompt, the `tools` and every earlier message. If you edit any of that and send a later thinking block back, the check fails. For accounts created on or after 31 August 2026 it is enforced by default and returns a 400; older accounts can opt in. Build for enforcement regardless of account age.

| You were doing | Do this instead |
|---|---|
| Editing the system prompt mid-session | Append a `role: "system"` message |
| Editing the `tools` array mid-session | Declare all tools up front; send `tool_addition` / `tool_removal` |
| Deleting old tool results client-side | Server-side context editing |
| Injecting a per-turn reminder, then deleting it | Append it after the tool results and leave earlier copies in place |
| Compacting client-side while replaying recent thinking blocks | Server-side compaction or context editing; client-side, replace the whole history with one summary and replay no earlier thinking |

Server-side clearing and compaction don't count as edits, because the check compares the conversation as you sent it, not the server's edited copy. Two client-side shapes break: keep-tail compaction (summarise old turns, keep recent turns verbatim with their thinking) and swapping a summary in while newer turns already exist. Snipping turns out of the middle invalidates every later block, and no client-side trick avoids it.

The same habits keep the prompt cache warm, so the fix pays twice. To check an existing harness, capture consecutive request bodies and confirm that `system`, `tools` and the shared prefix of `messages` are byte-identical up to the newly appended turns. In CI, send `thinking.block_binding.prefix_mismatch_behavior: "error"` under the `thinking-binding-controls-2026-08-01` beta so any edit fails the run.

> **Key takeaways**
> - Context editing prunes, compaction summarises, memory persists across sessions; long agents often use all three.
> - With compaction, append the full `response.content` every turn.
> - Tool search and programmatic tool calling keep schemas and intermediate data out of context.
> - Append a `role: "system"` message for mid-session instructions instead of editing `system`.
> - On Opus 5.5, keep history append-only; use server-side editing or compaction to trim.
