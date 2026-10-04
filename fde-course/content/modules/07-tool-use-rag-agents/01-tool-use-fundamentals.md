---
title: "Tool Use: How Claude Calls Your Code"
type: reading
minutes: 18
---

> **By the end of this lesson you will be able to:**
> - Explain the request → tool_use → tool_result → answer cycle
> - Define tools with clear names, descriptions, and strict JSON Schemas
> - Return results and errors in exactly the shape the API expects
> - Apply the security rules that matter once Claude can trigger real actions

## Why tools change everything

So far, Claude has worked with whatever text you put in the prompt. Real customer questions need live data: *"Where's my order B-1001?"* The answer is in Brightway Retail's order system, not in Claude's training data. **Tool use** lets Claude ask *your code* to fetch that data (or take an action), then use the result in its answer.

Our customer for this module is **Brightway Retail**, the retailer whose shipments you synced from Northwind in Module 4. They want a customer-service assistant that can look up orders, track shipments, and issue store credit.

## The cycle

```
1. You → Claude:   question + tool definitions
2. Claude → you:   stop_reason "tool_use", with a tool_use block:
                   {name: "lookup_order", input: {"order_id": "B-1001"}, id: "toolu_01..."}
3. You:            run lookup_order("B-1001") in your own code
4. You → Claude:   the conversation so far + a tool_result block for that id
5. Claude → you:   stop_reason "end_turn", with the final answer text
```

Two things to internalize:

- **Claude never runs your code.** It *asks*; your code decides whether and how to run it. That's where you put validation, permissions, and safety checks.
- **The API is still stateless.** Step 4 resends the whole conversation, including Claude's `tool_use` turn, plus your result.

## Defining a tool

A tool is a name, a description, and a JSON Schema for its input:

```python
LOOKUP_ORDER = {
    "name": "lookup_order",
    "description": (
        "Look up a Brightway order by its ID (format B-1234). Returns status, items, total and "
        "shipment ID. Call this whenever the customer mentions an order number or asks about an order."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "order_id": {"type": "string", "description": "Order ID such as B-1001"},
        },
        "required": ["order_id"],
        "additionalProperties": False,
    },
    "strict": True,
}
```

What makes a tool definition good:

- **A specific name:** `lookup_order`, not `data` or `helper`.
- **A description that says *when* to call it**, not just what it does. Claude decides whether to use a tool largely from its description. "Call this whenever the customer mentions an order number" measurably increases correct usage.
- **Descriptions on each property,** with formats and examples.
- **`enum` for fixed choices** (`"reason": {"enum": ["late_delivery", "damaged", "goodwill"]}`).
- **`strict: True`** guarantees Claude's input matches your schema exactly. Strict schemas need `additionalProperties: False` and a full `required` list, like structured outputs.
- **A focused set of tools.** Five well-described tools beat thirty overlapping ones.

## Reading the tool_use response

```python
response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=16000,
    tools=[LOOKUP_ORDER],
    messages=[{"role": "user", "content": "Where is my order B-1001?"}],
)

if response.stop_reason == "tool_use":
    for block in response.content:
        if block.type == "tool_use":
            print(block.id, block.name, block.input)   # toolu_01...  lookup_order  {'order_id': 'B-1001'}
```

The response can also contain thinking and text blocks (for example "Let me look that up"), so loop over the blocks and pick out the `tool_use` ones. `block.input` is already a parsed Python dict.

## Sending the result back

```python
result = lookup_order(block.input["order_id"])            # your code

messages = [
    {"role": "user", "content": "Where is my order B-1001?"},
    {"role": "assistant", "content": response.content},     # Claude's full turn, unchanged
    {"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": block.id, "content": json.dumps(result)},
    ]},
]
final = client.messages.create(model="claude-opus-5-5", max_tokens=16000, tools=[LOOKUP_ORDER], messages=messages)
```

The rules the API enforces:

1. **Append Claude's full `response.content`** as the assistant turn, so its `tool_use` blocks are present.
2. **The very next user message must contain a `tool_result` for every `tool_use` id.** Miss one and the API returns a 400 error.
3. **Keep sending the same `tools`** on follow-up requests.
4. **`content` is a string** (JSON is a good choice for structured data) or a list of content blocks.

## When the tool fails

Tools fail: the order doesn't exist, the database times out, the input is invalid. Don't crash and don't invent data. Return the error to Claude:

```python
{"type": "tool_result", "tool_use_id": block.id, "is_error": True,
 "content": "No order found with ID B-9999. Order IDs look like B-1001."}
```

Claude will usually explain the problem to the user or ask for a corrected order number. Informative error messages ("Order IDs look like B-1001") help it recover.

## Several tools at once

Claude can request **multiple tools in one turn**, for example looking up an order and tracking its shipment in parallel. Run them all and send **all the results back in one user message**, each with its own `tool_use_id`. Splitting them across messages breaks the rule above.

## Controlling tool use

`tool_choice` controls whether Claude may use tools:

| Value | Behavior |
|---|---|
| `{"type": "auto"}` | Claude decides (the default) |
| `{"type": "none"}` | Tools are visible but can't be called |

Older models also accepted "force a tool" options (`any`, or a specific tool), but **Claude Opus 5.5 rejects forced tool use**. If you need Claude to use a particular tool, say so in the prompt ("Use lookup_order to check the status") and check that a call was made. If you only wanted JSON, use structured outputs instead.

## Security: Claude's input is untrusted

Tool inputs are generated from a conversation that includes **user text**. A customer can type anything, including attempts to get the assistant to look up someone else's order or issue a huge credit. So:

- **Validate every input** in your tool code: formats, ranges, and especially **authorization** ("does this order belong to the signed-in customer?"). The schema checks shape; your code checks permission.
- **Separate reads from writes.** Reading an order is low risk. Issuing credit, refunds, or emails needs limits and often human approval (lesson 7).
- **Log every tool call** with its input and result. When something goes wrong, the log is the story of what happened.

> **Key takeaways**
> - Claude asks for tool calls; your code runs them, after validating inputs and permissions.
> - Good tools have specific names, descriptions that say when to call them, property descriptions, enums, and strict schemas.
> - Append Claude's full turn, then answer every tool_use id with a tool_result in the next user message; use `is_error` for failures.
> - Claude Opus 5.5 supports `tool_choice` auto and none only; ask for a tool in the prompt and check the call was made.
