---
title: "The Agent Loop"
type: reading
minutes: 16
---

> **By the end of this lesson you will be able to:**
> - Write the agent loop that lets Claude chain several tool calls to finish a task
> - Bound the loop so it can't run forever or run up a surprise bill
> - Trace an agent's run step by step for debugging and audits
> - Explain when to use the SDK's tool runner instead of a hand-written loop

## From one tool call to many

In the last exercise, Claude made at most one round of tool calls. Real requests often need a chain:

> *"My lamp order is late. Can you check what's going on and make it right?"*

1. Look up the order → get the shipment ID.
2. Track the shipment → it's delayed.
3. Check the policy and issue a late-delivery credit.
4. Explain what happened and what was done.

Claude decides each next step based on what the previous one returned. Running that decision-making repeatedly is the **agent loop**.

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

That's the whole pattern: **call → if Claude wants tools, run them all and send all results back → repeat until Claude stops asking.** Everything else is about making it safe and observable.

<div data-diagram="agent-loop"></div>

## Bound everything

An unbounded loop is a production incident waiting to happen. A confused agent can call the same failing tool over and over, and every iteration resends a growing history (more tokens, more cost).

- **Maximum steps:** stop after N iterations and fail clearly (or hand off to a human). 5-10 is typical for customer-service tasks.
- **Maximum cost or tokens:** track `usage` across iterations and stop if a budget is exceeded.
- **Time limits:** a user waiting in chat won't wait two minutes.
- **Limits inside tools:** caps on refund amounts, rate limits on emails. The loop's limits protect against runaway behavior; the tools' limits protect against harmful behavior.

## Make it traceable

When an agent does something surprising, you need to know exactly what happened. Record a **trace** for every run:

```
step 1  tool_use  lookup_order(order_id="B-1001")         → shipped, SHP-1003
step 2  tool_use  track_shipment(shipment_id="SHP-1003")  → exception: weather delay
step 3  tool_use  issue_store_credit(C-100, 25, late_delivery) → new balance $25.00
step 4  end_turn  "I'm sorry your lamp is delayed..."
```

Log the tool name, input, result (or error), and timing for each call, plus the final answer and total tokens. Traces are how you debug, how you answer "why did the assistant give this customer $25?", and the raw material for evaluations in Module 8.

## Errors inside the loop

When a tool fails, return an `is_error` result and let the loop continue. Claude can often recover: retry with a corrected input, try a different tool, or explain the problem. Only stop the loop for problems Claude can't fix (the max-step limit, an exhausted budget, or a failure in your own infrastructure).

## Context grows with every step

Each iteration appends Claude's turn and the tool results. Large tool results (a full order history, a 50-page document) quickly fill the context and raise cost. Keep tool results **compact**: return the fields Claude needs, not entire database rows. For very long-running agents, the API also offers context-management features (such as clearing old tool results and server-side compaction) that you can read about when you need them.

## The SDK's tool runner

Writing the loop yourself is the best way to understand it, and you'll do that in the next exercise. In production code, the Anthropic SDK offers a **tool runner** (a beta feature) that runs this loop for you: you write plain Python functions, decorate them, and the runner handles calling the API, running tools, and sending results back.

```python
import anthropic
from anthropic import beta_tool

client = anthropic.Anthropic()

@beta_tool
def lookup_order(order_id: str) -> str:
    """Look up a Brightway order by its ID (format B-1234).

    Args:
        order_id: Order ID such as B-1001.
    """
    return json.dumps(find_order(order_id))

runner = client.beta.messages.tool_runner(
    model="claude-opus-5-5",
    max_tokens=16000,
    tools=[lookup_order],
    messages=[{"role": "user", "content": "Where is order B-1001?"}],
)
for message in runner:        # one message per step; the loop ends when Claude stops calling tools
    print(message)
```

The runner generates tool schemas from your function signatures and docstrings, and still lets you inspect each step, so you can log traces and add approval gates. (The course's in-browser simulator supports the manual loop; use the tool runner on your own machine with the real SDK.)

## Agents aren't always the answer

Agents are powerful and genuinely expensive: multiple calls per request, harder to test, harder to predict. Before building one, check:

- **Is the task truly multi-step and hard to specify in advance?** If the steps are always "look up order, then track shipment," write that as plain code that calls Claude once at the end. (Lesson 7 covers this trade-off.)
- **Is the value worth the cost and latency?**
- **Can mistakes be caught and undone?**

> **Key takeaways**
> - The agent loop: call, run every requested tool, send all results back in one message, repeat until Claude stops asking.
> - Bound it: max steps, token/cost budgets, time limits, and hard limits inside risky tools.
> - Record a trace of every step; keep tool results compact; let Claude recover from tool errors.
> - In production, the SDK's tool runner implements this loop for you; use an agent only when the task really needs one.
