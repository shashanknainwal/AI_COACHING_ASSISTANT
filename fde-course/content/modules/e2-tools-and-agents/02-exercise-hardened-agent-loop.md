---
title: "Exercise: Harden a Trip-Support Agent Loop"
type: exercise
minutes: 40
hints:
  - "`execute_tool`: there are four outcomes in the table. Start from the fields every result shares, and handle the unknown-tool case before you try to call anything."
  - "Order your `except` clauses from most specific to least. Ask of each failure: is this message safe and useful for the model to read? A `ToolError` was written for the model; an arbitrary exception was not."
  - "`run_agent`: one loop over API calls. Each pass records usage, appends the assistant turn unchanged, then decides what to do from `stop_reason`."
  - "The order of your stop-reason checks matters. Which turns must never have their tools run? And on the last allowed call, what should happen before any tool runs?"
  - "A `tool_use` turn produces exactly one user message, however many tools were called. Build the results first, append once."
---

Leo Martins drops a file into your shared folder. "Treat this like a take-home. Fernway Travel, a fictional corporate travel agency, has a trip-support agent that a contractor wrote. It works in the demo. In production it crashed when the flight-ops database timed out, looped 40 times on one ticket, and once leaked an internal database hostname into a reply. Make the loop production-safe. I'll review it like a PR."

The tools, their schemas and sample data are given. You write the tool executor and the loop. The simulated Claude behaves like the real API: it can ask for two tools in one turn, it can get cut off, and it can refuse.

## Your task

**1. `execute_tool(block)`** runs one `tool_use` block and returns a `tool_result` dict. It must **never raise**.

| Case | Returned dict |
|---|---|
| Success | `{"type": "tool_result", "tool_use_id": block.id, "content": json.dumps(return_value)}` |
| Tool raised `ToolError` | same keys plus `"is_error": True`, content `str(exc)` |
| Name not in `TOOL_FUNCTIONS` | `"is_error": True`, content `"Unknown tool: <name>"` |
| Any other exception | `"is_error": True`, content `"<name> failed unexpectedly (<ExceptionClass>). Try again later or tell the traveler."` |

Look tools up in `TOOL_FUNCTIONS` at call time. For unexpected exceptions, include only the class name: the exception's text can hold internal details.

**2. `run_agent(client, question, max_iterations=6)`** returns:

```python
{"status": "completed", "answer": "...", "iterations": 3,
 "tool_calls": [{"name": "get_booking", "input": {...}, "is_error": False}, ...],
 "usage": {"input_tokens": 1672, "output_tokens": 64}}
```

- Every request: `model=MODEL`, `max_tokens=MAX_TOKENS`, `system=SYSTEM_PROMPT`, `tools=TOOLS`, and no forced `tool_choice`.
- Append each `response.content` unchanged as the assistant turn.
- `stop_reason == "refusal"`: status `"refusal"`, answer `REFUSAL_MESSAGE`. Run no tools from that turn.
- `stop_reason == "max_tokens"`: status `"max_tokens"`, answer = the text blocks you got. Run no tools from that turn.
- Any other non-`tool_use` stop: status `"completed"`, answer = all text blocks joined.
- `tool_use`: run every `tool_use` block with `execute_tool`, and send all the results back in **one** user message, in call order.
- If Claude still wants tools on call number `max_iterations`, return status `"max_iterations"` with answer `HANDOFF_MESSAGE` **without** running those tools or making another call.
- `iterations` is the number of API calls. `usage` sums `input_tokens` and `output_tokens` over every call.

## Example

```python
>>> run_agent(client, "Booking FW7Q2K: I just got a cancellation email. What are my options?")["tool_calls"]
[{'name': 'get_booking', ...}, {'name': 'get_flight_status', ...}, {'name': 'find_alternatives', ...}]
```

The second and third tool calls come from **one** assistant turn. Press **Run**, then open the **Trace** tab: you'll see both calls under one step, and the RT5V1C run's failed lookup marked in red. Then **Submit**.
