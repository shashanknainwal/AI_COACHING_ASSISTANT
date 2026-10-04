---
title: "Exercise: Extract Requirements from Call Notes with Claude"
type: exercise
minutes: 30
hints:
  - "Each requirement item is an object schema with properties `title`, `type`, `priority`, `evidence`. Use `\"enum\": [...]` for type and priority, list all four in `required`, and set `\"additionalProperties\": False`."
  - "The top-level schema is an object with two array properties: `requirements` (items = your requirement object) and `open_questions` (items = `{\"type\": \"string\"}`)."
  - "Pass `output_config={\"format\": {\"type\": \"json_schema\", \"schema\": REQUIREMENTS_SCHEMA}}` to `client.messages.create`."
  - "Check `response.stop_reason` before parsing: raise `ValueError(\"truncated\")` for `\"max_tokens\"` and `ValueError(\"refused\")` for `\"refusal\"`."
  - "Get the JSON text with `next(b.text for b in response.content if b.type == \"text\")`, then `json.loads` it."
  - "For `prioritized`, `sorted(items, key=lambda r: PRIORITY_ORDER.index(r[\"priority\"]))` is stable, so items with the same priority keep their order. Track seen titles with `title.strip().lower()` in a set."
---

You've just finished three discovery calls at **Lumen Insurance**. Your notes are long and messy. Before Friday you need a typed, prioritized requirements list with evidence for each item, so you can review it with Marcus (the champion) and get it confirmed.

You'll build the extraction pipeline from the last lesson, using Claude with structured outputs.

## Your task

**1. `REQUIREMENTS_SCHEMA`**: a JSON Schema for this shape:

```python
{
    "requirements": [
        {
            "title": "Auto-fill policy number from claim emails",
            "type": "functional",     # one of REQUIREMENT_TYPES
            "priority": "must",       # one of PRIORITY_ORDER
            "evidence": "policy number was off by one digit"
        },
        ...
    ],
    "open_questions": ["Which ClaimsPro version is in production?", ...]
}
```

Rules: every object has `"additionalProperties": False` and lists all its properties in `"required"`. `type` and `priority` must use `"enum"` with the values in `REQUIREMENT_TYPES` and `PRIORITY_ORDER`.

**2. `extract_requirements(client, notes)`**:
- Call `client.messages.create` with `model=MODEL`, `max_tokens` of **at least 4096**, `system=SYSTEM_PROMPT`, one user message containing the notes, and `output_config` set to use your schema.
- If `stop_reason` is `"max_tokens"`, raise `ValueError("truncated")`. If it's `"refusal"`, raise `ValueError("refused")`.
- Otherwise find the text block, parse it with `json.loads`, and return the resulting dictionary.

**3. `prioritized(result)`** takes the parsed dictionary and returns a list of requirement **titles**:
- Ordered must → should → could. Requirements with the same priority keep their original order.
- Drop duplicates: if two requirements have the same title ignoring case and surrounding spaces, keep only the first one (the first one after sorting).

The `SYSTEM_PROMPT` is written for you, using the guidance from the lesson. Read it; good prompts are part of the deliverable.

Press **Run** to extract requirements from the sample notes, then **Submit**.

> **In a real engagement:** send the prioritized list to your champion with the evidence quotes and the open questions. Asking "Did we get this right?" turns a draft into an agreed scope.
