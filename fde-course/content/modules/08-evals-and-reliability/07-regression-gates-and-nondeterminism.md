---
title: "Release Gates, Noise and Nondeterminism"
type: reading
minutes: 17
---

> **By the end of this lesson you will be able to:**
> - Tell a real improvement from noise using confidence intervals
> - Design a release gate that blocks regressions a higher average would hide
> - Measure consistency across repeated runs with pass@k and pass^k
> - Connect offline evals to monitoring in production

## "The new prompt scores higher, ship it"

A teammate's new prompt scores 15/20; the current one scores 14/20. Is it better? Three problems:

1. **Noise.** With 20 cases, one case is 5 points. The difference could easily come from chance.
2. **Hidden regressions.** The new prompt fixed three tickets and broke two. One it broke is a damaged-item report, a slice the customer cares about most.
3. **Nondeterminism.** Run the same eval twice and some outputs change. One run is one sample.

A **release gate** is code that answers "can this ship?" with rules everyone agreed on in advance, on every change. It replaces arguments with criteria.

## Confidence intervals: is it real?

A pass rate from n cases is an estimate. A **confidence interval** gives the range the true rate plausibly lies in. For pass rates, use the **Wilson score interval**. It behaves well for small samples and for rates near 0% or 100%, where the simple textbook formula breaks.

```
p      = passes / n,   z = 1.96 (95%)
denom  = 1 + z²/n
center = (p + z²/(2n)) / denom
half   = z × √(p(1−p)/n + z²/(4n²)) / denom
interval = (center − half, center + half)
```

For 14/20 that's about 48%-86%; for 15/20, about 53%-89%. The intervals overlap almost completely, so **20 cases can't tell these two prompts apart.** The same rates on 1,000 cases would give intervals about 6 points wide.

Practical rules:

- **Size the set for the decisions you need.** To detect a 5-point change, you need hundreds of cases, not dozens.
- **Compare on the same cases.** Paired comparisons (case by case: regressions vs fixes) are more sensitive than comparing two averages.
- **Read the changed cases.** Two regressions you understand are more informative than a 1-point change in the average.

## Designing the gate

Average scores hide what matters. Good gates combine several rules:

| Rule | Why |
|---|---|
| **Must-pass cases** | Some cases are non-negotiable: a safety complaint, a fraud report, a known past incident. One failure blocks. |
| **No drop beyond a tolerance** | Allows noise-sized wiggles (say 2 points) but blocks real declines. |
| **No regressions in critical slices** | A better average can hide a worse fraud slice. |
| **Hard limits** | Zero policy violations (credit above limits, invented citations), latency and cost budgets. |

Agree on the rules with the customer **before** the results are in. Rules written after seeing the numbers tend to say whatever lets the favored change ship.

Run the gate in CI on every pull request that touches prompts, models, tools or retrieval, and post the report (headline, intervals, regressions and fixes) on the pull request. A model upgrade is a change too: run the gate before switching.

## Nondeterminism: pass@k and pass^k

Even with the same input, model outputs vary between runs, and agents vary more because small differences compound over steps. So run important cases several times (k trials) and measure:

- **pass@k:** the share of cases that passed **at least once** in k trials. Useful when a person picks the best of several attempts, or when you retry.
- **pass^k** (pass all k): the share that passed **every** time. This is what matters for customer-facing automation: a support agent that handles a request correctly 4 times out of 5 fails one customer in five.

A big gap between the two means the system is **flaky**. Flaky cases are often the most valuable to read: they sit on a decision boundary, which usually points to an ambiguous instruction or a missing rule.

Ways to reduce variance: clearer instructions and examples, structured outputs, splitting a step into simpler steps, moving decisions from the model into code, and (for agents) tighter tools.

## Offline evals and production monitoring

Offline evals run before release on a fixed set. Production brings inputs your set doesn't have. Close the loop:

- **Shadow mode:** run the new version on live traffic without showing its output, and compare with the current version.
- **Canary release:** send a small share of traffic (say 5%) to the new version and watch metrics before rolling out.
- **Online signals:** escalation rate, customer thumbs-down, agent overrides, refusals, errors, latency and cost per request.
- **Sample and grade:** have a judge (or a person) grade a daily sample of production outputs.
- **Feed failures back:** every production failure becomes an eval case, so it can never silently come back.

Module 9 covers the logging and observability that make this possible.

> **Key takeaways**
> - Small eval sets can't distinguish close scores; use Wilson intervals and paired, case-by-case comparisons.
> - A release gate combines must-pass cases, a tolerance on the overall rate, no critical-slice regressions and hard limits, agreed in advance.
> - Measure consistency with repeated trials: pass@k for best-of-k use, pass^k for automation; read flaky cases.
> - Close the loop with shadow and canary releases, online signals, sampled grading and new eval cases from failures.
