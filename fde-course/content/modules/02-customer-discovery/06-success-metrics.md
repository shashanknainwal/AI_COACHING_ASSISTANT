---
title: Success Metrics, Baselines, and Acceptance Criteria
type: reading
minutes: 3
---

> **By the end of this lesson you will be able to:**
> - Build a metric tree from business outcome to weekly measures
> - Measure an honest baseline with the median and p90
> - Write a complete metric definition and testable acceptance criteria

Marisol Grant, Head of Claims Operations at Lumen, will report this project to her boss, Joan Pierce (VP Claims), and the CFO. Agree how success is judged now, or it'll be judged on gut feel.

## The metric tree

```
BUSINESS OUTCOME (lagging, what the sponsor reports)
  Regulator complaints about late payouts: 14/quarter → under 5
        │
OPERATIONAL METRICS (what the team feels)
  Median hours from claim received → claim entered: 26h → 4h
  Rework rate (claims sent back for keying errors): 18% → 5%
        │
SYSTEM METRICS (what you build and tune)
  Field extraction accuracy on policy number: ≥ 99%
  Share of claims auto-filled with no human edits: ≥ 60%
  Cost per processed claim: ≤ $0.15
```

**Lagging** metrics (top) prove value but move quarterly. **Leading** metrics (lower) move weekly and are how you steer. Agree the whole tree with the sponsor.

## Honest baselines

"4 hours" is impressive if today is 26 and trivial if today is 5. Measure from **real system data**, not memory; over **4-8 weeks**, watching for seasonality; **before the pilot starts** (after, the old baseline is gone); and **write down how** so you can measure "after" identically.

### Median and p90, not the average

Process times are skewed: a few items take forever and drag the average.

```
Hours to enter 9 claims:  2, 3, 3, 4, 4, 5, 6, 8, 120
Average: 17.2 hours   ← one stuck claim distorts it
Median:   4.0 hours   ← what a typical customer experiences
```

Report the **median** for typical and **p90** for the tail ("9 in 10 claims within X hours"). **Nearest rank:** sort; the p-th percentile is the value at position ⌈p/100 × n⌉, counting from 1. Here p90 is position ⌈0.9 × 9⌉ = 9: 120 hours.

**Report open items too.** Unfinished claims are usually the slowest; leaving them out makes the baseline look better than reality.

## A complete metric definition

Someone who wasn't in the room should get the same number.

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

Guardrails stop you "winning" by making claims faster and sloppier.

## Acceptance criteria

Metrics measure outcomes over weeks; acceptance criteria define "done" for a deliverable, before you build:

```
Given a claim email with a readable PDF attachment
When the system processes it
Then the claim appears in ClaimsPro within 10 minutes
 And policy number, claimant name, and loss date are pre-filled
 And any field with confidence below 0.9 is highlighted for review
```

"User-friendly" isn't one. "An adjuster can review and submit a pre-filled claim in under 3 minutes" is.

## Common mistakes

| Mistake | Fix |
|---|---|
| Vanity metric ("500 users logged in") | Measure the outcome the logins should cause |
| No baseline | Measure from system data first |
| Unmeasurable ("agent happiness") | Use a proxy such as a monthly survey score |
| Target doesn't improve (26h → 30h) | Check the direction |
| Moving goalposts | Change only through an explicit, written decision |
| Average of skewed data | Median and p90 |

> **Key takeaways**
> - Metric tree: business outcome → operational → system metrics.
> - Baseline from real data, before you change anything; report median, p90 and open count.
> - A complete metric has definition, baseline, target, direction, deadline, owner and guardrails.
