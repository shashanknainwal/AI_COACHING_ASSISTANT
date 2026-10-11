---
title: "Exercise: A CI Regression Gate"
type: exercise
minutes: 35
hints:
  - "`pass_rates`: errors are counted but never scored. A category whose rows all errored still appears, with a rate of `None`."
  - "`paired_flips`: look the candidate up by id. Only a clean pass-to-fail or fail-to-pass is a flip; a pair involving an error tells you nothing about quality."
  - "`sign_test_p`: under 'no real change', each flip is a fair coin. You want the probability of at least this many regressions out of all flips. The standard library has a function for binomial coefficients."
  - "`gate`: work through the rules table in order and append reasons as you go. For category drops you need the number of regressions *in that category*, so you'll need to know which category each flipped case belongs to."
  - "The decision is derived from the reasons' severities, never decided separately. Return the p-value even when no paired reason was added."
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
| 4 | For each baseline category, alphabetically, where both rates exist: `round(baseline_rate - candidate_rate, 3)` is at most `max_category_drop` | `category_drop` | block only if the candidate's `n` ≥ `min_category_n` **and** the category has at least `min_category_flips` regressions; else review | `"roaming dropped 0.667 -> 0.333 (n=3, regressions=1)"` |
| 5 | If regressions outnumber fixes and `p < alpha` | `significant_regression` | block | `"6 regressions vs 0 fixes (sign test p=0.0156)"` |
| 5 | If regressions outnumber fixes and `p >= alpha` | `net_regression` | review | same format |

Rules 3 and 4 use the rounded rates from `pass_rates`. Format every rate and threshold with 3 decimals and the p-value with 4.

`decision` is `"block"` if any reason is a block, otherwise `"review"` if any reason is a review, otherwise `"ship"`. `p_value` is `sign_test_p(regressions, fixes)`, always included.

Why a "review" severity, and why a minimum flip count? A drop from 2 of 3 to 1 of 3 is one case. So is 5 of 5 to 4 of 5, which is a 0.2 drop and would clear any sensible size threshold. Blocking on a single flipped case trains people to ignore the gate. Flagging it for a human keeps the gate trusted, and on a real model that human's first move is to rerun the case and see whether it flips back.

There's a second reason. Kestrel has eight categories, and each one gets its own threshold check on every PR. The more categories you test, the more likely it is that one crosses the line by chance alone: the **multiple-comparisons problem**. With twenty categories, a check that is wrong 5% of the time per category fires on most runs even when nothing changed. The minimum flip count and the review severity are cheap guards. The rigorous version is a per-category paired test (the same sign test, per category) at a corrected threshold such as `alpha / number_of_categories` (Bonferroni). The overall sign test in rule 5 doesn't have this problem, because it is one test.

## Example

```python
>>> sign_test_p(4, 0)
0.0625
>>> gate(base, base, config)          # identical runs
{"decision": "ship", "reasons": [], "p_value": 1.0}
```

Press **Run** to see Kestrel's decision, then **Submit**. Then draft the one-paragraph PR comment you'd post for the author: what blocked it, what needs a human look, and what you'd do next.
