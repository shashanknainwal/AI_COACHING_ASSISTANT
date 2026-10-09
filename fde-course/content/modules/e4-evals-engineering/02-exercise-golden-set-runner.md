---
title: "Exercise: A Golden-Set Runner That Tells the Truth"
type: exercise
minutes: 40
hints:
  - "Wilson: `p = passes / n`, `denom = 1 + z*z/n`, `center = (p + z*z/(2*n)) / denom`, `half = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / denom`. Round `center - half` and `center + half` to 3 decimals."
  - "`cases_needed` is one line: `math.ceil(z * z * p * (1 - p) / (margin * margin))`."
  - "In `run_golden_set`, start each row as an error (`actual: None`, `status: \"error\"`), then use `try / except Exception as e / else`. Only grade in the `else` branch. A pass needs `isinstance(actual, str)` and `actual.strip().lower() == case[\"expected\"]`."
  - "In `summarize`, build `scored = [r for r in rows if r[\"status\"] != \"error\"]` once. Categories come from every row (`sorted({r[\"expected\"] for r in rows})`), but each category's n counts only its scored rows."
  - "In `traffic_report`, a category is tested when its scored n is above 0. Divide the weighted sum by the total traffic share of the tested categories. Sort gaps with `key=lambda c: (-traffic_mix[c], c)`."
---

Leo Martins, a Staff engineer on the applied team (a fictional coach for this track), drops a take-home on your desk. It's in the style of applied AI interviews: small, practical, and judged on whether your numbers can be trusted.

"Kestrel Mobile routes support messages to six queues with an LLM intent router. They have a 24-case golden set sampled from real traffic and labelled by their support leads. Their dashboard says 'accuracy: 75%' and nobody can tell me what that number means. Build me the runner I'd want: per-category rates with intervals, errors kept out of the score, and a view weighted by real traffic. Then tell me what the set can't tell us."

`GOLDEN_SET` (24 cases), `TRAFFIC_MIX` (share of last month's traffic per intent) and `kestrel_router(text)`, the system under test, are loaded for you. Treat the router as a black box. Like any production call, it can raise.

## Your task

**1. `wilson_interval(passes, n, z=1.96)`** returns the Wilson score interval as `(low, high)`, each rounded to 3 decimals:

```
p      = passes / n
denom  = 1 + z²/n
center = (p + z²/(2n)) / denom
half   = z * sqrt(p(1-p)/n + z²/(4n²)) / denom
(low, high) = (center - half, center + half)
```

With `n == 0`, return `(0.0, 1.0)`: no data, no information.

**2. `cases_needed(margin, p=0.5, z=1.96)`** returns the smallest whole `n` for which the normal-approximation margin `z * sqrt(p(1-p)/n)` is at most `margin`. That's `ceil(z² p(1-p) / margin²)`. This is the number you quote when someone asks "how many cases do we need?"

**3. `run_golden_set(cases, system)`** calls `system(case["text"])` for every case, in order, and returns one row per case:

```python
{"id": "K-02", "expected": "billing", "actual": "Billing ", "status": "pass", "error": None}
```

- `status` is `"pass"` when the output is a string that equals `expected` after `.strip().lower()`; otherwise `"fail"`. `actual` keeps the raw output.
- If the call raises, `actual` is `None`, `status` is `"error"` and `error` is `f"{type(e).__name__}: {e}"`. Keep going.

**4. `summarize(rows, min_n=5)`** returns:

```python
{"n": 23, "passes": 18, "pass_rate": 0.783, "ci": (0.581, 0.903), "errors": 1,
 "by_category": {
     "billing": {"n": 6, "passes": 5, "pass_rate": 0.833, "ci": (0.436, 0.97), "low_n": False},
     ...}}
```

- **Errors are not scored.** `n` counts only `pass` and `fail` rows, and `errors` counts the rest.
- `by_category` groups by `expected`, with keys in alphabetical order, and includes a category even if all its rows errored.
- `pass_rate` is rounded to 3 decimals, or `None` when `n` is 0. `ci` is `wilson_interval(passes, n)`. `low_n` is `n < min_n`.

**5. `traffic_report(summary, traffic_mix, min_n=5)`** returns:

```python
{"weighted_pass_rate": 0.781, "gaps": ["device_support", "plan_change", ...], "untested_share": 0.03}
```

- A traffic category is **tested** if it appears in `summary["by_category"]` with `n > 0`. `weighted_pass_rate` is `sum(share * pass_rate)` over tested categories, divided by the sum of their shares, rounded to 3 decimals (`None` if nothing is tested). Use the rounded `pass_rate` values from the summary.
- `gaps` lists every category in `traffic_mix` with fewer than `min_n` scored cases (including ones with none), sorted by traffic share, highest first, then by name.
- `untested_share` is the total traffic share of categories with no scored cases, rounded to 3 decimals.

## Example

```python
>>> wilson_interval(9, 10)
(0.596, 0.982)
>>> cases_needed(0.05)
385
```

Nine out of ten sounds like 90%. The interval says the true rate could be anywhere from about 60% to 98%.

Press **Run** to see Kestrel's report, then **Submit**. Before you move on, write down your answer to Leo: which two categories would you add cases to first, and why? (Hint: compare `low_n` with `TRAFFIC_MIX`, and remember that one category has no cases at all.)
