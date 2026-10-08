---
title: "Structured Outputs and Validation in Depth"
type: reading
minutes: 20
---

> **By the end of this lesson** you'll be able to say exactly what structured outputs guarantee and what they don't, design an extraction schema that resists made-up values, handle every stop reason that can break your parser, choose between `output_config.format`, strict tools and `messages.parse()`, and measure extraction quality field by field.

## How this comes up in an interview

Extraction is a common first workload for an LLM integration, so it's a natural vehicle for coding and design questions. The fundamentals version is "how do you get reliable JSON out of a model?" The senior version is "your extractor returns valid JSON 100% of the time and the customer still says it's wrong 6% of the time. Walk me through it."

The answer that separates people: **valid is not the same as correct.** The API can guarantee the first. Only your validation and your evals can tell you about the second.

## What the guarantee actually covers

Think of extraction quality in layers. Each layer has an owner.

| Layer | Example failure | Who catches it |
|---|---|---|
| Syntax | Trailing text after the JSON, a missing brace | The API, with `output_config.format` |
| Shape | Missing field, extra field, a value outside the enum | The API, with `output_config.format` |
| Constraints the API doesn't enforce | A negative quantity, a 900-character "summary" | Your code (or the SDK's client-side validation) |
| Grounding | A well-formed serial number that isn't in the email | Your code |
| Business rules | A refund requested on a product that's out of warranty | Your code |
| Truth | The right field filled with the wrong one of two dates in the email | Your evals |

Two exceptions break even the first two layers. A **refusal** (`stop_reason: "refusal"`) may not match your schema at all, and on current models the content can be empty. A **truncated** answer (`stop_reason: "max_tokens"`) is cut off mid-JSON. Check `stop_reason` before you parse, every time.

## Three ways to ask for structure

```python
# Illustrative: output_config.format with a raw JSON schema
response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=4096,
    system=SYSTEM_PROMPT,
    messages=[{"role": "user", "content": user_message}],
    output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
)
```

| Mechanism | Use it when | Notes |
|---|---|---|
| `output_config.format` | The answer itself is the data | The default for extraction and classification. Text block contains JSON matching the schema. |
| Strict tool (`"strict": True` on the tool) | The model should decide whether and when to call something, and the arguments must match | Guarantees the shape of `tool_use.input`. On Claude Opus 5.5 and Sonnet 5.5, forcing a call with `tool_choice` `any` or `tool` returns a 400, so a fake tool is no longer a way to get JSON. |
| `client.messages.parse(..., output_format=MyModel)` | You're in Python or TypeScript and want a typed object back | Takes a Pydantic model and validates the response. The SDK also removes schema constraints the API doesn't support and checks them client-side. |

You can combine tools and `output_config.format` in one request: tools during the turn, a structured final answer at the end. The older top-level `output_format` parameter on `messages.create()` is deprecated in favour of `output_config.format`.

## What a schema can and can't say

Structured outputs support a subset of JSON Schema. Knowing the edges saves you from a schema that's silently weaker than you think.

| Supported | Not supported |
|---|---|
| object, array, string, integer, number, boolean, null | Recursive schemas |
| `enum`, `const`, `anyOf`, `allOf`, `$ref` / `$defs` | Numeric limits: `minimum`, `maximum`, `multipleOf` |
| String formats such as `date`, `date-time`, `email`, `uri`, `uuid` | String length limits: `minLength`, `maxLength` |
| `additionalProperties: false` (required on every object) | Complex array constraints; `additionalProperties` set to anything but `false` |

So "quantity must be between 1 and 50" is a rule for your validator (or for `parse()`'s client-side check), not something the API enforces on raw `create()` calls.

Two operational facts interviewers like: a **new schema costs extra latency on its first request** while it compiles, and the compiled schema is then cached for 24 hours. And structured outputs are **incompatible with citations and with assistant prefill** (both return a 400), but work with batches, streaming and thinking.

## Designing a schema that resists made-up values

Most hallucinated fields come from a schema that leaves the model no honest way to say "I don't know".

1. **Give every enum an escape hatch.** `"unknown"` for a SKU, `"other"` for a category, `"unclear"` for an action. Without it, an ambiguous input is forced into a real value, and that wrong value looks exactly like a right one.
2. **Make unknowns nullable, not optional.** Keep every field in `required` and allow `null` through `anyOf: [{"type": "string"}, {"type": "null"}]`. "The model said null" and "the field is missing because of a bug" are different situations, and you want to tell them apart.
3. **Use enums for anything code will branch on.** Free text is for humans to read. If code routes on it, it's an enum.
4. **Ask for evidence you can check.** A short exact quote from the input per key decision lets you verify grounding with a substring check. It's also what an auditor actually wants.
5. **Don't ask for the model's reasoning in the output.** A `reasoning` field that pushes the model to reproduce its internal thinking in the response can be declined on Claude Opus 5.5 and Sonnet 5.5 (refusal category `reasoning_extraction`). A short explanation of the answer, or an evidence quote, is fine. If you need to see how the model thought, read summarized thinking blocks and log them separately.
6. **One decision per field.** `"status": "damaged_needs_refund"` hides two decisions in one string, and you can't score them separately.
7. **Keep it flat and small.** Every field is something to test. Ten fields you check beat thirty you don't.
8. **Generate the schema from the same lists as the prompt.** The catalog that feeds the prompt also feeds the enum. Then they can't drift apart.

## Reading the response safely

```python
# Illustrative: the order of checks
if response.stop_reason == "refusal":
    return needs_review("refused")            # don't retry the same request
if response.stop_reason == "max_tokens":
    return retry_with_more_room()             # the JSON is incomplete
text = next(b.text for b in response.content if b.type == "text")
data = json.loads(text)                       # json.loads, never a regex
errors = validate(data, source_text)          # constraints, grounding, business rules
```

- **Branch on `stop_reason`, not on `stop_details`.** `stop_details` describes a refusal (category, explanation) but is informational and can be `None`.
- **Find the text block by type.** Current models put a thinking block before the text, so `response.content[0].text` breaks.
- **Never extract JSON with a regex.** A regex fails on nested braces, braces inside strings, escaped quotes and different (equally valid) escaping of the same characters. With `output_config.format` the whole text block is the JSON. Parse it with `json.loads` and let a real failure raise.

## Validation and retry policy

| Failure | Retry? | How |
|---|---|---|
| Refusal | No (not with the same request) | Route to review; consider a fallback model if the category allows it |
| `max_tokens` | Once | Same messages, larger `max_tokens` |
| Grounding or constraint error | Once | Append the assistant turn and a user turn listing the exact errors |
| Still invalid after one retry | No | Human review, with the last answer attached |
| 429, 5xx, connection errors | Yes | The SDK retries these with backoff (2 retries by default) |

Track the **review rate** (share of inputs that end in human review) and the **retry rate** as production metrics. A retry rate that creeps up after a model or prompt change is an early warning.

## Measuring extraction quality

"Accuracy" on an extractor hides the information you need. Measure **per field**:

- **Normalize before comparing.** `"Acme Corp "` and `"acme corp"` are the same vendor; `1200` and `1200.00` the same total. Decide the normalization rules once, in code, and keep them in the repo.
- **Report each field's accuracy separately.** A prompt change that lifts `vendor` from 80% to 95% and drops `currency` from 100% to 90% can still raise the average. The average hides a new bug.
- **Treat null as a value.** Expected null and got a value is a made-up field. Expected a value and got null is a miss. They have different costs, so look at both.
- **Mark critical fields.** A wrong amount or currency moves money; a wrong ticket title doesn't. Any regression on a critical field blocks the release, whatever the average does.
- **Compare versions case by case.** The useful output of a prompt change is the list of (case, field) pairs that went from right to wrong.

You'll build exactly this in the next exercise. The FDE track's lesson "Release Gates, Noise and Nondeterminism" covers confidence intervals and pass@k if you want the statistics behind release gates.

## Practice (say it out loud)

Original prompts in the style of an applied AI fundamentals or design round:

1. "Structured outputs guarantee valid JSON. Why does your extractor still need a validator? Give three concrete checks."
2. "A customer's schema has a free-text `category` field and their dashboard shows 214 distinct categories. What happened, and how do you fix it without losing information?"
3. "Your model fills `invoice_date` with the due date about 4% of the time. Schema, prompt or eval: where do you start, and why?"
4. "Walk me through everything that can come back from `messages.create` when you asked for structured output, and what your code does with each."

> **Key takeaways**
>
> - Structured outputs guarantee syntax and shape. Constraints, grounding, business rules and truth are yours to check.
> - Check `stop_reason` first: a refusal or a `max_tokens` cut-off can break the schema.
> - Use `output_config.format` for answers, strict tools for actions, and `messages.parse()` for typed objects. Forced tool choice is a 400 on Claude Opus 5.5.
> - Give enums an escape hatch, make unknowns nullable, ask for checkable evidence, and don't ask for the model's reasoning in the output.
> - Parse with `json.loads`, never a regex. Retry once with the errors, then hand off to a human.
> - Measure extraction per field, with normalization, null handling and critical fields.
