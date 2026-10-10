---
title: "The Tool Loop in Depth"
type: reading
minutes: 20
---

> **By the end of this lesson** you will be able to:
> - Handle every `stop_reason` a tool loop can return, not just `tool_use` and `end_turn`
> - Batch parallel tool calls correctly and turn tool failures into results instead of crashes
> - Bound a loop and say exactly what happens at the cap
> - Explain why forced `tool_choice` returns a 400 on the newest models, and what to do instead
> - Argue for a workflow instead of an agent when that's the right call

## How this shows up in interviews

Anthropic's Applied AI Engineer postings list agents among the core skills, next to prompting and retrieval (Official, from the job postings). Candidate accounts of applied AI loops at Anthropic, OpenAI and Perplexity describe system design rounds built around LLM systems, and agents are a common prompt (Reported). In practice the topic comes up in three forms:

| Round | What it sounds like (original examples) | What they're checking |
|---|---|---|
| Fundamentals | "What exactly goes over the wire when the model calls two tools at once?" | You know the protocol, not just the idea |
| Coding / take-home | "Here's a stub agent. Make it production-safe." | Caps, error handling, stop reasons, tests |
| Design | "Design an agent that rebooks travelers after cancellations." | Whether you'd even use an agent, and how you bound it |

C2 covered the basic loop. This lesson is the version a staff engineer would accept in a code review.

## The protocol, message by message

A traveler writes: *"Booking FW7Q2K was cancelled. What are my options?"* Here is the full exchange for a run where Claude asks for two tools at once in its second turn.

| # | Role | Content blocks | Notes |
|---|---|---|---|
| 1 | user | text | The question |
| 2 | assistant | thinking, tool_use `get_booking` | `stop_reason: "tool_use"` |
| 3 | user | tool_result (for #2's id) | Your code ran the tool |
| 4 | assistant | thinking, tool_use `get_flight_status`, tool_use `find_alternatives` | Two independent lookups in **one** turn |
| 5 | user | tool_result, tool_result | **Both** results, **one** message, same order |
| 6 | assistant | text | `stop_reason: "end_turn"` |

Three rules make or break this:

1. **Append the assistant turn unchanged.** `response.content` goes back as-is, thinking blocks included. On Claude Opus 5.5, thinking is always on and the blocks are tied to the conversation they came from. Treat history as **append-only**: editing or dropping earlier messages can make the API reject or silently drop that reasoning, and it also breaks prompt caching.
2. **Every `tool_use` needs a matching `tool_result` in the very next user message.** The API returns a 400 if any id is missing. This is also why you can't "pause" in the middle of a turn and send something else (Lesson 4 builds on this).
3. **Read blocks by `type`, never by position.** A response can start with one or more `thinking` blocks.

## Every stop reason, and what your loop does

The basic loop checks `tool_use` and treats everything else as done. That's how you ship bugs.

| `stop_reason` | Meaning | What a production loop does |
|---|---|---|
| `end_turn` | Claude finished | Return the text blocks as the answer |
| `tool_use` | Claude wants tools run | Run them all, send all results in one message, loop |
| `max_tokens` | Hit your `max_tokens` cap | Return what you have, or retry with a bigger cap. **Never run a `tool_use` from this turn**: its input may be cut off |
| `refusal` | Claude declined (see `stop_details.category`) | Stop. **Don't run that turn's tools**: a refusal can cut a `tool_use` off mid-input. Return a safe message |
| `pause_turn` | A **server-side** tool (web search, code execution) paused a long turn | Re-send the conversation with the paused assistant turn appended, without adding a "continue" message. Cap the number of continuations |
| `stop_sequence` | Hit a custom stop sequence | Treat as done, unless you use stop sequences for control flow |
| `model_context_window_exceeded` | The conversation filled the context window | Compact or split the work; retrying unchanged won't help |

`max_tokens` on Opus 5.5 also covers thinking, so size it for thinking plus reply. A cap that looked fine on an older no-thinking route can truncate replies.

## Parallel tool calls

Claude can return several `tool_use` blocks in one turn. You can run them concurrently, but the results must go back **together, in one user message**. Keep them in the same order as the calls; it makes traces readable and matches the documented examples.

```python
results = []
for block in response.content:
    if block.type == "tool_use":
        results.append(execute_tool(block))      # never raises; see below
messages.append({"role": "user", "content": results})
```

Two details interviewers like:

- **Not all tools are parallel-safe.** Reads (`get_booking`, `search`) are. Writes that touch the same record (`cancel_booking` then `issue_refund`) may not be. A harness can run read-only tools concurrently and serialize writes. That's one reason to prefer dedicated tools over a generic "run this command" tool: your code can see what each call does.
- **You can limit it.** `tool_choice: {"type": "auto", "disable_parallel_tool_use": true}` means at most one call per turn. Use it when ordering matters more than speed.

## Errors are results, not exceptions

A tool that raises inside your loop kills the whole run, and the traveler gets a 500. Catch everything at the tool boundary and send back a `tool_result` with `"is_error": true`. Then decide what the message says:

| Failure | Example | Message to the model |
|---|---|---|
| The model can fix it | Unknown booking ref, bad date format | Specific: what was wrong and the expected format |
| Transient | Timeout to the flight-ops database | Generic: "failed unexpectedly, try again later or tell the traveler" |
| Unknown tool | Model invents `issue_voucher` | "Unknown tool: issue_voucher" (it happens; don't crash) |

Never paste `str(exc)` from an unexpected exception into the result. It's how internal hostnames, SQL and stack details end up in model context, then in a customer-facing reply or a log export.

## Bounding the loop

Every iteration resends the whole history, so cost grows faster than linearly with steps. Rough numbers for one run on Claude Opus 5.5 ($4 input / $20 output per million tokens) with `output_config={"effort": "low"}` set explicitly, 3,000 tokens of system prompt and tools, each iteration adding about 800 tokens, 300 visible output tokens per call, and an assumed 300 thinking tokens per call. Thinking is billed as output and counted in `usage.output_tokens`, so it belongs in the table:

| Design | Calls | Input tokens | Output tokens (reply + thinking) | Cost per run |
|---|---|---|---|---|
| Workflow: code does the lookups, one Claude call writes the reply | 1 | ~4,500 | 300 + 300 = 600 | ~$0.030 |
| Agent, 6 iterations | 6 | 3,000×6 + 800×(0+1+…+5) = 30,000 | 6 × 600 = 3,600 | ~$0.192 |

The 300 thinking tokens are an assumption, not a measured figure. At the default effort (`medium` on Opus 5.5) thinking is usually larger. As a sensitivity check, at 900 thinking tokens per call the agent run is 30,000 input plus 7,200 output, about $0.26. Measure `usage.output_tokens` on your own traffic before you quote a number.

That's about 6.4x, before retries. Prompt caching cuts the repeated prefix sharply, but the shape stays the same. So bound every loop:

- **Iteration cap.** 5 to 10 is typical for support tasks. At the cap, **stop without running the tools Claude just requested** (nobody will read their results, and they may have side effects) and hand off with a clear status like `"max_iterations"`.
- **Token or dollar budget**, summed from `response.usage` on every call.
- **Wall-clock limit**, because a person is waiting in chat.
- **Limits inside risky tools** (refund caps). The loop's caps stop runaway behavior; the tool's caps stop harmful behavior.

Return a **status** from the loop (`completed`, `max_iterations`, `refusal`, `max_tokens`), not just a string. The caller, the dashboard and the eval harness all need to tell them apart.

## Forced `tool_choice` on the newest models

On Claude Opus 5, and older models, you could force a call with `tool_choice: {"type": "any"}` (some tool) or `{"type": "tool", "name": "..."}` (this tool). On **Claude Opus 5.5, Claude Sonnet 5.5, Claude Fable 5.1 and Claude Mythos 5.1**, both return a 400:

```text
tool_choice: type "tool" and "any" are not supported for this model.
```

`auto` (the default) and `none` still work. Migrate by intent:

| You forced a tool because... | Do this instead |
|---|---|
| You need the model to call it | `auto` + say so in the prompt ("Use get_booking to answer") + **check** that a `tool_use` block came back, and retry or fall back if not |
| You need schema-valid arguments | `"strict": true` on the tool (schema with `additionalProperties: false`) |
| You only wanted JSON out | Structured outputs: `output_config.format` with a JSON schema. No fake tool needed |
| You needed exactly one call | `disable_parallel_tool_use: true` with `auto` now means *at most* one; check for zero |

This is a good interview signal: it shows you track model-level API changes and plan migrations instead of discovering them in production.

## Tool runner or hand-written loop?

The Python SDK has a **tool runner** (beta): decorate functions with `@beta_tool`, call `client.beta.messages.tool_runner(...)`, and it runs the loop. Anthropic's SDK guidance is to default to it. It still lets you inspect each turn, gate risky calls, intercept results and cap iterations. Write the loop yourself when you need control it doesn't expose (a custom transport, pausing for an approval that arrives hours later), or you don't want a beta dependency. In an interview, say both: "I'd start with the tool runner; here's the loop it runs, and here's when I'd own it."

## Workflows vs agents

An **agent** lets the model choose the next step in a loop. A **workflow** is code that decides the steps and calls the model for some of them.

| Signal | Lean workflow | Lean agent |
|---|---|---|
| Steps | Same 2 to 3 steps for 80% of cases | Path depends on what tools return |
| Branches | You can draw the flowchart | The flowchart would have dozens of branches |
| Risk | Writes money, sends email, changes records | Mostly reads; writes are gated |
| Latency budget | Under 2 to 3 seconds | Tens of seconds are fine |
| Testing | Needs exact, auditable behavior | Graded with evals over many runs |

**When not to build an agent:** the customer has one high-volume path ("where's my order?"), a strict latency budget, or actions they can't undo. A common answer that interviewers like is a **hybrid**: a workflow handles routing and the top paths, and an agent handles the long tail, with its write tools behind approval.

## Practice

Original prompts in the style of an applied AI loop. Answer out loud in two minutes each.

1. "Your agent returns `stop_reason: "max_tokens"` and the last block is a `tool_use`. Walk me through what your loop does and why."
2. "You're migrating a pipeline from Opus 5 to Opus 5.5 and it uses `tool_choice: {"type": "tool"}` to extract invoice fields. What breaks and what do you change?"
3. "A customer wants an agent for order-status questions, 40,000 a day, p95 under 2 seconds. Push back or build it?"

> **Key takeaways**
> - Append `response.content` unchanged and treat history as append-only; every `tool_use` gets a `tool_result` in the next user message.
> - Handle every stop reason. Never run tools from a `refusal` or `max_tokens` turn.
> - Parallel calls: one user message with all results, in order. Errors go back as `is_error` results with safe messages.
> - Bound loops by iterations, tokens and time; at the cap, stop without running the pending tools and return a status.
> - Forced `tool_choice` 400s on Opus 5.5 and Sonnet 5.5: use `auto` plus a prompt plus a check, `strict: true`, or structured outputs.
> - Default to a workflow; use an agent when the path truly depends on tool results.
