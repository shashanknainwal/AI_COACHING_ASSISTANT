---
title: "Exercise: Your First Tool, End to End"
type: exercise
minutes: 30
hints:
  - "`LOOKUP_ORDER_TOOL`: copy the shape from the lesson. The property is `order_id` (string); add `\"additionalProperties\": False` and `\"strict\": True`."
  - "`lookup_order`: normalize with `order_id.strip().upper()`. If it isn't in `ORDERS`, raise `KeyError(f\"No order found with ID {order_id}.\")`."
  - "`run_tool`: wrap the call in `try/except KeyError as e` and build `{\"type\": \"tool_result\", \"tool_use_id\": block.id, \"content\": ..., \"is_error\": True}` on failure. `str(e)` of a KeyError includes quotes, so use `e.args[0]`."
  - "`answer`: after the first call, if `stop_reason != \"tool_use\"`, just return its text."
  - "Collect a tool_result for **every** tool_use block (there might be more than one), append the assistant turn and one user turn with all results, then call again with the same tools."
---

Brightway's first assistant feature: answer "where's my order?" questions using live order data. You'll build the tool, the code that runs it, and the full two-call cycle.

Order data comes from `fde_datasets.brightway` (`ORDERS` is imported for you).

## Your task

**1. `LOOKUP_ORDER_TOOL`**: a strict tool definition named `lookup_order` with one required string property `order_id`. Its description must say **when** to call it and include the words `order ID`.

**2. `lookup_order(order_id)`** returns a dict for the order: `{"order_id", "status", "total", "items", "shipment_id"}`, where `items` is a list of item names. Normalize the ID (strip, uppercase). Unknown IDs raise `KeyError("No order found with ID <normalized id>.")`.

**3. `run_tool(block)`** takes one `tool_use` block and returns a `tool_result` dict:
- Success: `{"type": "tool_result", "tool_use_id": block.id, "content": json.dumps(result)}`
- `KeyError`: the same, but `content` is the error message and `"is_error": True` is added.
- A tool name other than `lookup_order`: `is_error` result with content `"Unknown tool: <name>"`.

**4. `answer(client, question)`** runs the full cycle and returns Claude's final text:
1. Call Claude with `model=MODEL`, `max_tokens` ≥ 4096, `system=SYSTEM_PROMPT`, `tools=[LOOKUP_ORDER_TOOL]`, and the question.
2. If `stop_reason` isn't `"tool_use"`, return the text.
3. Otherwise run every `tool_use` block, then call Claude again with the history: question, Claude's **full** turn, and **one** user turn containing all the tool results. Return the final text.

Press **Run** to ask about a real order and a non-existent one, then **Submit**.
