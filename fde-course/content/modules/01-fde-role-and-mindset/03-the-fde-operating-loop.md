---
title: The FDE Operating Loop
type: reading
minutes: 12
---

Every successful engagement, whether it lasts three weeks or a year, runs the same loop over and over. Learn it once and you'll always know what to do next.

```
   ┌──────────────┐
   │  1. Discover │  What problem, for whom, measured how?
   └──────┬───────┘
          ▼
   ┌──────────────┐
   │  2. Build    │  Smallest thing that tests the riskiest assumption
   └──────┬───────┘
          ▼
   ┌──────────────┐
   │  3. Deploy   │  Into real workflows, with real users and data
   └──────┬───────┘
          ▼
   ┌──────────────┐
   │  4. Measure  │  Against the metric agreed in step 1
   └──────┬───────┘
          ▼
   ┌──────────────┐
   │ 5. Feed back │  To the customer (results) and your product team (patterns)
   └──────┬───────┘
          └──────────► back to 1, with sharper questions
```

## 1. Discover

Your goal is a **problem statement with a number in it**. Not "improve support with AI", but:

> "Tier-1 support agents spend about 6 minutes per ticket finding the right help-center article. Cut that to under 2 minutes for the top 20 ticket categories, without lowering CSAT."

Discovery questions that consistently pay off:

- *"Walk me through the last time this went wrong."* Stories reveal the real workflow; abstractions hide it.
- *"What happens today if we do nothing?"* This tells you the cost of the problem, which tells you its priority.
- *"Who else touches this process?"* This surfaces hidden stakeholders (security, legal, a team that owns the data).
- *"How would you know in a month that this worked?"* This turns into your success metric.

Module 2 goes deep on discovery.

## 2. Build

Build the **smallest thing that tests the riskiest assumption**. The riskiest assumption is usually one of:

- *Data:* "Can we actually get the tickets out of their system, and are they usable?"
- *Feasibility:* "Can Claude classify these tickets accurately enough?"
- *Adoption:* "Will agents actually use a suggestion panel in their workflow?"

If the riskiest thing is data access, your first build is a script that pulls and profiles one week of data, not a UI. If it's model quality, your first build is a small eval set and a prompt, not an integration.

## 3. Deploy

A prototype on your laptop teaches you a fraction of what a deployment teaches you. Get something in front of real users early, with guardrails:

- Start with a **pilot group** (5 agents, not 500).
- Use **shadow mode** where possible: the system makes suggestions that humans review before anything reaches the end customer.
- Make it **easy to roll back**.

## 4. Measure

Measure against the metric from step 1, plus a small set of guardrail metrics (quality, cost, latency, user satisfaction). Two rules:

1. **Have a baseline.** "Handle time is 2.1 minutes" means nothing unless you know it was 6 minutes before.
2. **Look at examples, not just averages.** Read 20 failures every week. Averages hide the failure modes that will cost you the customer's trust.

## 5. Feed back

This step is the most often skipped, and it separates great FDEs from good ones. Feedback flows in two directions:

- **To the customer:** a short, regular written update with what shipped, the metric, what's next, and what you need from them. This builds trust and keeps the sponsor engaged.
- **To your product team:** patterns across customers, workarounds you built, and feature requests with evidence. Write it down; hallway conversations evaporate.

## Running the loop fast

The loop isn't a waterfall. In the first two weeks of a good engagement you might go around it three or four times in miniature. Speed through the loop beats perfection at any single step.

| Anti-pattern | What it looks like | Fix |
|---|---|---|
| Discovery forever | Six weeks of meetings, no code | Timebox discovery; build something by end of week 1 |
| Build in a cave | Big reveal after a month | Demo every week, even if it's rough |
| Pilot purgatory | Pilot "succeeds" but never expands | Agree on expansion criteria *before* the pilot starts |
| Vanity metrics | "Users love it!" | Tie every metric to the problem statement |
| Silent FDE | Customer doesn't know what you did | Weekly written update, same day, same format |

In the next exercise, you'll practice a core FDE skill from steps 1 and 2: deciding what to work on first when everything is "urgent".
