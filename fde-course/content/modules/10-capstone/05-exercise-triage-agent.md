---
title: "Exercise: Build the Exception-Triage Agent"
type: exercise
minutes: 45
hints:
  - "`notify_customer`: check the length first, then each word in `BANNED_WORDS` with `re.search(rf\"\\b{word}\", message.lower())`. The `\\b` stops 'credit' from matching inside other words, while still catching 'credited'."
  - "`guarded_execute`: handle unknown tools first, then the approval gate (only for `WRITE_TOOLS_NEEDING_APPROVAL`, approved only when the approver returns exactly `True`, and an exception means declined), then run the tool inside `try/except (KeyError, ValueError)`."
  - "Every path through `guarded_execute` appends exactly one audit entry: `{\"tool\", \"input\", \"approval\", \"is_error\"}`."
  - "`run_triage`: the loop from Module 7. Send `system=SYSTEM_PROMPT` and `tools=TOOLS` every time, and all tool results from a turn in one user message."
  - "When Claude stops calling tools, the decision is the `input` of the last successful `record_decision` entry in the audit, or `None` if there isn't one."
---

This is the system the engagement is about. Given a shipment ID, the agent looks up the shipment, decides the priority, tells the customer what's happening, opens a ticket when a coordinator must act, proposes a backup carrier for missed pickups (with a coordinator's approval), and records its decision. NorthStar's hard rules from discovery become **code**, not just prompt text.

Given:
- The clean data: `SHIPMENTS`, `LATEST` and `CUSTOMERS`.
- `SYSTEM_PROMPT`, the five strict `TOOLS`, and the tool functions `get_shipment`, `create_ops_ticket`, `reroute_shipment` and `record_decision`.
- The constants `BANNED_WORDS`, `MAX_MESSAGE_CHARS`, `WRITE_TOOLS_NEEDING_APPROVAL` and `DECLINED`.

## Your task

**1. `notify_customer(shipment_id, message)`** is the guardrail for customer messages:
- Unknown shipment: `KeyError("No shipment found with ID <id>.")`.
- Longer than 600 characters: `ValueError("message is 612 characters; the limit is 600")`.
- Contains a word **starting with** any of `BANNED_WORDS`, ignoring case: `ValueError("message must not promise compensation (found 'credit')")`. Check the words in `BANNED_WORDS` order and report the first one found.
- Otherwise return `{"status": "queued", "to": <the customer's contact email>}`.

**2. `guarded_execute(block, approver, audit)`** runs one `tool_use` block and returns a `tool_result`:
- Unknown tool: `is_error` with `"Unknown tool: <name>"`.
- `reroute_shipment` needs approval: call `approver({"tool": ..., "input": ...})`. Only an explicit `True` approves. Anything else, including an exception, means declined: return `is_error` with content `DECLINED` and don't run the tool.
- Otherwise run the function: JSON content on success, `is_error` with `e.args[0]` on `KeyError`/`ValueError`.
- Always append one audit entry: `{"tool", "input", "approval", "is_error"}`, where `approval` is `"not_required"`, `"approved"` or `"declined"`.

**3. `run_triage(client, shipment_id, approver, max_steps=8)`** runs the agent loop:
- Start with the user message `"Triage the exception for shipment <id>."`.
- Every request uses `model=MODEL`, `max_tokens` ≥ 4096, `system=SYSTEM_PROMPT` and `tools=TOOLS`.
- When Claude stops calling tools, return `{"decision": ..., "steps": <API calls>, "audit": [...]}`. The decision is the `input` of the last successful `record_decision` call, or `None`.
- After `max_steps` calls without finishing, raise `RuntimeError("triage did not finish within max_steps")`.

Press **Run** to triage four shipments, including one where the guardrail blocks a credit promise and Claude rewrites the message, then **Submit**.
