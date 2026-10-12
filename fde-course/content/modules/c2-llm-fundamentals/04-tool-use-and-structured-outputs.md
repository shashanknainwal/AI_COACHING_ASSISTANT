---
title: Tool Use and Structured Outputs
type: reading
minutes: 28
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

### Never edit the history

Notice that the loop appends `response.content` exactly as it came back, thinking blocks included, and never changes an earlier message. That's deliberate.

- **Pass thinking blocks back unmodified.** On current models a response can start with one or more `thinking` blocks. Read content by block `type`, not by position, and send the blocks back exactly as received.
- **Text between tool calls may arrive as thinking.** On Claude Opus 5.5, text the model writes between tool calls comes back inside `thinking` blocks rather than `text` blocks. If your UI showed that narration, look for it there.
- **Preserved thinking.** On Opus 5.5, Sonnet 5.5, Haiku 5.5 and Fable 5.1, each thinking block's signature is bound to the system prompt, the tools and every earlier message. Edit or trim an earlier turn and the replayed block no longer matches. For accounts created on or after 2026-08-31, that request returns a **400** by default. Older accounts aren't enforced by default, but Anthropic's guidance is to build append-only regardless.

So the rule is **append-only history**. When a conversation gets too long, use compaction (summarise and start a fresh context) or the API's server-side context editing, rather than snipping old turns yourself. Append-only is also what keeps the prompt cache hitting (Lesson 6), so one habit serves both.

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

Original prompts in the style of a fundamentals round. Answer out loud, then check.

**1.** "Walk me through, message by message, what goes over the wire when a user asks a support agent for a refund and the agent needs two tools."

<details>
<summary>Model answer and self-check</summary>

"Say the tools are `lookup_order` and `issue_refund`.

1. **Request 1:** my code sends the system prompt, both tool definitions, and the user message 'I want a refund for order ORD-10293.'
2. **Response 1:** `stop_reason: "tool_use"`, possibly a thinking block, and a `tool_use` block for `lookup_order` with an `id` and `input: {order_id: "ORD-10293"}`. The model runs nothing.
3. **My code** runs the lookup, checking the user is allowed to see that order.
4. **Request 2:** the same system prompt and tools, the original user message, the assistant's response appended unchanged, then a user message with one `tool_result` whose `tool_use_id` matches.
5. **Response 2:** the model asks for `issue_refund`. Because it moves money, my code checks policy and may require human approval before running it. If it fails, I return a `tool_result` with `is_error: true` and a clear message.
6. **Request 3:** history plus that result. **Response 3:** `stop_reason: "end_turn"` and the text reply to the user.

Every request resends the full history, so three round trips means the order data is billed as input twice. I'd keep tool outputs small and the prefix cached."

Score yourself:
- [ ] Said clearly that your code runs the tools, not the model.
- [ ] Matched each `tool_result` to its `tool_use_id` and appended the assistant turn unchanged.
- [ ] Put a permission or approval check on the risky tool.
- [ ] Mentioned error handling (`is_error`) and that history is resent each time.

</details>

**2.** "Your agent sometimes passes `order_id: 10293` instead of `"ORD-10293"`. What do you change?"

<details>
<summary>Model answer and self-check</summary>

"Layers, cheapest first. The property description gets a format example: 'Order ID including the ORD- prefix, for example ORD-10293.' The schema gets `type: string` and a `pattern` for the format, and the tool gets `strict: true` so the arguments always match the schema's types. Strict mode guarantees shape, not meaning, so the tool code still validates. If the ID is wrong, it returns `is_error: true` with an actionable message such as 'Order IDs look like ORD-10293', and the model can retry. Then I add the failing cases to the eval set so I can see the error rate drop and stay down."

Score yourself:
- [ ] Improved the description with a concrete format example.
- [ ] Tightened the schema (string type, pattern) and used `strict: true`.
- [ ] Kept validation in the tool and returned a helpful error.
- [ ] Added the case to an eval.

</details>

> **Key takeaways**
>
> - The model never runs tools. It returns `stop_reason: "tool_use"`, your code runs the tool, and you send back a `tool_result` with the matching `tool_use_id`. Loop until `end_turn`.
> - Return all parallel results in one message, and return errors with `is_error` instead of dropping them.
> - Keep history append-only and pass thinking blocks back unmodified. On Opus 5.5 and the other current models, editing earlier turns invalidates thinking signatures (a 400 for newer accounts) and breaks the cache.
> - Tool descriptions are prompts: say when to call the tool, describe every field, use enums.
> - `strict: true` guarantees the argument shape; `output_config.format` guarantees a JSON answer. Neither guarantees the content is correct.
