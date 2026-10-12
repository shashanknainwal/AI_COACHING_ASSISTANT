---
title: "Exercise: A Warranty-Claim Extractor That Checks Its Own Output"
type: exercise
minutes: 40
hints:
  - "`build_system_prompt` has no inputs. Assemble it from the given constants as a list of lines and join once at the end; the blank entries between sections are what produce the empty lines in the expected layout."
  - "`RMA_SCHEMA`: a nullable string is an `anyOf` of two types. Derive both enums from the same constants the prompt uses, so a new SKU can never appear in one and not the other."
  - "`validate_rma`: order matters. A badly formatted serial should not also be reported as missing from the email, so only run the grounding check when the format check passed. 'Appears in the email' means subject or body; the evidence quote is checked against the body only."
  - "`extract_rma`: current models can return a thinking block before the text, so don't assume the text is at a fixed index. Decide what to do from `stop_reason` before you try to parse anything."
  - "The two retry kinds differ in what you change. A validation failure needs the conversation extended (the whole previous turn, then the correction). A truncation needs the same conversation with more room. Keep `messages` and `max_tokens` as variables your loop can update."
---

Leo hands you a practice take-home, written in the style of a take-home case study. "The customer is Halden Robotics, a made-up maker of desktop robot arms. Their returns team reads every warranty email by hand and types the details into their RMA system. They want Claude to fill in those fields. Most candidates hand in a prompt, a schema and a `json.loads`. That gets you through the demo, but it falls over on real email. I want an extractor that **knows when its own output is wrong**: it checks what the schema can't, gives Claude one chance to fix it, and sends the rest to a human. When I review this, I read the prompt, the schema and the failure handling, in that order."

The catalog (`PRODUCTS`), the failure modes, the actions, `CONTEXT`, `RULES`, `MODEL`, `MAX_TOKENS`, `PROMPT_VERSION`, the serial format and five sample `EMAILS` are given.

## Your task

**1. `build_system_prompt()`** returns (lines joined with `"\n"`):

```
<CONTEXT>

<product_catalog>
- HR-ARM-2: six-axis desktop robot arm
- ...one line per product...
</product_catalog>

<failure_modes>
- no_power: the unit doesn't turn on at all
- ...one line per failure mode...
</failure_modes>

<rules>
<RULES, unchanged>
</rules>
```

It takes no input, so it's identical on every call. That's what makes it cacheable. Identical bytes are only the precondition: in production you'd also send the system prompt as a block with `cache_control` (Lesson 1). This exercise leaves the marker out so the tests can compare a plain string.

**2. `build_user_message(email)`** returns:

```
<email>
<subject>Arm is dead</subject>
<body>
Hi, my HR-ARM-2 (serial HX-204611) won't power on ...
</body>
</email>

Extract the warranty-claim fields from the email above.
```

**3. `RMA_SCHEMA`**: all six fields required, `additionalProperties: False`.

| Field | Type |
|---|---|
| `serial_number` | string **or null** (`anyOf`) |
| `sku` | enum: the catalog SKUs, then `"unknown"` |
| `failure_mode` | enum: the `FAILURE_MODES` names |
| `safety_issue` | boolean |
| `requested_action` | enum: `ACTIONS` |
| `evidence` | string |

**4. `validate_rma(data, email)`** returns a list of error strings, in this order:

| Check | Error text |
|---|---|
| A non-null serial must fully match `SERIAL_FORMAT` | `serial_number '204611' is not a valid serial (expected HX- followed by 6 digits)` |
| Otherwise, a non-null serial must appear in the subject or body | `serial_number 'HX-999999' does not appear in the email` |
| `evidence` must be non-blank and appear exactly in the body | `evidence is not an exact quote from the email body` |

(Build the serial messages with `{serial!r}`.) These are the checks a schema can't express: is the value *grounded* in the input?

**5. `correction_message(errors)`** returns `"Your previous answer failed validation:"`, then one `"- <error>"` line per error, then `"Return the corrected fields for the same email."`, joined with `"\n"`.

**6. `extract_rma(client, email)`** calls `MODEL` with `max_tokens=MAX_TOKENS`, `system=build_system_prompt()`, one user message, and `output_config={"format": {"type": "json_schema", "schema": RMA_SCHEMA}}`. It makes **at most two attempts** and returns:

```python
{"id": "M-104", "status": "ok", "data": {...}, "errors": [], "attempts": 2, "prompt_version": "rma-extract@v1"}
```

| What came back | What you do |
|---|---|
| `stop_reason == "refusal"` | Stop. `status` `"needs_review"`, `data` None, `errors` `["refused"]` |
| `stop_reason == "max_tokens"` | Errors `["output was cut off at max_tokens"]`, data None. Retry with the **same messages** and `max_tokens=2 * MAX_TOKENS` |
| Valid JSON that passes `validate_rma` | `status` `"ok"` |
| Validation errors | Retry: append `response.content` as an assistant turn, then a user turn with `correction_message(errors)` |

If the second attempt still fails, return `"needs_review"` with the last `data` (it helps the reviewer) and the last errors.

Press **Run** to process the five emails. M-104 contains an injection attempt and gets an invented serial on the first try; M-105 never produces a real quote. Then **Submit**.

## Why it's built this way

- **Retry once, with the errors.** Showing Claude exactly what failed fixes most grounding mistakes in one turn. A second blind retry mostly costs money. After one retry, a human is cheaper than a loop.
- **Don't retry refusals with the same request.** You'd get the same answer and pay for it again.
- **A truncated answer gets more room, not feedback.** There's nothing useful to show back.
- **Append `response.content`, not just the text.** Current models return thinking blocks, and passing the whole turn back unchanged is the safe default when you continue a conversation.

In an interview debrief, expect: "What's your human-review rate on real traffic, and what would you change if it were 15%?" Have a number in mind and a first thing to look at (the errors, grouped by type).
