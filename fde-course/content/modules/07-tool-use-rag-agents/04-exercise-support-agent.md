---
title: "Exercise: A Support Agent with Three Tools"
type: exercise
minutes: 35
hints:
  - "Tool functions use the module-level `CUSTOMERS`, `ORDERS`, `SHIPMENTS` dicts. `reset_data()` (given) restores them."
  - "`issue_store_credit`: validate `0 < amount <= CREDIT_LIMIT` first (raise `ValueError(f\"amount must be between 0 and {CREDIT_LIMIT}\")`), then the customer (raise `KeyError`)."
  - "`execute`: look up `TOOL_FUNCTIONS.get(block.name)`, call it with `**block.input`, and catch `(KeyError, ValueError)`, using `e.args[0]` as the error content."
  - "In `run_agent`, keep `messages`, a `trace` list, and loop `for step in range(1, max_steps + 1)`."
  - "Record every tool call in the trace before moving on: `{\"tool\": block.name, \"input\": block.input, \"is_error\": result.get(\"is_error\", False)}`."
  - "Return when `stop_reason != \"tool_use\"`. If the loop ends without returning, `raise RuntimeError(\"agent did not finish within max_steps\")`."
---

Brightway's assistant now gets three tools: look up orders, track shipments, and issue store credit (up to $50 without approval, per Brightway's policy). You'll write the tools, a safe executor, and the agent loop with a trace.

The data comes from `fde_datasets.brightway`; `reset_data()` gives you fresh copies.

## Your task

**1. Tool functions** (each returns a dict; failures raise):
- `lookup_order(order_id)` → `{"order_id", "customer_id", "status", "shipment_id", "total"}`. Unknown → `KeyError("No order found with ID <id>.")`.
- `track_shipment(shipment_id)` → `{"shipment_id", "status", "eta", "last_event"}`. Unknown → `KeyError("No shipment found with ID <id>.")`.
- `issue_store_credit(customer_id, amount, reason)` → adds `amount` to the customer's `store_credit` and returns `{"customer_id", "new_balance"}`. Check `0 < amount <= CREDIT_LIMIT` first: otherwise `ValueError("amount must be between 0 and 50")`. Unknown customer → `KeyError("No customer found with ID <id>.")`.

**2. `TOOLS`**: three strict tool definitions with these names and inputs: `order_id` (string), `shipment_id` (string), and `customer_id` (string) + `amount` (number) + `reason` (string, `"enum": CREDIT_REASONS`). Every description must say when to call the tool.

**3. `execute(block)`** runs a `tool_use` block through `TOOL_FUNCTIONS` and returns a `tool_result`: JSON content on success; `is_error: True` with the exception message on `KeyError`/`ValueError`; `is_error` with `"Unknown tool: <name>"` for unknown names.

**4. `run_agent(client, question, max_steps=6)`** runs the loop from the lesson and returns:

```python
{"answer": "...", "steps": 4, "trace": [{"tool": "lookup_order", "input": {...}, "is_error": False}, ...]}
```

`steps` is the number of API calls made. Each request uses `model=MODEL`, `max_tokens` ≥ 4096, `system=SYSTEM_PROMPT`, `tools=TOOLS`. All results from one turn go back in a single user message. If Claude is still calling tools after `max_steps` calls, raise `RuntimeError("agent did not finish within max_steps")`.

Press **Run** to watch the agent handle a late-delivery complaint, then **Submit**.
