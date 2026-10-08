---
title: "Exercise: A Field-Level Prompt Regression Suite"
type: exercise
minutes: 35
hints:
  - "`normalize`: return None first. For `total`, `round(float(str(value).replace(\",\", \"\")), 2)`. For `currency`, `str(value).strip().upper()`. Everything else: `\" \".join(str(value).split()).casefold()`."
  - "`run_suite`: wrap the call in `try/except anthropic.APIError as e` and store `type(e).__name__`. Check `stop_reason` for `\"refusal\"` and `\"max_tokens\"` before parsing; the JSON is in the text block, not `content[0]`."
  - "`field_accuracy`: `True` counts as 1, so `sum(r[\"scores\"][f] for r in rows) / len(rows)` is a rate. A row counts toward `all_fields` when `all(r[\"scores\"].values())`."
  - "`compare`: build `before = {r[\"id\"]: r[\"scores\"] for r in old_rows}`, then walk `new_rows` (skip IDs not in `before`) and `FIELDS` in order, adding `f\"{id}:{field}\"` to regressions (True to False) or fixes (False to True)."
  - "`compare` reasons: first one line per field in `FIELDS` whose delta is below `-tolerance` (`f\"{field} accuracy dropped from {old:.3f} to {new:.3f}\"`), then one line per regression whose field is in `critical`."
---

Leo forwards you a pull request from a teammate on a fictional engagement with Tallis Freight, whose accounts-payable team uses Claude to extract fields from supplier invoices. The PR rewrites the extraction prompt (`PROMPT_V1` to `PROMPT_V2`). The description says: "Accuracy up from 50% to 70% on the golden set. Ship it?"

"That number is the share of invoices with *every* field right," Leo says. "It's a fine headline and a terrible release gate. Totals and currencies feed the payment run. Build the suite that scores each field, diffs the two versions case by case, and blocks the release if a field that moves money got worse. Then tell me whether this PR ships."

Given: `FIELDS`, `CRITICAL_FIELDS`, `INVOICE_SCHEMA`, both prompts, and `GOLDEN` (10 labelled invoices: `{"id", "text", "expected"}`).

## Your task

**1. `normalize(field, value)`** returns the comparable form of a value:

| Field | Rule | Example |
|---|---|---|
| any, value is None | `None` | `None` |
| `total` | number rounded to 2 decimals; strings may contain commas | `"1,200.00"` → `1200.0` |
| `currency` | stripped and upper-case | `" gbp"` → `"GBP"` |
| everything else | whitespace collapsed to single spaces, then `casefold()` | `" Sorrel   &  Pike"` → `"sorrel & pike"` |

**2. `score_case(expected, actual)`** returns `{field: bool}` for every field in `FIELDS`: true when the normalized values are equal (so expected null and got null is correct). If `actual` is None, every field is False.

**3. `invoice_message(text)`** returns `"<invoice>\n" + text + "\n</invoice>\n\nExtract the invoice fields."`.

**4. `run_suite(client, system_prompt, cases)`** calls `MODEL` once per case (any `max_tokens` ≥ 1024, `system=system_prompt`, one user message, `output_config` with `INVOICE_SCHEMA`) and returns one row per case, in order:

```python
{"id": "G-02", "actual": {...}, "scores": {"vendor": False, "invoice_number": True, ...}, "error": None}
```

A failure scores that case as all-wrong and the suite keeps going: `"refused"` for a refusal, `"max_tokens"` for a truncated answer, or the exception's class name (`"OverloadedError"`) for an `anthropic.APIError`. `actual` is None for failed cases.

**5. `field_accuracy(rows)`** returns each field's accuracy plus `"all_fields"` (the share of rows with every field right), rounded to 3 decimals. With no rows, every value is `0.0`.

**6. `compare(old_rows, new_rows, critical=CRITICAL_FIELDS, tolerance=0.02)`** returns:

```python
{"deltas": {"vendor": 0.3, ..., "all_fields": 0.2},      # new minus old, rounded to 3 decimals
 "regressions": ["G-05:due_date", ...],                  # right before, wrong now
 "fixes": ["G-02:vendor", ...],                          # wrong before, right now
 "verdict": "block",                                     # "ship" only when there are no reasons
 "reasons": ["currency accuracy dropped from 1.000 to 0.800", "critical field currency regressed on G-06", ...]}
```

List regressions and fixes in `new_rows` order, then `FIELDS` order, and skip IDs that aren't in `old_rows`. The reasons come in two groups, in this order:

1. Each field in `FIELDS` whose delta is below `-tolerance`: `"<field> accuracy dropped from <old> to <new>"`, with 3 decimals.
2. Each regression on a field in `critical`: `"critical field <field> regressed on <id>"`. These block the release **even when the field's average stays within tolerance**.

Press **Run** to compare the two prompts, then **Submit**.

## What to notice

- The headline went up 20 points, and the PR still shouldn't ship. The new rule "If no currency code is printed, use USD" turned `€` and `£` invoices into dollars.
- `due_date` accuracy didn't move (0.9 to 0.9), yet one case broke: a fix and a regression cancelled out. Only the case-level diff shows it, and the broken case is a made-up due date, which is exactly the kind of value the prompt said never to invent.
- The fix isn't to throw away v2. Keep the vendor rules, drop the two "helpful" defaults, and run the suite again. One change at a time.

In a debrief, be ready for: "Ten invoices is tiny. How big should the golden set be, and where would you get it?" A good answer draws from real traffic, oversamples the hard cases (symbols instead of codes, missing fields, foreign number formats), and grows the set with every production bug.
