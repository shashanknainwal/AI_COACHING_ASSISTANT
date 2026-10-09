---
title: "Exercise: Pause for Approval, Resume Later"
type: exercise
minutes: 45
hints:
  - "`requires_approval`: `True` for `cancel_booking`; for `issue_refund`, `tool_input[\"amount\"] > AUTO_REFUND_LIMIT`; `False` otherwise."
  - "In `run_agent`, check `state[\"iterations\"] >= MAX_ITERATIONS` before each call, then increment it after the call. Append `response.content` to `state[\"messages\"]`."
  - "For a `tool_use` turn, walk the blocks in order: risky ones go into a `pending` list as `{\"id\", \"tool\", \"input\", \"summary\": describe(...)}`; safe ones run now with `execute(block)` and get an `\"auto\"` audit entry. Keep their results in a dict keyed by `block.id`."
  - "If anything is pending, save the call order, the results so far and the pending list in `state`, and return without appending a user message. Otherwise append one user message with all results in call order and loop."
  - "`resume`: raise `ValueError(\"no pending approvals\")` if nothing is pending, then clear `state[\"pending\"]` before running anything. Approve only when `decisions.get(id, {}).get(\"approved\") is True`; rebuild the block with `anthropic.ToolUseBlock(p[\"tool\"], p[\"input\"], id=p[\"id\"])` so `execute()` uses the original id as the idempotency key."
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
