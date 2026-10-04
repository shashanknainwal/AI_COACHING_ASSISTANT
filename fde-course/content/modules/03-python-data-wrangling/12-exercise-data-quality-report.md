---
title: "Exercise: Build a Data-Quality Report"
type: exercise
minutes: 30
hints:
  - "Start `evaluate_rule` by pulling the column's values: `values = [r.get(rule[\"column\"]) for r in rows]`."
  - "For `required`, every row is checked and missing values fail. For `unique`, every row is checked; count non-missing stripped values with `Counter` and fail rows whose value appears more than once."
  - "For `regex`, `numeric` and `allowed`, only check present values: `present = [v.strip() for v in values if not is_missing(v)]`."
  - "Use `re.fullmatch(rule[\"pattern\"], v)` for regex and `re.fullmatch(r\"-?\\d+(\\.\\d+)?\", v)` for numeric."
  - "`pass_rate = round((checked - failed) / checked * 100, 1)` when `checked > 0`, else `100.0`."
  - "Sort results with `key=lambda r: (r[\"pass_rate\"], r[\"name\"])`. Format the pass rate with `f\"{rate:.1f}%\"`."
---

Cobalt's data owner asked for a single document: "Tell me what's wrong with our CRM data, worst first, so I can assign fixes." You'll build a small rules engine and a Markdown report generator, then run it on a CRM sample.

## Your task

**1. `evaluate_rule(rows, rule)`** returns `{"name", "checked", "failed", "pass_rate"}` for one rule. The rule's `"check"` decides what's checked:

| check | Rows checked | A row fails when… |
|---|---|---|
| `"required"` | all rows | the value is missing (`is_missing`) |
| `"unique"` | all rows | its non-missing stripped value appears more than once in the column (missing values don't fail) |
| `"regex"` | rows with a value | the stripped value doesn't `re.fullmatch` `rule["pattern"]` |
| `"numeric"` | rows with a value | the stripped value isn't a plain number like `12` or `-3.5` |
| `"allowed"` | rows with a value | the stripped value isn't in `rule["values"]` |

`pass_rate` is the percentage of checked rows that passed, rounded to 1 decimal, or `100.0` if nothing was checked.

**2. `severity(pass_rate)`** returns `"critical"` below 90, `"warning"` below 98, and `"ok"` otherwise.

**3. `dq_report(rows, rules, title)`** returns a Markdown string, exactly in this format:

```
# Cobalt CRM data quality
16 rows checked against 6 rules.

| Rule | Checked | Failed | Pass rate | Severity |
|---|---|---|---|---|
| email format | 13 | 3 | 76.9% | critical |
| email present | 16 | 3 | 81.2% | critical |
| account id unique | 16 | 2 | 87.5% | critical |
| revenue numeric | 13 | 1 | 92.3% | warning |
| owner present | 16 | 1 | 93.8% | warning |
| industry allowed | 15 | 0 | 100.0% | ok |

Critical: 3, warnings: 2, ok: 1
```

That's the real report for Cobalt's sample, so you can compare your output line by line. Lines are joined with `"\n"`, with one blank line before the table and one before the summary line. Pass rates always show one decimal and a `%`.

Press **Run** to generate Cobalt's report, then **Submit**.

> **What you'd do next:** paste this into an email, add 3 example failing values and a suggested owner under each critical rule, and offer to re-run it every Monday.
