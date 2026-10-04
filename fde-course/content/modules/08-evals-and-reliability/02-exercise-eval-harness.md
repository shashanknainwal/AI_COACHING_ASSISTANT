---
title: "Exercise: Build an Eval Harness"
type: exercise
minutes: 35
hints:
  - "`grade`: if `actual is None`, every check is False. Otherwise compare `actual.get(\"category\")` and `actual.get(\"urgency\")` with the case."
  - "`run_eval`: wrap `triage(client, case[\"text\"])` in `try/except Exception as e` and store `f\"{type(e).__name__}: {e}\"` as the error."
  - "`summarize`: booleans add up like numbers, so `sum(values) / len(values)` gives a rate. Round with `round(x, 3)`."
  - "`by_category`: group rows by `row[\"expected\"][\"category\"]` with `setdefault(category, []).append(passed)`, then turn each list into a rate."
  - "`confusions`: skip rows where `actual` is None or the category was right; the key is `f\"{expected} -> {actual}\"`."
---

Brightway's ticket-triage system is about to go live. It sends every incoming ticket to the right queue with an urgency level. The VP of Support asks the question every FDE should expect: **"How do we know it works?"**

You'll build the harness that answers that question. You'll run the system over 20 labeled tickets (`brightway.EVAL_TICKETS`), grade each result, and produce a report someone can act on.

The system under test, `triage(client, text)`, is given. It returns `{"category": ..., "urgency": ...}` and, like any real API client, sometimes raises an error.

## Your task

**1. `grade(case, actual)`** returns `{"category": bool, "urgency": bool, "pass": bool}`. `pass` is true only when both match. If `actual` is `None` (the system failed), every check is `False`.

**2. `run_eval(client, cases)`** runs `triage` on every case, in order, and returns one row per case:

```python
{"id": "T-07",
 "expected": {"category": "damaged_item", "urgency": "high"},
 "actual": {"category": "damaged_item", "urgency": "normal"},   # None if triage raised
 "grades": {"category": True, "urgency": False, "pass": False},
 "error": None}                                                 # or "OverloadedError: ..." if triage raised
```

An exception in one case must **not** stop the eval: record `f"{type(e).__name__}: {e}"` and keep going.

**3. `summarize(rows)`** returns:

```python
{"n": 20, "pass_rate": 0.7, "category_accuracy": 0.8, "urgency_accuracy": 0.85, "errors": 1,
 "by_category": {"order_status": 1.0, ..., "account": 0.333}}
```

Rates are rounded to 3 decimals. `by_category` is the pass rate for each **expected** category.

**4. `confusions(rows)`** counts wrong categories as `{"account -> billing": 1, ...}` (expected → actual). Skip rows where the system errored.

Press **Run** to see the report, then **Submit**. Look at the failures: which one would you raise with the customer first?
