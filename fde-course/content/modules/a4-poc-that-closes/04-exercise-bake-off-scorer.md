---
title: "Exercise: Score the Bake-Off"
type: exercise
minutes: 40
hints:
  - "`check_same_cases`: build `ids = [r[\"id\"] for r in records]`. Missing ids keep the eval-set order (`[c for c in case_ids if c not in set(ids)]`); unknown and duplicate ids are sorted lists. Only add a candidate to the result if one of the three lists is non-empty."
  - "`percentile`: sort, then `k = math.ceil(p / 100 * len(values))` and return `ordered[k - 1]` (use `max(1, k)` so p=0 doesn't index -1)."
  - "`score_candidate`: first keep only the first record for each id that's in `case_ids`. Cost, latency and the error check all use those kept records. `errors = len(case_ids) - len(scored)` counts errored and missing cases together."
  - "Cost per record is `(input_tokens * input_per_mtok + output_tokens * output_per_mtok) / 1_000_000`. Average over the kept records and round to 6 decimals."
  - "`pick_winner`: loop over `sorted(scores)` to build reasons. The leader is `min(eligible, key=lambda n: (-acc, cost, n))`. Tied: eligible names whose `ci[1] >= scores[leader][\"ci\"][0]`. Winner: `min(tied, key=lambda n: (cost, -acc, n))`."
---

Grace Liu, the Principal architect who coaches this track (a fictional character), has the bake-off results from Ellery Bank and a problem.

"Ellery's card-dispute team ran five candidates on the same 40 frozen cases: three Claude configurations, a cheaper zero-shot variant, and Quillon, their incumbent vendor, which their Head of Disputes likes a lot. Their analysts graded everything blind. Quillon's deck says 94% and their Head of Disputes has already forwarded it to the CIO. Before Monday I need the scores computed the way we agreed in the plan: accuracy with intervals, cost per task, p95 latency, errors and missing cases counted, hard constraints first, and our tie rule. If we lose, we lose fairly. If the 94% doesn't hold up, I want to be able to show exactly why, without a single unkind word about Quillon."

Ellery Bank, Quillon and everyone named here are fictional, and every result is invented for this exercise: they say nothing about how any real model or vendor performs. `EVAL_CASE_IDS` (40 ids), `RESULTS`, `PRICING` and `CONSTRAINTS` are loaded for you.

## The data

`RESULTS[name]` is a list of records, one per case the candidate returned:

```python
{"id": "D-01", "correct": True, "input_tokens": 2237, "output_tokens": 393, "latency_ms": 2663, "error": None}
```

`correct` was decided by blind graders. `error` is `None` or a string such as `"TimeoutError: no response after 30s"`. `PRICING[name]` has `input_per_mtok` and `output_per_mtok` in US dollars per million tokens. `CONSTRAINTS` holds `min_accuracy`, `max_cost_per_task`, `max_p95_ms` and `max_error_rate`.

## Your task

**1. `check_same_cases(case_ids, results)`** returns `{name: {"missing": [...], "unknown": [...], "duplicates": [...]}}` for every candidate with at least one coverage problem, and leaves clean candidates out. `missing` keeps the eval-set order; `unknown` (ids not in the set) and `duplicates` (ids that appear more than once) are sorted.

**2. `percentile(values, p)`** uses the nearest-rank method: sort the values and return the `ceil(p/100 * n)`-th smallest (1-based). Return `None` for an empty list. With 40 values, p95 is the 38th smallest.

**3. `wilson_interval(passes, n, z=1.96)`** returns `(low, high)` rounded to 3 decimals, or `(0.0, 1.0)` when `n` is 0:

```
p = passes / n;  denom = 1 + z²/n;  center = (p + z²/(2n)) / denom
half = z * sqrt(p(1-p)/n + z²/(4n²)) / denom;  (low, high) = (center - half, center + half)
```

**4. `score_candidate(records, pricing, case_ids)`** returns:

```python
{"n": 39, "passes": 34, "accuracy": 0.872, "ci": (0.733, 0.944), "errors": 1, "error_rate": 0.025,
 "cost_per_task": 0.007689, "p95_ms": 2755}
```

- Keep only the **first** record for each id that is in `case_ids`. Ignore duplicates and unknown ids.
- **Scored** records are the kept ones with `error` of `None`. `n` and `passes` count them, `accuracy` is `passes / n` rounded to 3 decimals (`None` if `n` is 0), and `ci` is `wilson_interval(passes, n)`.
- `errors` is `len(case_ids) - n`: errored **and missing** cases. `error_rate` is `errors / len(case_ids)`, rounded to 3 decimals.
- `cost_per_task` is the total dollar cost of the kept records divided by their count, rounded to 6 decimals. Errored calls are included: they still cost something.
- `p95_ms` is the nearest-rank p95 of the kept records' `latency_ms`, timeouts included. Users waited for them.

**5. `pick_winner(scores, constraints)`** takes `{name: score}` and returns:

```python
{"winner": "...", "leader": "...", "tied": [...], "disqualified": {name: [reasons]}}
```

- Go through candidates in name order. A candidate is **disqualified** with one reason per failed constraint, in this order and format (skip any constraint key that's absent):
  - `"no scored cases"` if its accuracy is `None` (always checked), otherwise `"accuracy 77.5% below 85.0%"` if accuracy is below `min_accuracy`
  - `"cost $0.0173 per task above $0.0100"` if cost is above `max_cost_per_task`
  - `"p95 latency 4701 ms above 3000 ms"` if p95 is above `max_p95_ms`
  - `"error rate 10.0% above 5.0%"` if the error rate is above `max_error_rate`
- The **leader** is the eligible candidate with the highest accuracy (ties: lower cost, then name).
- **Tied** candidates are the eligible ones whose interval's upper bound is at least the leader's lower bound, sorted by name. The leader is always tied with itself.
- The **winner** is the cheapest tied candidate (ties: higher accuracy, then name). That's the rule agreed in the plan: within noise, cost decides.
- With no eligible candidates, return `{"winner": None, "leader": None, "tied": [], "disqualified": {...}}`.

## Example

```python
>>> percentile([5, 1, 3], 50)
3
>>> wilson_interval(34, 40)
(0.709, 0.929)
```

34 of 40 is 85%, but the interval runs from about 71% to 93%. On this many cases, a candidate at 87% isn't measurably better.

Press **Run** to see the bake-off, then **Submit**. Before you move on, write Grace the two sentences she'll say on Monday about Quillon's 94%. Then write one sentence on what you'd recommend doing before Ellery commits to the winner. (Look at how wide the winner's interval is, and at what the tie rule assumed.)
