---
title: "Release Gates, Noise and Nondeterminism"
type: reading
minutes: 3
---

> **By the end of this lesson you will be able to:**
> - Tell a real improvement from noise with confidence intervals
> - Design a release gate that blocks regressions an average would hide
> - Measure consistency with pass@k and pass^k

A teammate tells Jordan the new prompt scores 15/20 against the current 14/20, so it should ship. Three problems: with 20 cases one case is 5 points (**noise**); it fixed three tickets and broke two, one a damaged-item report Jordan cares about (**hidden regression**); and re-running changes some outputs (**nondeterminism**). A **release gate** answers "can this ship?" with rules agreed in advance.

## Confidence intervals

Use the **Wilson score interval** for pass rates. It behaves well for small samples and rates near 0% or 100%.

```
p      = passes / n,   z = 1.96 (95%)
denom  = 1 + z²/n
center = (p + z²/(2n)) / denom
half   = z × √(p(1−p)/n + z²/(4n²)) / denom
interval = (center − half, center + half)
```

14/20 gives about 48%-86%; 15/20 about 53%-89%. The intervals overlap almost completely: **20 cases can't tell these prompts apart.** On 1,000 cases the intervals would be about 6 points wide. To detect a 5-point change you need hundreds of cases. Compare **case by case** (regressions vs fixes), which is more sensitive than two averages, and read the changed cases.

## Designing the gate

| Rule | Why |
|---|---|
| **Must-pass cases** | Safety complaints, fraud reports, past incidents: one failure blocks |
| **No drop beyond a tolerance** | Allows noise (say 2 points), blocks real declines |
| **No regressions in critical slices** | A better average can hide a worse fraud slice |
| **Hard limits** | Zero policy violations; latency and cost budgets |

Agree the rules with the customer **before** results are in. Run the gate in CI on every change to prompts, models, tools or retrieval, model upgrades included.

## pass@k and pass^k

Outputs vary between runs, and agents vary more. Run important cases k times:

- **pass@k:** share of cases that passed **at least once**. Fits best-of-k or retry setups.
- **pass^k:** share that passed **every** time. This matters for automation: an agent right 4 times in 5 fails one customer in five.

A big gap means **flakiness**. Flaky cases sit on a decision boundary, usually an ambiguous instruction or missing rule. Reduce variance with clearer instructions and examples, structured outputs, simpler steps, decisions moved into code, and tighter tools.

## From offline evals to production

- **Shadow mode:** run the new version on live traffic without showing its output.
- **Canary:** send a small share (say 5%) to the new version first.
- **Online signals:** escalations, thumbs-down, agent overrides, refusals, errors, latency, cost.
- **Sample and grade** a daily slice of production outputs.
- **Feed failures back** as eval cases. Module 9 covers the logging behind this.

> **Key takeaways**
> - Small sets can't separate close scores; use Wilson intervals and case-by-case comparison.
> - Gates combine must-pass cases, a tolerance, critical-slice rules and hard limits, agreed in advance.
> - pass@k for best-of-k, pass^k for automation; read flaky cases.
> - Shadow, canary, online signals and sampled grading close the loop.
