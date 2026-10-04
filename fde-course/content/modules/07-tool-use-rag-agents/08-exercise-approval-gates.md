---
title: "Exercise: Human-in-the-Loop Approval Gates"
type: exercise
minutes: 30
hints:
  - "`needs_approval`: `name == \"issue_store_credit\" and tool_input[\"amount\"] > AUTO_APPROVE_LIMIT`."
  - "`describe_action`: format money with `f\"${amount:.2f}\"`. For other tools use `json.dumps(tool_input, sort_keys=True)`."
  - "`guarded_execute`: call the approver inside `try/except Exception`, and treat the call as approved only if it returned exactly `True` (`approver(request) is True`)."
  - "On a decline, return `{\"type\": \"tool_result\", \"tool_use_id\": block.id, \"content\": DECLINED_MESSAGE, \"is_error\": True}` **without** calling `execute`."
  - "The approval label is `\"approved\"` after a yes, `\"auto\"` for a write tool that didn't need approval (`block.name in WRITE_TOOLS`), otherwise `\"not_required\"`."
---

Brightway's policy (help-center article KB-04): agents can issue up to **$50** of store credit on their own; larger amounts need a supervisor. Your agent from exercise 4 can now issue up to $200 (`HARD_LIMIT`), so a human must approve anything above $50.

The tools, `execute`, and the agent loop are given. The loop calls your `guarded_execute(block, approver, audit)` for every tool call. **Press Run first:** the starter runs every call without a check, so the "declined" $75 credit goes through anyway. That's the bug you're fixing.

An **approver** is a function your application provides (in production it might post to Slack and wait for a supervisor's click). It receives a request dict and returns `True` to approve.

## Your task

**1. `needs_approval(name, tool_input)`** returns `True` only for `issue_store_credit` with `amount > AUTO_APPROVE_LIMIT`. Reads never need approval.

**2. `describe_action(name, tool_input)`** returns the line the reviewer sees:
- `issue_store_credit`, known customer: `"Issue $80.00 store credit to Ben Ito (C-101, standard) for damaged_item. Current balance: $15.00."`
- unknown customer: `"Issue $60.50 store credit to unknown customer C-777 for goodwill."`
- any other tool: `'Run lookup_order with {"order_id": "B-1001"}'` (JSON with sorted keys).

**3. `guarded_execute(block, approver, audit)`**:
- If the call needs approval, call `approver({"tool": block.name, "input": block.input, "summary": describe_action(...)})`.
- **Fail closed:** only a return value of exactly `True` approves. `False`, `None`, `"yes"`, or an exception all mean declined.
- Declined → don't run the tool; return an `is_error` tool_result with content `DECLINED_MESSAGE`.
- Otherwise run it with `execute(block)` and return that result.
- Always append one audit entry: `{"tool", "input", "approval", "is_error"}`, where `approval` is `"not_required"` (reads), `"auto"` (writes within the limit), `"approved"`, or `"declined"`.

The tool's own `HARD_LIMIT` check still applies after approval: a supervisor can't approve $500.

Press **Run** to see three runs (auto-approved, approved, declined) with their audit logs, then **Submit**.
