---
title: "Why Evals Are the FDE's Superpower"
type: reading
minutes: 16
---

> **By the end of this lesson you will be able to:**
> - Explain why "it looked good in the demo" isn't evidence, and what is
> - Build an evaluation set from real customer data, with labels and slices
> - Turn vague success criteria into measurable ones the customer agrees to
> - Use evals to drive development instead of checking at the end

## "How do we know it works?"

Every LLM project reaches this moment. The demo went well, the customer is excited, and someone senior asks: *how do we know it works?* If the answer is "we tried a bunch of examples and they looked good," the project is at risk. Demos sample the cases you thought of. Production sends you the cases you didn't.

An **eval** (evaluation) is a repeatable test of an LLM system's quality: a fixed set of inputs, the expected results, and a grader that scores each output. It's the LLM equivalent of a test suite, with one twist: results are rates ("92% of tickets routed correctly"), not pass/fail.

For an FDE, evals are leverage:

- **They make quality discussable.** "92% overall, 60% on fraud tickets" starts a productive conversation. "It seems pretty good" doesn't.
- **They make change safe.** New prompt, new model, lower effort? Run the eval and compare.
- **They earn trust.** A customer who has seen the eval report, including the failures, trusts the system more than one who has only seen a demo.
- **They outlast you.** When you hand the project to the customer's team, the eval is how they'll keep it working.

## Start from success criteria

Before building the eval, agree on what "working" means, in numbers, with the customer:

| Vague | Measurable |
|---|---|
| "Route tickets accurately" | "≥ 90% of tickets reach the right queue on a labeled set of 200" |
| "Catch the urgent ones" | "≥ 98% of safety and fraud tickets are marked high urgency" |
| "Answers should be correct" | "≥ 95% of answers judged correct and grounded; 0 invented policies" |
| "Fast enough" | "p95 latency under 3 seconds" |
| "Affordable" | "under $0.01 per ticket at 5,000 tickets/day" |

Notice the second row: **not all errors are equal**. Missing a fraud report costs far more than sending a sizing question to the wrong queue. Good criteria say which slices matter most.

## Building the eval set

1. **Use real data.** Pull 100-500 real tickets (with the customer's permission and with personal data removed). Synthetic examples are useful for filling gaps, not as the main set.
2. **Cover the distribution and the edges.** Mostly typical cases, plus deliberately hard ones: ambiguous wording ("return the rug because it came damaged"), multiple issues in one ticket, other languages, prompt-injection attempts, empty or garbled input.
3. **Label carefully.** Ideally, two people label each case independently and you discuss the disagreements. Disagreements often reveal that the *categories* are unclear, which is worth fixing before you blame the model.
4. **Tag slices.** Category, customer tier, channel, language. A single overall number hides problems in small but important slices.
5. **Keep it versioned.** The eval set is code: put it in the repository and review changes. Add every production failure you find as a new case ("regression cases").
6. **Hold some back.** If you tune the prompt against every case, you'll overfit to the set. Keep a held-out portion you only run occasionally.

How big? Big enough that the numbers mean something. With 20 cases, one case is 5 percentage points. Lesson 7 shows how to put error bars on a pass rate; for decisions that matter, plan for hundreds of cases.

## What to measure

- **Quality:** accuracy, pass rate against a rubric, per-slice rates, confusions (what gets mistaken for what).
- **Robustness:** errors, timeouts, refusals, invalid outputs. A harness must record these, not crash on them.
- **Cost and latency:** tokens per case and time per case, measured during the eval run.

A good eval report has a headline number, slices, and **the actual failures**, which people should read. Reading 20 failures teaches you more than any metric.

## Eval-driven development

Use evals from the first day, not at the end:

```
write eval cases → baseline (simplest prompt) → look at failures → change one thing → re-run → compare
```

- **Baseline first.** Run the simplest version and record the score. Now every change has something to beat.
- **Change one thing at a time,** so you know what helped.
- **Read failures, not just scores.** A drop from 90% to 88% might be three new failures that are all the same bug.
- **Watch for regressions.** Fixing one slice often breaks another (lesson 7 builds a release gate for this).

> **Key takeaways**
> - Demos sample the cases you thought of; evals measure the cases production will send.
> - Agree on measurable success criteria with the customer, including which slices matter most.
> - Build the set from real data, cover edge cases, label carefully, tag slices, and version it.
> - Report headline numbers, slices and actual failures, and record errors instead of crashing.
> - Run evals from day one: baseline, change one thing, compare.
