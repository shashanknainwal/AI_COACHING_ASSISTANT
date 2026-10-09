---
title: Tool Use and Structured Outputs
type: reading
minutes: 22
---

> **By the end of this lesson** you'll be able to walk through the tool-use loop step by step, design a tool schema an interviewer would accept, and explain when to use strict tools versus structured outputs.

## How this comes up in an interview

"Walk me through what happens when the model calls a tool" is a classic fundamentals question, and it often opens a design round about agents. Anthropic's applied AI job postings name agents among the core skills (Official, from the postings), so expect to explain the mechanics, not just name them.

The trap is vagueness. "The model calls the API" is wrong: the model never runs anything itself. Your code does. This lesson gives you the exact sequence. Code snippets are **illustrative**: they show the request shapes from the Anthropic Python SDK documentation, trimmed for reading.

## The tool loop, step by step

1. **You send a request with `tools`.** Each tool has a `name`, a `description` and an `input_schema` (JSON Schema).
2. **The model decides.** If it wants a tool, the response has `stop_reason: "tool_use"` and one or more `tool_use` content blocks. Each block has an `id`, the tool `name` and the `input` arguments.
3. **Your code runs the tool.** You look up the function by name, validate the input, and execute it. This is where permissions, timeouts and approval gates live.
4. **You send the result back.** Append the assistant's full response to the conversation, then a `user` message containing a `tool_result` block for each call, with the matching `tool_use_id`.
5. **Repeat** until `stop_reason` is `"end_turn"`. Then read the final text.

```python
# Illustrative: a manual tool loop (Anthropic Python SDK shapes)
messages = [{"role": "user", "content": "What's the weather in Paris?"}]

while True:
    response = client.messages.create(
        model="claude-opus-5-5",
        max_tokens=16000,
        tools=tools,
        messages=messages,
    )
    if response.stop_reason != "tool_use":
        break

    messages.append({"role": "assistant", "content": response.content})
    results = []
    for block in response.content:
        if block.type == "tool_use":
            output = run_tool(block.name, block.input)   # your code
            results.append({
                "type": "tool_result",
                "tool_use_id": block.id,                 # must match the call
                "content": output,
            })
    messages.append({"role": "user", "content": results})
```

A production loop also handles the other stop reasons: `max_tokens` (the answer was cut off), `refusal` (the model declined; check `stop_details`) and `pause_turn` (a server-side tool paused a long turn and you re-send to continue). The SDK also has a beta **tool runner** that drives this loop for you; knowing the manual loop is what lets you explain it.

### Details interviewers listen for

- **Parallel calls.** One response can contain several `tool_use` blocks. Run them (concurrently if you like) and return **all** the results in **one** user message. Splitting them across messages teaches the model to stop calling tools in parallel.
- **Errors are results.** If a tool fails, return a `tool_result` with `"is_error": True` and a useful message ("Location 'xyz' not found. Use a city name."). Don't drop the call; the model can recover if it knows what went wrong.
- **History is resent.** Each loop iteration resends the whole conversation, tool results included. Big tool outputs inflate every later request. That's a cost question waiting to happen (Lesson 1).
- **Forcing a tool call.** On Claude Opus 5.5 and Sonnet 5.5, `tool_choice` set to `any` or a specific tool returns a 400. Use the default `auto`, tell the model in the prompt which tool to use, and check that a `tool_use` block actually came back.

## Designing a tool schema

A tool definition is a prompt. The model reads the name and description to decide when to call it.

```python
# Illustrative tool definition
{
    "name": "lookup_order",
    "description": (
        "Look up one order by its ID. Call this whenever the user mentions an "
        "order number or asks about delivery status, refunds or items in an order."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "order_id": {"type": "string", "description": "Order ID, e.g. ORD-10293"},
            "include": {
                "type": "string",
                "enum": ["status", "items", "refund"],
                "description": "Which part of the order to return",
            },
        },
        "required": ["order_id"],
    },
}
```

What a good answer covers:

- **Clear names** that say what the tool does: `lookup_order`, not `tool2`.
- **Descriptions that say *when* to call it,** not only what it does. Trigger conditions in the description measurably help recent models decide to call a tool.
- **A description on every property,** with a format example.
- **Enums for fixed sets.** The model can't invent a value that isn't listed.
- **Only truly required fields in `required`.**
- **Narrow tools over god tools.** `lookup_order` and `issue_refund` are easier to permission, log and evaluate than one `database_query` tool. Put risky actions (refunds, emails, writes) behind a separate tool you can gate with human approval.

## Strict tools

Add `"strict": True` to a tool definition (next to `name` and `input_schema`) and the model's `input` is guaranteed to validate against the schema. The schema must set `"additionalProperties": False` and list `required` fields.

```python
# Illustrative: strict tool
{
    "name": "book_flight",
    "description": "Book a flight to a destination",
    "strict": True,
    "input_schema": {
        "type": "object",
        "properties": {
            "destination": {"type": "string"},
            "date": {"type": "string", "format": "date"},
            "passengers": {"type": "integer", "enum": [1, 2, 3, 4, 5, 6, 7, 8]},
        },
        "required": ["destination", "date", "passengers"],
        "additionalProperties": False,
    },
}
```

Strict mode guarantees the **shape** of the arguments. It does not guarantee they're **right**: a valid date can still be the wrong date. Your tool code still checks business rules.

## Structured outputs

When you don't need a tool at all, just a JSON answer, use **structured outputs**: `output_config.format` with a JSON schema. The response's text is valid JSON that matches the schema.

```python
# Illustrative: structured output with a raw JSON schema
response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=16000,
    messages=[{"role": "user", "content": "Extract: John Smith (john@example.com) wants the Enterprise plan."}],
    output_config={
        "format": {
            "type": "json_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "plan": {"type": "string"},
                },
                "required": ["name", "email", "plan"],
                "additionalProperties": False,
            },
        }
    },
)
text = next(b.text for b in response.content if b.type == "text")
data = json.loads(text)
```

The Python SDK also has `client.messages.parse(...)`, which takes a Pydantic model and returns a validated object. The older top-level `output_format` parameter on `messages.create()` is deprecated in favour of `output_config.format`.

## Which one when?

| You need... | Use |
|---|---|
| The model to fetch data or take an action, then keep going | Tools (the loop above) |
| Tool arguments that always match the schema | Tools with `strict: True` |
| A final answer in a fixed JSON shape, no action | Structured outputs (`output_config.format`) |
| Both: tools during the turn, then a JSON final answer | Both together in one request |
| JSON on a model that rejects prefill and forced tool choice | Structured outputs, not a "fake tool" or a `{` prefill |

## Practice (say it out loud)

Original prompts in the style of a fundamentals round:

- "Walk me through, message by message, what goes over the wire when a user asks a support agent for a refund and the agent needs two tools."
- "Your agent sometimes passes `order_id: 10293` instead of `"ORD-10293"`. What do you change?" (Hint: description with a format example, a pattern in the schema, strict mode, and validation in the tool.)

> **Key takeaways**
>
> - The model never runs tools. It returns `stop_reason: "tool_use"`, your code runs the tool, and you send back a `tool_result` with the matching `tool_use_id`. Loop until `end_turn`.
> - Return all parallel results in one message, and return errors with `is_error` instead of dropping them.
> - Tool descriptions are prompts: say when to call the tool, describe every field, use enums.
> - `strict: true` guarantees the argument shape; `output_config.format` guarantees a JSON answer. Neither guarantees the content is correct.
