---
title: "Exercise: Profile a CRM Export"
type: exercise
minutes: 25
hints:
  - "`is_missing`: return True if the value is None, otherwise check `value.strip().lower() in MISSING_TOKENS`."
  - "In `infer_type`, first keep only the non-missing values (stripped). If none are left, return \"empty\"."
  - "`re.fullmatch(r\"-?\\d+\", v)` checks for an integer. For floats, `re.fullmatch(r\"-?\\d+(\\.\\d+)?\", v)` accepts both 12 and 12.5. Check int first, then float, then date."
  - "For dates, write a tiny helper that tries `datetime.strptime(v, \"%Y-%m-%d\")` and returns False if it raises `ValueError`."
  - "For the top value, count with `Counter`, then pick `min(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0]`: highest count first, then alphabetical."
  - "`duplicate_values`: count the stripped, non-missing values and return `sorted(v for v, n in counts.items() if n > 1)`."
---

Cobalt Supply sent their CRM export: 16 accounts (a sample of the full file). Before cleaning anything, you want a profile of every column, the same thing you'd do in your first hour on any engagement. Then you'll reuse this function on every dataset for the rest of your career.

## Your task

**1. `is_missing(value)`** returns `True` if the value is `None`, or if, after stripping whitespace and lowercasing, it's in `MISSING_TOKENS` (`""`, `"n/a"`, `"null"`, `"-"`, and so on).

**2. `infer_type(values)`** looks at the **non-missing** values (stripped) and returns:
- `"empty"` if there are none
- `"int"` if every value is a whole number like `42` or `-7` (no commas, no decimals)
- `"float"` if every value is a number with or without a decimal part, like `12` or `12.5`
- `"date"` if every value is an ISO date `YYYY-MM-DD` that `datetime.strptime` accepts
- `"text"` otherwise

Check in that order, so a column of whole numbers is `"int"`, not `"float"`.

**3. `profile_column(rows, column)`** returns:

```python
{
    "column": "industry",
    "missing": 3,          # count of missing values
    "missing_pct": 18.8,   # missing / total rows * 100, rounded to 1 decimal
    "distinct": 5,         # distinct non-missing values (after strip)
    "top": "Manufacturing",# most common non-missing value; ties -> alphabetical first; None if all missing
    "type": "text",        # infer_type of the column's values
}
```

**4. `profile(rows)`** returns a list with one `profile_column` result per column, in the order of the first row's keys. Return `[]` for no rows.

**5. `duplicate_values(rows, column)`** returns the sorted list of stripped, non-missing values that appear more than once. Use it to check whether the ID column is really unique.

Press **Run** to see the profile of Cobalt's export, then **Submit**.

> **Look at the output carefully.** The profile tells you which questions to send Cobalt today: why are some revenues missing or written with commas, and why does one account ID appear twice?
