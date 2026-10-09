---
title: "Why Evals Are the FDE's Superpower"
type: reading
minutes: 3
---

> **By the end of this lesson you will be able to:**
> - Explain why a good demo isn't evidence, and what is
> - Build an eval set from real customer data, with labels and slices
> - Turn vague success criteria into measurable ones the customer agrees to

The Brightway demo went well. Then Jordan Lee's COO asks the question every LLM project reaches: *how do we know it works?* "We tried a bunch of examples and they looked good" puts the project at risk. Demos sample the cases you thought of; production sends the ones you didn't.

An **eval** is a repeatable test: fixed inputs, expected results, and a grader that scores each output, reported as rates ("92% overall, 60% on fraud tickets"). Evals make quality discussable, make changes safe, and earn trust when the customer sees the failures too.

## Start from success criteria

Agree what "working" means, in numbers, before building:

| Vague | Measurable |
|---|---|
| "Route tickets accurately" | "≥ 90% reach the right queue on a labeled set of 200" |
| "Catch the urgent ones" | "≥ 98% of safety and fraud tickets marked high urgency" |
| "Answers should be correct" | "≥ 95% judged correct and grounded; 0 invented policies" |
| "Fast and affordable" | "p95 under 3 seconds; under $0.01 per ticket" |

**Not all errors are equal.** Missing a fraud report costs far more than misrouting a sizing question, so say which slices matter most.

## Building the eval set

| Step | How |
|---|---|
| Real data | 100-500 real tickets, with permission and personal data removed; synthetic only to fill gaps |
| Coverage | Mostly typical cases, plus hard ones: ambiguous wording, several issues in one ticket, other languages, prompt injection, garbled input |
| Labels | Two people label independently and discuss disagreements; these often show the *categories* are unclear |
| Slices | Tag category, tier, channel, language; one overall number hides small, important slices |
| Versioning | Keep the set in the repo; add every production failure as a regression case |
| Hold-out | Keep a portion you rarely run, so you don't overfit the prompt to the set |

With 20 cases, one case is 5 percentage points. For decisions that matter, plan for hundreds (lesson 7 adds error bars).

## What to measure and report

Measure quality (accuracy, per-slice rates, confusions), robustness (errors, timeouts, refusals, invalid outputs: record them, don't crash), and cost and latency per case. Report a headline, slices and **the actual failures**.

## Eval-driven development

```
write eval cases → baseline (simplest prompt) → look at failures → change one thing → re-run → compare
```

Baseline first, change one thing at a time, and read failures, not just scores: a drop from 90% to 88% might be three cases with the same bug.

> **Key takeaways**
> - Demos sample the cases you thought of; evals measure what production sends.
> - Agree measurable criteria with the customer, including critical slices.
> - Build from real data, cover edge cases, label carefully, tag slices, version it.
> - Report headline, slices and failures; baseline, change one thing, compare.
