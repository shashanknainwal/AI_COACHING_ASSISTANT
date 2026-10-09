---
title: The FDE Operating Loop
type: reading
minutes: 5
---

> **By the end of this lesson** you will be able to run the discover, build, deploy, measure, feed back loop and pick the right first build.

Dana Ruiz says Brightline's referral intake is "too slow" and asks what you'll build first. Find out how slow, then build the smallest thing that tests what's most likely to fail.

```
 1. Discover  → what problem, for whom, measured how?
 2. Build     → smallest thing that tests the riskiest assumption
 3. Deploy    → real workflows, real users, real data
 4. Measure   → against the metric agreed in step 1
 5. Feed back → results to the customer, patterns to your product team
      └──────► back to 1 with sharper questions
```

## 1. Discover

The output is a **problem statement with a number in it**:

> "Tier-1 support agents spend about 6 minutes per ticket finding the right help-center article. Cut that to under 2 minutes for the top 20 ticket categories, without lowering CSAT."

Ask: *"Walk me through the last time this went wrong."* *"What happens if we do nothing?"* *"How would you know in a month that this worked?"*

## 2. Build

The riskiest assumption is usually **data** (can we get it, is it usable?), **feasibility** (is Claude accurate enough?) or **adoption**. If it's data access, your first build is a script that pulls and profiles a week of data, not a UI. If it's model quality, it's a small eval set and a prompt.

## 3. Deploy

Start with a **pilot group** (5 users, not 500), use **shadow mode** (humans review suggestions first), and keep it **easy to roll back**.

## 4. Measure

Track the step-1 metric plus guardrails (quality, cost, latency) against a **baseline**: 2.1 minutes means nothing unless you know it was 6. **Read 20 failures a week**; averages hide them.

## 5. Feed back

A weekly written update to the customer; written patterns and feature requests to your product team.

## Anti-patterns

| Anti-pattern | Fix |
|---|---|
| Discovery forever | Timebox it; build something by end of week 1 |
| Build in a cave | Demo every week, even rough |
| Pilot purgatory | Agree expansion criteria *before* the pilot |
| Vanity metrics ("users love it") | Tie every metric to the problem statement |
| Silent FDE | Weekly written update, same day, same format |

Go around the loop several times in the first two weeks. Speed beats perfection at any step.

> **Key takeaways**
> - Discovery ends in a problem statement with a baseline, a target and a guardrail.
> - Build first whatever tests the riskiest assumption, often data access.
> - Agree expansion criteria before a pilot starts.
