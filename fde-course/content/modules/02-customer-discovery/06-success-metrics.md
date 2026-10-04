---
title: Success Metrics, Baselines, and Acceptance Criteria
type: reading
minutes: 16
---

> **By the end of this lesson you will be able to:**
> - Build a metric tree that connects a business outcome to things you can measure weekly
> - Measure an honest baseline, and explain why the median usually beats the average
> - Write a complete metric definition and testable acceptance criteria
> - Recognize the metric mistakes that make "successful" projects look like failures

## "It works" is not a success criterion

At the end of an engagement, someone will decide whether it was worth the money. If you haven't agreed on how that decision will be made, it will be made on gut feel, often by someone who wasn't paying close attention. Agreed metrics protect the customer, your company, and you.

## The metric tree

Connect three levels, from what the executive cares about down to what you can change this week.

```
BUSINESS OUTCOME (lagging, what the sponsor reports)
  Regulator complaints about late payouts: 14/quarter → under 5
        │
        ▼
OPERATIONAL METRICS (what the team feels)
  Median hours from claim received → claim entered: 26h → 4h
  Rework rate (claims sent back for keying errors): 18% → 5%
        │
        ▼
SYSTEM METRICS (what you build and tune)
  Field extraction accuracy on policy number: ≥ 99%
  Share of claims auto-filled with no human edits: ≥ 60%
  Cost per processed claim: ≤ $0.15
```

- **Lagging metrics** (top) prove value, but move slowly: you might wait a full quarter for the regulator numbers.
- **Leading metrics** (middle and bottom) move weekly and predict the lagging ones. They're how you steer.

Agree the whole tree with the sponsor. Then report the leading metrics weekly and the lagging metric whenever it's available.

## Baselines: measure before you change anything

A target without a baseline is meaningless. "Process claims in 4 hours" is impressive if today is 26 hours and trivial if today is 5.

Rules for an honest baseline:

1. **Measure from real system data,** not from what people remember. People are very bad at estimating durations.
2. **Use a meaningful window,** for example the last 4-8 weeks, and check for seasonality (month-end spikes, holidays).
3. **Measure before your pilot starts.** Once you change the workflow, the old baseline is gone forever.
4. **Write down exactly how you measured it,** so you can measure the "after" identically.

### Why the median, not the average

Process times are almost always **skewed**: most items are quick, a few take forever. The average gets dragged around by those few outliers.

```
Hours to enter 9 claims:  2, 3, 3, 4, 4, 5, 6, 8, 120
Average: 17.2 hours   ← one stuck claim makes the "typical" claim look 4x slower
Median:   4.0 hours   ← the middle claim; what a typical customer experiences
```

Report the **median** for "typical," and a high **percentile** like the 90th (p90) for "how bad does it get." The p90 is the value that 90% of items are at or below. Executives intuitively understand "9 out of 10 claims are entered within X hours."

**Percentile by nearest rank:** sort the values; the p-th percentile is the value at position ⌈p/100 × n⌉ (counting from 1). For the 9 values above, p90 is at position ⌈0.9 × 9⌉ = 9, which is 120 hours. That stuck claim is real, and the p90 makes it visible.

### Don't forget the items that haven't finished

If 15 claims from the window are still open, excluding them makes the baseline look better than reality, because the open ones are usually the slowest. Always report how many items are still open alongside the median.

## A complete metric definition

A metric is fully defined when someone who wasn't in the room could measure it and get the same number. Use a template like this:

| Field | Example |
|---|---|
| **Name** | Median claim intake time |
| **Definition** | Hours from email received (mail server timestamp) to claim created in ClaimsPro |
| **Baseline** | 26.0 hours (median, Jan 6 – Feb 28, n = 7,412; 15 still open) |
| **Target** | 4.0 hours |
| **Direction** | Decrease |
| **Deadline** | 2026-06-30 |
| **Owner** | Marcus Lee (Claims Ops) |
| **Guardrails** | Rework rate must not increase; adjuster satisfaction ≥ current |

The **guardrails** matter. It's easy to make claims faster by making them sloppier. Guardrails prevent you from "winning" a metric while hurting the business.

## Acceptance criteria

Metrics measure outcomes over weeks. **Acceptance criteria** define, before you build, what "done" means for a specific deliverable. Write them in a testable form, such as Given/When/Then:

```
Given a claim email with a readable PDF attachment
When the system processes it
Then the claim appears in ClaimsPro within 10 minutes
 And policy number, claimant name, and loss date are pre-filled
 And any field with confidence below 0.9 is highlighted for review
```

Good acceptance criteria are specific, observable, and agreed in writing. "The system should be user-friendly" is not an acceptance criterion. "An adjuster can review and submit a pre-filled claim in under 3 minutes" is.

## Common metric mistakes

| Mistake | Example | Fix |
|---|---|---|
| Vanity metric | "500 users logged in" | Measure the outcome the logins should cause |
| No baseline | "Reduce handling time" | Measure the current value from system data first |
| Unmeasurable | "Improve agent happiness" | Pick a proxy: a short monthly survey score |
| Target doesn't improve | Baseline 26h, target 30h | Check the direction; it's usually a typo, but catch it |
| Moving goalposts | Metric changes every month | Agree in writing; change only through an explicit decision |
| Average of skewed data | "Average time is 17h" | Report median and p90 |
| Ignoring open items | Only counting finished claims | Report the open count with the baseline |

## Making it routine

Two of the most useful small scripts an FDE can write are a **baseline calculator** (from raw timestamps) and a **metric definition checker** (catches missing fields and targets that don't improve on the baseline). That's your next exercise.

> **Key takeaways**
> - Build a metric tree: business outcome → operational metrics → system metrics.
> - Measure the baseline from real data before you change anything, and record how you measured it.
> - For process times, report the median and p90, plus the number of items still open.
> - A complete metric has a definition, baseline, target, direction, deadline, owner, and guardrails.
