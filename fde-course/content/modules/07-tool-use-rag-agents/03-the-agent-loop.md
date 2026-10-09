---
title: "The Agent Loop"
type: reading
minutes: 6
---

> **By the end of this lesson you will be able to:**
> - Write the loop that lets Claude chain tool calls
> - Bound it so it can't run forever or run up a bill
> - Trace each run, and know when to use the SDK's tool runner

Jordan forwards a real ticket: *"My lamp order is late. Can you check what's going on and make it right?"* Answering it takes a chain: look up the order, track the shipment, check the policy and issue a credit, then explain. Claude picks each step from what the last one returned. Running that repeatedly is the **agent loop**.

## The loop

```python
def run_agent(client, question, max_steps=6):
    messages = [{"role": "user", "content": question}]
    for step in range(1, max_steps + 1):
        response = client.messages.create(
            model="claude-opus-5-5", max_tokens=16000, system=SYSTEM, tools=TOOLS, messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            return "".join(b.text for b in response.content if b.type == "text")

        results = [execute(b) for b in response.content if b.type == "tool_use"]
        messages.append({"role": "user", "content": results})

    raise RuntimeError("agent did not finish within max_steps")
```

Everything else is safety and observability.

<div data-diagram="agent-loop"></div>

## Bound everything

A confused agent can call the same failing tool forever, and each step resends a growing history.

| Limit | Typical setting |
|---|---|
| Max steps | 5-10 for support tasks; fail clearly or hand off to a human |
| Token or cost budget | Sum `usage` across steps; stop when exceeded |
| Time | A customer in chat won't wait two minutes |
| Limits inside tools | Credit caps, email rate limits |

Loop limits stop runaway behavior; tool limits stop harmful behavior.

## Make it traceable

```
step 1  tool_use  lookup_order(order_id="B-1001")         → shipped, SHP-1003
step 2  tool_use  track_shipment(shipment_id="SHP-1003")  → exception: weather delay
step 3  tool_use  issue_store_credit(C-100, 25, late_delivery) → new balance $25.00
step 4  end_turn  "I'm sorry your lamp is delayed..."
```

Log each call's name, input, result or error and timing, plus the final answer and total tokens. The trace answers "why did the assistant give this customer $25?" and feeds the evals in Module 8.

When a tool fails, return an `is_error` result and keep looping; Claude often recovers. Stop only for what Claude can't fix: the step limit, the budget, or your own infrastructure failing. Keep tool results **compact** (the fields Claude needs, not whole rows); for very long runs the API offers context management such as clearing old tool results and server-side compaction.

## The SDK's tool runner

In production, the SDK's **tool runner** (beta) runs this loop for you from decorated functions:

```python
from anthropic import beta_tool

@beta_tool
def lookup_order(order_id: str) -> str:
    """Look up a Brightway order by its ID (format B-1234).

    Args:
        order_id: Order ID such as B-1001.
    """
    return json.dumps(find_order(order_id))

runner = client.beta.messages.tool_runner(model="claude-opus-5-5", max_tokens=16000,
    tools=[lookup_order], messages=[{"role": "user", "content": "Where is order B-1001?"}])
for message in runner:        # one message per step
    print(message)
```

It builds schemas from docstrings and still lets you inspect each step. (The in-browser simulator supports the manual loop only.)

Before building an agent, check that the steps really can't be written in advance, that the value is worth several calls per request, and that mistakes can be caught and undone (lesson 7).

> **Key takeaways**
> - Loop: call, run every tool, send all results in one message, repeat until Claude stops.
> - Bound steps, tokens, time, and risky tools.
> - Trace every step, keep results compact, let Claude recover from tool errors.
