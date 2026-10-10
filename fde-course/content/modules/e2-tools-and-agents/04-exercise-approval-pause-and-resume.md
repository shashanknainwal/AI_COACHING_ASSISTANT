---
title: "Exercise: Pause for Approval, Resume Later"
type: exercise
minutes: 45
hints:
  - "`requires_approval` is a pure policy function: the tool name decides it for cancellations, and the amount decides it for refunds."
  - "Count API calls in `state`, not in a local variable, because a paused run is resumed in a later call. Check the cap before each request."
  - "In a `tool_use` turn, sort each block into 'run now' or 'hold'. Run the safe ones immediately and keep their results so they can go back later in the same message as the held ones."
  - "If anything is held, the turn can't be answered yet: persist what you need to rebuild that one user message later (the call order, the results so far, the held calls) and return without sending anything."
  - "`resume`: make a second delivery of the same webhook harmless by changing state before you run anything. Treat anything other than an explicit `True` as a decline, and execute approved calls under their original `tool_use` id so the idempotency key still matches."
---

Leo is back with the Fernway file. "Their finance team signed off on the agent with one condition: any refund over $200, and every cancellation, needs a supervisor. Supervisors answer in Slack, sometimes an hour later, so the agent can't block a thread waiting. It has to stop, save its state, and pick up when the decision lands. And their payments team has seen webhooks arrive twice, so a resumed run must never refund twice."

The tools, an `execute(block)` helper, and a `describe()` helper for reviewer summaries are given. `execute` already passes the `tool_use` id to `issue_refund` as its idempotency key. You write the policy, the pausable loop and the resume step.

## The shape of a pause

The API requires a `tool_result` for **every** `tool_use` in Claude's turn, all in the next user message. So when a turn mixes a safe call and a risky one, you:

1. Run the safe calls now.
2. Hold the risky calls and return `"awaiting_approval"`. The conversation ends with Claude's `tool_use` turn; you make no API call while paused.
3. When decisions arrive, run or decline each held call, then send **all** of that turn's results together, in the original order, and continue the loop.

## Your task

`state` is a dict that must hold at least `"messages"`, `"iterations"` (API calls so far, across pauses) and `"pending"`. Add whatever else you need. `start()` is given.

**1. `requires_approval(name, tool_input)`**: `True` for `cancel_booking`, and for `issue_refund` when `amount > AUTO_REFUND_LIMIT` ($200). Everything else is `False`.

**2. `run_agent(client, state, audit)`** drives the loop and returns `{"status", "answer", "pending"}`:
- Before each call, if `state["iterations"] >= MAX_ITERATIONS`, return status `"max_iterations"`.
- Each request uses `MODEL`, `MAX_TOKENS`, `SYSTEM_PROMPT`, `TOOLS` and `state["messages"]`. Append `response.content` unchanged.
- Not `tool_use`: return status `"completed"` with the text as `answer` and `pending: []`.
- `tool_use`: for each block in order, run safe calls with `execute(block)` and audit them as `"auto"`; hold risky ones as `{"id", "tool", "input", "summary": describe(name, input)}`.
- If anything is held: return `{"status": "awaiting_approval", "answer": None, "pending": [...]}`. Otherwise send all results in one user message and continue.

**3. `resume(client, state, decisions, audit)`**: `decisions` maps a `tool_use` id to `{"approved": ..., "approver": "maria.chen"}`.
- If nothing is pending, raise `ValueError("no pending approvals")`.
- **Fail closed:** run a held call only if its decision has `approved` exactly `True`. Missing, `"yes"`, `None` or `False` means declined: don't run it, and use `{"type": "tool_result", "tool_use_id": id, "content": DECLINED_MESSAGE, "is_error": True}`.
- Run approved calls through `execute()` with a `ToolUseBlock` carrying the **original** id.
- Send every result from that turn in one user message, in call order, then keep driving with `run_agent`.

**Audit entries** (one per resolved call, in the order resolved): `{"tool", "input", "decision", "approver", "is_error"}` with `decision` in `"auto"`, `"approved"`, `"declined"`, and `approver` `None` for auto calls. Held calls aren't audited until they're decided.

## Example

```python
>>> outcome, state = start(client, "Booking FW7Q2K: the airline cancelled my flight. Please refund the full fare.", audit)
>>> outcome["status"], outcome["pending"][0]["summary"]
('awaiting_approval', 'Refund $612.00 to Ana Souza (FW7Q2K, fare paid $612.00) for airline_cancellation.')
>>> REFUNDS
[]
>>> resume(client, state, {outcome["pending"][0]["id"]: {"approved": True, "approver": "maria.chen"}}, audit)["status"]
'completed'
```

Press **Run** to watch one pause and approval, check the **Trace** tab, then **Submit**.

## Beyond one process

Clearing `pending` before running anything stops a duplicate webhook only when both deliveries reach the same process. In production, two workers can load the same saved state at once. The distributed version of the same idea is a **compare-and-set on the persisted run state** (for example `UPDATE runs SET status='resuming' WHERE id=? AND status='awaiting_approval'`, and only the worker whose update changed a row proceeds) or a lock keyed on the run id. Keep the payments-side idempotency key as well: defence in depth.
