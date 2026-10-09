---
title: "Tool Use: How Claude Calls Your Code"
type: reading
minutes: 3
---

> **By the end of this lesson you will be able to:**
> - Explain the request → tool_use → tool_result → answer cycle
> - Define tools with clear names, descriptions and strict schemas
> - Return results and errors in the shape the API expects

Jordan Lee, VP of Customer Support at Brightway Retail, wants an assistant that answers *"Where's my order B-1001?"* from Brightway's order system. **Tool use** lets Claude ask your code to fetch that data (or take an action), then use the result.

## The cycle

<div data-diagram="tool-cycle"></div>

**Claude never runs your code.** It asks; your code decides whether to run it, which is where validation and permissions live. The API is stateless, so the follow-up request resends the whole conversation plus your result.

## Defining a tool

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

| Do | Why |
|---|---|
| Specific name (`lookup_order`, not `helper`) | Claude picks tools by name and description |
| Description says **when** to call it | "Call this whenever the customer mentions an order number" measurably increases correct use |
| Property descriptions, `enum` for fixed choices; a small, focused tool set | Fewer malformed inputs and wrong picks |
| `strict: True` with `additionalProperties: False` and a full `required` list | Input is guaranteed to match the schema |

## Reading the response and sending the result back

```python
response = client.messages.create(model="claude-opus-5-5", max_tokens=16000,
    tools=[LOOKUP_ORDER], messages=[{"role": "user", "content": "Where is my order B-1001?"}])

if response.stop_reason == "tool_use":
    for block in response.content:
        if block.type == "tool_use":
            result = lookup_order(block.input["order_id"])   # block.input is a parsed dict

messages = [
    {"role": "user", "content": "Where is my order B-1001?"},
    {"role": "assistant", "content": response.content},     # Claude's full turn, unchanged
    {"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": block.id, "content": json.dumps(result)},
    ]},
]
final = client.messages.create(model="claude-opus-5-5", max_tokens=16000, tools=[LOOKUP_ORDER], messages=messages)
```

The response can also hold thinking and text blocks, so pick out the `tool_use` ones. The API enforces:

1. Append Claude's full `response.content` as the assistant turn.
2. The next user message must contain a `tool_result` for **every** `tool_use` id, or you get a 400. If Claude asks for two tools at once, send both results in **one** user message.
3. Keep sending the same `tools`.
4. `content` is a string (JSON works well) or a list of content blocks.

## When the tool fails

Don't crash or invent data. Return the error with a hint:

```python
{"type": "tool_result", "tool_use_id": block.id, "is_error": True,
 "content": "No order found with ID B-9999. Order IDs look like B-1001."}
```

## Controlling tool use

`tool_choice` can be `{"type": "auto"}` (the default) or `{"type": "none"}`. **Claude Opus 5.5 rejects forced tool use** (`any` or a named tool) with a 400. To get a specific tool, ask for it in the prompt and check in code that the call was made. If you only want JSON, use structured outputs.

## Claude's input is untrusted

Inputs come from a conversation a customer can type anything into. Validate in your tool, especially **authorization** ("does this order belong to the signed-in customer?"). Writes (credits, refunds) need limits and often human approval (lesson 7). Log every call.

> **Key takeaways**
> - Claude asks; your code runs the tool after validating input and permissions.
> - Good tools: specific names, descriptions that say when to call them, enums, strict schemas.
> - Answer every tool_use id in the next user message; use `is_error` for failures.
> - On Opus 5.5 `tool_choice` is auto or none only: ask in the prompt and verify the call.
