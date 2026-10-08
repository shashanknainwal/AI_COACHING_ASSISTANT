---
title: "Exercise: A CI Regression Gate"
type: exercise
minutes: 35
hints:
  - "`pass_rates`: build the category list from every row, but count `n` and `passes` from non-error rows only. A small helper that returns `{\"n\", \"passes\", \"rate\"}` keeps it short."
  - "`paired_flips`: make `cand = {r[\"id\"]: r[\"status\"] for r in candidate}`, then walk the baseline. Missing IDs go to `missing`. Only `pass -> fail` and `fail -> pass` count; anything involving `error` is skipped."
  - "`sign_test_p`: `n = regressions + fixes`; the answer is `sum(math.comb(n, k) for k in range(regressions, n + 1)) / 2 ** n`, rounded to 4 decimals. Return `1.0` when `n` is 0."
  - "`gate`: append reasons in the order of the rules table. For drops, loop over the baseline's `by_category` (already alphabetical), skip categories where either rate is `None`, and compare `round(b - c, 3) > max_category_drop`."
  - "Severity decides the outcome: `\"block\"` if any reason is a block, else `\"review\"` if any is a review, else `\"ship\"`. Compute `p_value` even when no paired reason is added."
---

Leo is back with Kestrel Mobile. "They want to ship v4 of the intent router: a rewritten prompt on a cheaper model. Their headline went from 80% to 87%, so the PR author says it's obviously better. Their golden set has grown to 40 cases, including sim-swap fraud. I don't want a human eyeballing every PR. Build the gate that runs in CI and returns a decision with reasons a reviewer can read in ten seconds."

In the style of an applied AI take-home, the spec below is exact, and the reviewers will check your output line by line.

`BASELINE_RUN` (v3) and `CANDIDATE_RUN` (v4) are loaded for you: one row per golden case, `{"id": "C-03", "category": "cancel", "status": "pass"}`, where `status` is `"pass"`, `"fail"` or `"error"`. `GATE_CONFIG` is in the editor.

## Background: compare case by case

Both runs used the same 40 cases, so you can pair them. Most cases give the same result in both. Only the cases that **flipped** carry information: **regressions** (pass to fail) and **fixes** (fail to pass).

If the new version were really no different, each flip would be equally likely to go either way, like a coin toss. The **sign test** asks: if flips were coin tosses, how likely is it to see at least this many regressions? With `r` regressions and `f` fixes, `n = r + f`:

```
p = sum over k from r to n of C(n, k)  /  2^n
```

Six regressions and no fixes gives `p = 1/64 = 0.0156`: unlikely to be chance. Two regressions and five fixes gives `p = 0.9375`: no evidence of a regression at all. A paired test like this can detect a change that comparing two overall rates with intervals would miss.

## Your task

**1. `pass_rates(rows)`** returns:

```python
{"total": 40, "errors": 1, "overall": {"n": 39, "passes": 34, "rate": 0.872},
 "by_category": {"billing": {"n": 10, "passes": 10, "rate": 1.0}, ...}}
```

Errors aren't scored. Categories come from all rows, in alphabetical order. `rate` is rounded to 3 decimals, or `None` when `n` is 0.

**2. `paired_flips(baseline, candidate)`** walks the baseline in order and returns `{"regressions": [...], "fixes": [...], "missing": [...]}`. An ID that isn't in the candidate goes to `missing`. A pair where either side is `"error"` is neither a regression nor a fix.

**3. `sign_test_p(regressions, fixes)`** returns the one-sided p-value above, rounded to 4 decimals, or `1.0` when there are no flips.

**4. `gate(baseline, candidate, config)`** returns `{"decision": ..., "reasons": [...], "p_value": ...}`. Each reason is `{"code", "severity", "detail"}`. Check the rules in this order, adding one reason per problem:

| # | Rule | Code | Severity | Detail format |
|---|---|---|---|---|
| 1 | Every baseline ID is in the candidate | `incomplete_run` | block | `"2 baseline cases missing from candidate: K-03, K-09"` |
| 2 | Candidate `errors / total` is at most `max_error_rate` | `error_rate` | block | `"candidate error rate 0.111 above 0.050"` |
| 3 | For each category in `category_floors`, alphabetically: the candidate has scored cases | `no_data` | block | `"zzz has no scored cases in the candidate run"` |
| 3 | ...and its candidate rate is at least the floor | `below_floor` | block | `"cancel pass rate 0.750 below floor 1.000"` |
| 4 | For each baseline category, alphabetically, where both rates exist: `round(baseline_rate - candidate_rate, 3)` is at most `max_category_drop` | `category_drop` | block if the candidate's `n` ≥ `min_category_n`, else review | `"roaming dropped 0.667 -> 0.333 (n=3)"` |
| 5 | If regressions outnumber fixes and `p < alpha` | `significant_regression` | block | `"6 regressions vs 0 fixes (sign test p=0.0156)"` |
| 5 | If regressions outnumber fixes and `p >= alpha` | `net_regression` | review | same format |

Rules 3 and 4 use the rounded rates from `pass_rates`. Format every rate and threshold with 3 decimals and the p-value with 4.

`decision` is `"block"` if any reason is a block, otherwise `"review"` if any reason is a review, otherwise `"ship"`. `p_value` is `sign_test_p(regressions, fixes)`, always included.

Why a "review" severity at all? A drop from 2 of 3 to 1 of 3 is one case. Blocking on it trains people to ignore the gate. Flagging it for a human keeps the gate trusted.

## Example

```python
>>> sign_test_p(4, 0)
0.0625
>>> gate(base, base, config)          # identical runs
{"decision": "ship", "reasons": [], "p_value": 1.0}
```

Press **Run** to see Kestrel's decision, then **Submit**. Then draft the one-paragraph PR comment you'd post for the author: what blocked it, what needs a human look, and what you'd do next.
