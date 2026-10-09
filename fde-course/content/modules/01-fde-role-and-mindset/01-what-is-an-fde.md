---
title: What is a Forward Deployed Engineer?
type: reading
minutes: 2
---

> **By the end of this lesson** you will be able to define the FDE role, describe a typical week, and name the six skill areas this course trains.

Your company just signed Brightline Health, a clinic network where faxed referrals take three days to reach the patient record. Dana Ruiz, VP Operations, wants intake faster by June, not a demo. You're the engineer being sent in.

A **Forward Deployed Engineer (FDE)** owns the outcome at a customer and writes whatever production code it takes to get there. The customer's problem decides what you build, not a roadmap.

## Where the role came from

Palantir made the title well known by sending engineers on-site to connect its platforms to messy customer data. Two lessons stuck: deployments generate the best product insight, and a prototype on the customer's data in week two beats a slide deck. With LLMs, someone still has to find the right task, connect Claude to the data, prove it with evals, and ship it.

## A realistic week

| Day | What happens |
|---|---|
| Monday | Review pilot metrics with the ops lead. Two edge cases fail. |
| Tuesday | Pull 30 days of tickets from their API; add the failures to the eval set. |
| Wednesday | Fix prompt and retrieval: eval accuracy 81% → 90%. Ship to the pilot group. |
| Thursday | Write a one-page data-flow doc for their security team. |
| Friday | Tell your product team: "Three customers asked for X. Here's my workaround." |

## The six skill areas

| Skill | What it means at a customer |
|---|---|
| Customer discovery | Find the problem worth solving, who cares, how success is measured |
| Data wrangling | Profile, clean and reconcile data that's messier than promised |
| Integration engineering | Rate limits, pagination, auth, schema surprises |
| LLM application engineering | Prompts, structured outputs, tool use, retrieval, agents, evals |
| Production engineering | Deploy and debug in environments you don't control |
| Communication | Briefs, demos, feedback to your product team |

Traits that matter: bias to a working thing, owning the outcome rather than the ticket, and low ego about the stack (sometimes the answer is a SQL query and a cron job, not an agent).

## How this course works

The right side runs Python in your browser: a scratchpad on readings, graded by tests on exercises. Claude calls use an offline simulator of the official `anthropic` SDK, so your code also runs against the real API with `pip install anthropic` and an `ANTHROPIC_API_KEY`.

**Try it now:** press **Run** in the editor on the right.

> **Key takeaways**
> - An FDE owns a customer outcome and writes production code to reach it.
> - Deployments are where the best product insight comes from.
