---
title: "Designing Tools Models Use Well"
type: reading
minutes: 20
---

> **By the end of this lesson** you will be able to:
> - Decide how big each tool should be, and when to split one
> - Write names, descriptions and schemas that steer the model, and know what `strict: true` does and doesn't guarantee
> - Return compact, fixable results and make write tools idempotent
> - Put risky actions behind permission tiers and approval gates that fail closed
> - Explain what MCP is and when a customer actually needs an MCP server

## How this shows up in interviews

In a design round, "what tools would your agent have?" is where many candidates go vague. Interviewers in applied AI loops are reported to probe failure handling and safety, not just the happy path (Reported, from candidate accounts of design rounds). A strong answer names each tool, its inputs, what it returns, what can go wrong, and who can approve it. A tool list is also the fastest way to show you've shipped an agent, because every decision in it comes from a failure you'd only see in production.

## Tool size: dedicated tools beat a god tool

The broadest possible tool is "run any command" or "run any SQL". It gives the model leverage and gives your harness nothing: every call has the same shape, so your code can't tell a harmless read from a destructive write. Anthropic's agent-design guidance makes the same point about a bash tool versus dedicated tools: promote an action to its own tool when you need to **gate** it, **audit** it, **render** it for a person, or **run it in parallel** safely.

| Design | Harness can... | Example |
|---|---|---|
| `run_sql(query)` | Almost nothing beyond logging a string | Model can `DELETE` as easily as `SELECT` |
| `get_booking(ref)`, `issue_refund(ref, amount, reason)` | Gate refunds over $200, run reads in parallel, show "Refund $612.00 to Ana Souza" to a reviewer | Each action has typed arguments you can check |

Split a tool when its arguments change meaning by mode (`manage_booking(action="cancel" | "lookup")` is two tools pretending to be one) or when parts of it carry different risk. Merge tools when the model always calls them together; that's a workflow step, not a choice.

Keep the set focused. Too many overlapping tools is a top cause of "wrong tool" failures (Lesson 5). For very large catalogs, the API's tool search feature lets Claude discover tools on demand instead of loading every schema up front.

## Names, descriptions and schemas

The model reads your tool definition as part of the prompt. Write it like one.

- **Names** say the action and object: `find_alternatives`, not `search2`.
- **Descriptions say when to call it**, not just what it does: "Call this when a flight is cancelled or the traveler wants to rebook." Anthropic's migration notes describe Claude Opus 4.8 as more conservative about reaching for custom tools and sub-agents unless told when they apply. That observation is documented for 4.8, not for Opus 5.5, but the fix is cheap on any model: trigger conditions in descriptions tell the model when a call is warranted.
- **Describe every property**, with a format example: `"Booking reference such as FW7Q2K"`.
- **Use `enum` for closed sets** (`reason`: `schedule_change`, `airline_cancellation`, ...). The model can't invent a value that isn't listed, and your reports get clean categories.
- **Mark only truly required fields as required.**

### What `strict: true` buys you

Add `"strict": true` to a tool and the model's `input` is guaranteed to match the schema. The schema must set `"additionalProperties": false`. Since forced `tool_choice` is gone on Opus 5.5 and Sonnet 5.5 (Lesson 1), strict mode is how you keep the "arguments always parse" guarantee.

What it does **not** buy you:

| Guarantee | Strict mode? | Where it lives instead |
|---|---|---|
| `amount` is a number | Yes | |
| `amount` is at most the fare paid | No | Tool code. The structured-outputs docs list numeric bounds like `minimum` and `maximum` as unsupported, so check ranges in code |
| `booking_ref` exists | No | Tool code returns a fixable error |
| `booking_ref` belongs to *this* traveler | No | Tool code checks authorization against the signed-in user, not the model's claim |
| The model should be refunding at all | No | Policy in code plus approval gates |

Shape is the model's job. Meaning is yours.

## Results: compact, structured and fixable

Every result you return is resent on every later iteration. A 6,000-token booking record returned at step 1 of an 8-step run costs you 48,000 input tokens.

- **Return the fields the model needs**, not the row. Five fields, not fifty.
- **Cap lists and say so**: `{"options": [...3 items...], "total": 41, "note": "Showing 3 of 41. Narrow by date."}`.
- **Use stable IDs** the model can pass to the next tool (`booking_ref`, `refund_id`), so it never has to guess one.
- **Make errors teach.** "No booking found with reference FW7Q2. References are 6 characters, like FW7Q2K." gets a corrected retry. "Error 404" gets a guess or an apology.
- **Size results when they're created.** Trimming old results later means editing history, which costs cache hits and, on Opus 5.5, can invalidate thinking blocks. For long runs, the API has server-side context editing (clearing old tool results) and compaction.

## Idempotency: assume every write can happen twice

A write tool can run twice for reasons that have nothing to do with the model's intent: your loop retries after a timeout, an approval webhook is delivered twice, a resumed run replays a turn, or the model simply calls `issue_refund` again because it didn't trust the first result.

| Pattern | How it works |
|---|---|
| Idempotency key | Pass a unique key with each write; the downstream system returns the original result for a repeated key. The `tool_use` block's `id` works as the key for **replays of the same call**: a duplicate webhook, a resumed run, your own retry of that execution. It does **not** catch the model calling `issue_refund` again, or a turn regenerated after a timeout: each of those is a new `tool_use` block with a new id |
| Natural key check | "Refund for booking X with reason Y already exists" → return it instead of creating another. This is the check that covers re-issued calls and regenerated turns, so risky writes need it in addition to the id |
| Conditional writes | "Cancel only if status is `confirmed`" |

Reads are safe to repeat. Writes must be safe to repeat. Say this sentence in your design round.

## Permission tiers and approval gates

Classify every tool by what it can break, then decide who can run it.

| Tier | Examples | Policy |
|---|---|---|
| Read | `get_booking`, `get_flight_status` | Run automatically; scope to the signed-in traveler's data |
| Reversible write, small | Refund ≤ $200, hold a seat | Run automatically with hard limits in code; audit |
| Irreversible or large | Cancel a booking, refund > $200, email a customer | Pause for a human; audit who approved what |

Rules that separate a good gate from a decorative one:

1. **Enforce it in code, not in the prompt.** "Never refund over $200 without approval" in a system prompt is a suggestion. An `if` statement in the executor is a control.
2. **Fail closed.** Only an explicit approval runs the action. A timeout, a missing decision, `"yes"` instead of `True`, or an exception in the approval service all mean no.
3. **Approve the exact call.** The reviewer approves "refund $612.00 on FW7Q2K for airline_cancellation", tied to that `tool_use` id, not "refunds for Ana".
4. **Show a one-line summary**, with the facts needed to decide (who, how much, why, what they paid). Reviewers who see raw JSON rubber-stamp or reject everything.
5. **Audit every resolved call**: tool, input, decision (`auto`, `approved`, `declined`), approver, and whether it errored.
6. **Tell the model what happened.** A declined call goes back as an `is_error` tool_result ("A supervisor declined this action. Do not retry it."), so it explains instead of retrying.

The hard part is timing. Approvals take minutes or hours, and the API needs every `tool_use` answered in the next user message. So you **persist the conversation, run the safe calls, hold the risky one, and resume later** with all of that turn's results together. You'll build exactly this next. (The SDK's tool runner can also gate calls inside the tool function; a long human wait is where a persisted, hand-written loop earns its keep.)

## MCP: what it is and when a customer wants it

The **Model Context Protocol (MCP)** is an open protocol for exposing tools, prompts and resources from a **server** to any MCP-compatible **client**. Claude Code, the Claude apps and the Claude Agent SDK are MCP clients, and you can write your own.

How Claude reaches MCP servers today (verified against Anthropic's SDK docs):

| Path | How | Notes |
|---|---|---|
| Your own app, manual or tool runner | The Python SDK's MCP helpers (`anthropic[mcp]`) convert MCP tools, prompts and resources into API types | Works with local servers (stdio) and gives you full control; beta |
| Messages API MCP connector | `mcp_servers=[{"type": "url", ...}]` plus a `{"type": "mcp_toolset", "mcp_server_name": ...}` entry in `tools`, beta `mcp-client-2025-11-20` | Anthropic connects to a **remote** server for you |
| Claude Managed Agents | MCP servers declared on the agent, credentials kept in a vault | MCP toolsets default to an `always_ask` permission policy: each call waits for confirmation |

**When a customer wants an MCP server:**

- The same system (orders, tickets, a data warehouse) must be reachable from **several** Claude surfaces: their support agent, an internal ops agent, analysts using Claude apps or Claude Code. One server, one permission model, many clients.
- They're a software vendor and want **their** product usable from their customers' AI tools.
- Different teams own the tools and the agent. MCP is the contract between them.

**When they don't:** one application, three tools, one team. Plain tool definitions in your code are simpler to test, version and debug. Adding a protocol boundary there buys you a network hop and nothing else.

Whatever the transport, the rules above still apply: least privilege on the server, validation inside it, approval for writes, and **treat what comes back as untrusted data**. A third-party server's tool descriptions also become part of your prompt, so connect only servers you trust.

## Practice

Original prompts in the style of a design round. Two minutes each.

1. "Design the tool set for an agent that handles flight cancellations for a travel agency. For each tool: inputs, outputs, risk tier, and what happens if it's called twice."
2. "Your agent sometimes refunds the wrong booking for travelers with several trips. Strict mode is on. What's going on, and where do you fix it?"
3. "A customer's CTO says 'we want an MCP server'. What do you ask before agreeing?"

> **Key takeaways**
> - Prefer dedicated, typed tools over a god tool: your harness can gate, audit, render and parallelize them.
> - Descriptions say *when* to call a tool; `strict: true` guarantees shape, never meaning. Ranges, ownership and policy live in code.
> - Return compact results with stable IDs and errors that tell the model how to fix the call.
> - Make writes idempotent: the `tool_use` id dedupes replays of one call, and a natural-key check (booking plus reason) catches the model re-issuing the call with a new id.
> - Approval gates live in code, fail closed, approve the exact call, and audit every decision.
> - MCP earns its place when many clients or teams share one system; for a single app, plain tools are simpler.
