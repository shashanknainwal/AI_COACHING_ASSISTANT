---
title: "Exercise: A Release Gate for Prompt Changes"
type: exercise
minutes: 30
hints:
  - "Wilson: `p = passes / n`, `denom = 1 + z*z/n`, `center = (p + z*z/(2*n)) / denom`, `half = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / denom`. Return `(round(center - half, 3), round(center + half, 3))`."
  - "`diff_runs`: build `before = {r[\"id\"]: r[\"pass\"] for r in baseline}`, then walk the candidate rows, skipping IDs not in `before`."
  - "`gate`: check the three rules in order (must-pass, pass rate, critical regressions), appending a reason string for each problem. `ship` is `not reasons`."
  - "Pass rate in the reason uses three decimals: `f\"pass rate dropped from {before:.3f} to {after:.3f}\"`."
  - "`consistency`: a case counts toward pass@k if `any(trials)`, toward pass^k if `all(trials)`, and is flaky if it's in the first group but not the second."
---

Someone on the team rewrote the triage prompt. The new version scores **15/20** against the current **14/20**, and they want to ship it today. Your job is to build the release gate that decides, automatically, on every change.

Given: `BASELINE` and `CANDIDATE` eval results (one row per ticket: `{"id", "category", "pass"}`), `MUST_PASS` case IDs, `CRITICAL_CATEGORIES`, and `AGENT_TRIALS` (five repeated runs of each agent case).

## Your task

**1. `wilson_interval(passes, n, z=1.96)`** returns the 95% Wilson score interval for a pass rate, as `(low, high)` rounded to 3 decimals (formula in the lesson). With `n == 0`, return `(0.0, 1.0)`.

**2. `diff_runs(baseline, candidate)`** returns `{"regressions": [...], "fixes": [...]}`: IDs that passed in the baseline and fail in the candidate, and the reverse. Keep candidate order and ignore IDs missing from the baseline.

**3. `gate(baseline, candidate, must_pass, critical, tolerance=0.02)`** returns `{"ship": bool, "reasons": [...]}`. Check these rules in this order and add one reason per problem:

| Rule | Reason text |
|---|---|
| Every `must_pass` ID passes in the candidate (a missing ID counts as failed) | `"must-pass case T-07 failed"` |
| Candidate pass rate ≥ baseline pass rate − `tolerance` | `"pass rate dropped from 0.750 to 0.250"` |
| No regression in a `critical` category | `"regression in critical category damaged_item: T-05"` |

`ship` is true only when there are no reasons.

**4. `consistency(trials)`** takes `{case_id: [bool, ...]}` and returns:
- `pass_at_k`: the share of cases that passed **at least once**.
- `pass_all_k`: the share that passed **every** time (often written pass^k).
- `flaky`: IDs that passed sometimes but not always.

Round shares to 3 decimals.

Press **Run** and compare the two intervals: is 15/20 really better than 14/20? Then **Submit**.
