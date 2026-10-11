---
title: "Exercise: Flaky or Regression? A Rerun Policy"
type: exercise
minutes: 35
hints:
  - "`rerun_policy`: one pass over `regressions + fixes`. Add a case only if its `2 * k` calls still fit in the budget; otherwise it goes to `skipped` (and keep checking the rest, so the order stays simple and predictable)."
  - "`classify`: check regression and fix before flaky. A case that went from 5 of 5 to 1 of 5 has a fractional rate on one side, but it's a regression, not noise."
  - "`observations`: the first-run status comes first, then the reruns for that version, then drop errors. A case with no reruns has a single observation."
  - "`paired_difference`: for each case, candidate mean minus baseline mean. Then take the plain mean and sample standard deviation of those differences, and use `t95(n - 1)`."
  - "`verdict`: classify only the cases you reran, using the rerun trials alone. Use every observation (first run plus reruns) for the paired difference."
---

Teodora Kessler at Gannet Home Energy (fictional) is reviewing a model and prompt upgrade. "The CI gate you'd recognise from module E4 said 'review' for five categories. Each lost exactly one case, and the gate won't block on fewer than two regressions per category. Good: we don't block on noise. But somebody still has to decide. Our rule is to rerun the flipped cases five times on both versions. Turn that rule into code that tells me which flips were real."

`BASELINE_RUN` and `CANDIDATE_RUN` (one run of 40 cases each), `RERUNS` (five more trials of each flipped case on both versions), `CONFIG`, `paired_flips()` (from E4/05) and `t95(df)` are loaded for you.

## Background: what a rerun can and can't tell you

A single run of a model-backed system is one draw. When a case flips between versions, there are three stories: the candidate really broke it, the case is flaky on both, or the first run was a fluke. Five trials per version usually separates them. A case that passes 5 of 5 on the baseline and 1 of 5 on the candidate is a regression. A case that passes 3 of 5 and 2 of 5 is flaky, and its flip says nothing about the change.

Two statistical traps come with reruns. First, the extra trials are **not** extra cases. Module E4 made that point; here you measure it. Trials of one case are correlated, so the standard error must be clustered by case, and its square over the naive SE (the **design effect**) shows how much precision the naive formula invents. Second, rerunning only the flipped cases piles observations onto them. A rate pooled over all observations over-weights those cases. Compare versions per case: average each case's trials first, then compare the case averages in pairs.

## Your task

**1. `rerun_policy(flips, k, max_calls)`**: walk `flips["regressions"]` then `flips["fixes"]`. Each case costs `2 * k` calls. Add it to `rerun` if it fits the remaining budget, otherwise to `skipped`. Return `{"rerun", "calls", "skipped"}`.

**2. `case_rate(statuses)`** returns `(passes, n)` with `"error"` left out.

**3. `classify(base_statuses, cand_statuses)`**, from the two pass rates `b` and `c`:

| Condition (in order) | Class |
|---|---|
| either side has no scored trials | `"unknown"` |
| `b >= 0.8` and `c <= 0.4` | `"regression"` |
| `b <= 0.4` and `c >= 0.8` | `"fix"` |
| `0 < b < 1` or `0 < c < 1` | `"flaky"` |
| otherwise | `"stable"` |

**4. `observations(first_run, reruns, version)`** returns `{case_id: [1 or 0, ...]}`: the case's first-run status followed by `reruns[case_id][version]` if present, errors dropped.

**5. `clustered_rate(obs)`** returns `{"rate", "n_obs", "n_cases", "se_naive", "se_clustered", "design_effect"}`, skipping empty cases. Use the clustered formula from lesson 02. Round the rate to 3, the SEs to 4 and the design effect `(se_clustered / se_naive)^2` to 2.

**6. `paired_difference(base_obs, cand_obs)`**: over cases with scored observations in both, `d = mean(candidate) - mean(baseline)`. Return `{"n", "diff", "se", "low", "high"}`, where `se` is the sample SD of `d` over `sqrt(n)` and the bounds are `diff ± t95(n - 1) * se`. Round `se` to 4 and the rest to 3.

**7. `verdict(baseline, candidate, reruns, config)`**: find the flips, plan the reruns, classify each rerun case on its rerun trials, and compute the paired difference over all observations. Reasons, in this order:

| Rule | Code | Severity | Detail |
|---|---|---|---|
| Each confirmed regression, in rerun order | `critical_regression` if its category is in `critical_categories`, else `regression` | block / review | `"VUL-05 (vulnerable): baseline 5/5, candidate 0/4 on rerun"` |
| Paired difference `high < 0` | `worse_overall` | block | `"mean per-case change -0.080 (95% CI -0.140 to -0.020)"` |
| Regressions skipped by the budget | `not_rerun` | review | `"regressions not rerun within budget: TAR-04, VUL-05"` |

Return `{"decision", "reasons", "confirmed_regressions", "confirmed_fixes", "flaky", "calls", "difference"}`, with the decision derived from the severities as before.

## Example

```python
>>> classify(["pass"] * 5, ["fail", "fail", "fail", "error", "fail"])
'regression'
```

Press **Run**, then **Submit**.

## What to notice

- **The average says nothing happened, and the candidate is still blocked.** The mean per-case change is -1.3 points with an interval from -10.7 to +8.2. Meanwhile one vulnerable-customer case went from 5 of 5 to 0 of 4. Averages hide concentrated harm, which is why critical categories get case-level rules.
- **Three of the five "regressions" weren't.** Two are flaky on both versions, and one passed every rerun. Quarantine flaky cases into their own report line and fix or replace them. Don't let them block, and don't let them silently pass either.
- **The design effect is about 2.7.** Pooling 79 observations as if they were independent makes the standard error look 40% smaller than it is. The pooled rate is also skewed toward the eight rerun cases. Report per-case numbers.
- **The budget is a policy decision.** Rerunning every flip costs 80 calls here. With a smaller budget, regressions go first because they can block; the ones you couldn't rerun stay as review items, never as silent passes.
