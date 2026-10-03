---
title: "Structured Outputs: Turning Messy Notes into Data with Claude"
type: reading
minutes: 16
---

> **By the end of this lesson you will be able to:**
> - Explain why "please return JSON" in a prompt isn't good enough for production
> - Use structured outputs (`output_config` with a JSON Schema) in the Anthropic Python SDK
> - Design an extraction schema that reduces made-up answers
> - Handle the stop reasons that can still break your parsing

## Why FDEs extract structure constantly

After discovery you have call notes, emails, recap docs, and Slack threads. You need a **requirements list**: typed, prioritized, and traceable back to what the customer actually said. Later in the engagement you'll do the same thing at scale for the customer's own documents: invoices, claims, referrals, contracts.

Claude is excellent at reading messy text. The engineering challenge is getting its output into a shape your code can rely on 100% of the time.

## Three ways to get JSON, from worst to best

**1. Ask nicely in the prompt.** "Respond only with JSON in this format…" works most of the time. "Most of the time" means your pipeline crashes at 2 a.m. on the one response that starts with "Here's the JSON you asked for:" or misses a field.

**2. Structured outputs.** You give the API a **JSON Schema**, and the response is constrained to match it. The text you get back is valid JSON with exactly the fields you defined. This is the right default for extraction.

**3. Strict tool use.** You define a tool with a schema and `strict: true`. Same guarantee, used when Claude should *decide* whether and when to call something. You'll learn this in Module 7.

## Structured outputs in the Python SDK

You pass the schema in `output_config.format`:

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

Things to notice:

- **`additionalProperties: False` is required on every object** in the schema. It tells the API that no extra keys are allowed. The real API (and the course simulator) rejects schemas without it.
- **Every field you need goes in `required`.** For a field that may legitimately be unknown, allow `null`: `{"type": ["string", "null"]}`. That gives Claude an honest way to say "not stated" instead of inventing something.
- **Find the text block by type.** Same rule as Module 1: don't assume `content[0]`.

> **Pydantic shortcut (real SDK):** with the real `anthropic` package you can also define a Pydantic model and call `client.messages.parse(..., output_format=MyModel)`, then read `response.parsed_output`. It's the same feature with automatic validation into Python objects. In this course we use the raw schema so you can see exactly what's sent.

## Designing a schema that resists hallucination

A schema shapes behavior, not just format. These patterns make extractions more trustworthy:

| Pattern | Example | Why it helps |
|---|---|---|
| **Enums for categories** | `"priority": {"type": "string", "enum": ["must", "should", "could"]}` | No free-text variants like "High-ish" |
| **An evidence field** | `"evidence": {"type": "string"}` holding a short quote from the source | Forces grounding, and lets a human verify each item in seconds |
| **Nullable unknowns** | `"deadline": {"type": ["string", "null"]}` | Gives an honest "not stated" option |
| **A place for uncertainty** | `"open_questions": [...]` | Ambiguities get surfaced instead of guessed |
| **Flat and small** | A few fields per item | Easier to review and evaluate |

Pair the schema with a clear system prompt:

```text
You extract software requirements from customer discovery notes.
- Only include requirements the notes state or clearly imply. Never invent.
- For each requirement, quote the shortest phrase from the notes that supports it as evidence.
- Use "must" only for things the customer called essential or blocking.
- Put anything ambiguous or contradictory in open_questions instead of guessing.
```

## What can still go wrong

Structured outputs guarantee the *shape* of complete responses. They can't help in these cases, so check `stop_reason` before parsing:

| `stop_reason` | What you get | What to do |
|---|---|---|
| `"end_turn"` | Complete, schema-valid JSON | Parse it |
| `"max_tokens"` | JSON cut off mid-way, which won't parse | Raise a clear error; retry with a higher `max_tokens` or split the input |
| `"refusal"` | No usable answer | Raise a clear error; don't try to parse |

A long call transcript can easily produce a large requirements list, so give extraction calls generous `max_tokens` (4,096 or more).

## Validation after parsing

Valid JSON isn't the same as *correct* data. After parsing, apply cheap business rules in code:

- **Deduplicate:** the same requirement often appears twice in different words. Exact-title duplicates are easy to remove in code.
- **Sort for humans:** musts first.
- **Sanity checks:** does every requirement have non-empty evidence? Are there suspiciously many "must"s?

And keep a human in the loop. An LLM-extracted requirements list is a **first draft** that saves you an hour. You still review it, and the customer still confirms it.

## The workflow you'll build

```
discovery notes ──► Claude + JSON Schema ──► stop_reason check ──► json.loads
                                                                      │
                     requirements doc ◄── prioritize + dedupe ◄──────┘
```

In the next exercise you'll write the schema, the API call, the error handling, and the prioritization step, then test them against the course's simulated Claude.

> **Key takeaways**
> - Use structured outputs (`output_config.format` with a JSON Schema) whenever code consumes Claude's output.
> - Every object needs `additionalProperties: False`; required fields must be listed; use `null` for "unknown."
> - Enums, evidence quotes, and an `open_questions` field make extractions more trustworthy.
> - Check `stop_reason` before parsing, then validate, dedupe, and have a human review.
