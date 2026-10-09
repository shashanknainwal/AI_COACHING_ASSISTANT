---
title: "Structured Outputs: Turning Messy Notes into Data with Claude"
type: reading
minutes: 6
---

> **By the end of this lesson you will be able to:**
> - Explain why "please return JSON" isn't good enough for production
> - Use structured outputs (`output_config` with a JSON Schema) in the Python SDK
> - Design a schema that reduces made-up answers and handle the stop reasons that break parsing

After three calls with Marisol Grant's claims team at Lumen, you have pages of notes and a promise to send a requirements list by Friday. Claude can draft it, if its output is a shape your code can rely on every time.

## Three ways to get JSON

1. **Ask in the prompt.** Works most of the time, so your pipeline crashes at 2 a.m. on the response that starts "Here's the JSON you asked for:".
2. **Structured outputs.** You pass a **JSON Schema** and the response is constrained to match it. The right default for extraction.
3. **Strict tool use.** A tool schema with `strict: true`, for when Claude should decide whether to call something (Module 7).

## Structured outputs in the Python SDK

```python
import json
import anthropic

client = anthropic.Anthropic()

schema = {
    "type": "object",
    "properties": {
        "customer": {"type": "string"},
        "pain_points": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["customer", "pain_points"],
    "additionalProperties": False,
}

response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=4096,
    system="Extract information from discovery notes. Only use facts stated in the notes.",
    messages=[{"role": "user", "content": notes}],
    output_config={"format": {"type": "json_schema", "schema": schema}},
)

text = next(b.text for b in response.content if b.type == "text")
data = json.loads(text)
print(data["pain_points"])
```

- **`additionalProperties: False` is required on every object.** The real API and the course simulator reject schemas without it.
- **List every field in `required`.** For a field that may be unknown, allow null: `{"type": ["string", "null"]}`, so Claude can say "not stated" instead of inventing.
- **Find the text block by type**, not `content[0]`.

> **Real SDK shortcut:** define a Pydantic model and call `client.messages.parse(..., output_format=MyModel)`, then read `response.parsed_output`. This course uses the raw schema so you see what's sent.

## Schemas that resist hallucination

| Pattern | Example | Why |
|---|---|---|
| Enums | `"priority": {"type": "string", "enum": ["must", "should", "could"]}` | No "High-ish" |
| Evidence field | `"evidence"`: a short quote from the source | Forces grounding; fast human check |
| Nullable unknowns | `"deadline": {"type": ["string", "null"]}` | Honest "not stated" |
| `open_questions` | A list for ambiguities | Surfaced, not guessed |

Pair it with a clear system prompt:

```text
You extract software requirements from customer discovery notes.
- Only include requirements the notes state or clearly imply. Never invent.
- For each requirement, quote the shortest phrase from the notes that supports it as evidence.
- Use "must" only for things the customer called essential or blocking.
- Put anything ambiguous or contradictory in open_questions instead of guessing.
```

## Check `stop_reason` before parsing

| `stop_reason` | You get | Do |
|---|---|---|
| `"end_turn"` | Complete, schema-valid JSON | Parse it |
| `"max_tokens"` | JSON cut off mid-way; won't parse | Raise a clear error; retry with higher `max_tokens` or split the input |
| `"refusal"` | No usable answer | Raise a clear error; don't parse |

Give extraction calls generous `max_tokens` (4,096 or more).

## Validate after parsing

Valid JSON isn't correct data. Remove exact-title duplicates, sort musts first, and check every item has evidence. The result is a first draft: you review it and the customer confirms it.

> **Key takeaways**
> - Use `output_config.format` with a JSON Schema whenever code consumes Claude's output.
> - `additionalProperties: False` on every object; list required fields; null for unknown.
> - Check `stop_reason`, then validate, dedupe and have a human review.
