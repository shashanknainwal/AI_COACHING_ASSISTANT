---
title: Why Discovery Decides the Engagement
type: reading
minutes: 3
---

> **By the end of this lesson you will be able to:**
> - Explain why most failed deployments fail before any code is written
> - Separate what a customer asks for from what they need
> - Name the outputs every discovery phase must produce

Marisol Grant, Head of Claims Operations at Lumen Insurance, opens your first meeting with: "We need AI to read our claim emails." That's a solution, not a problem. Whether you build the right thing depends on what you find out in the next week.

## A story you will live through

A logistics company buys "an AI assistant for our dispatchers". The FDE gets a feature list from IT, and six weeks later the assistant is accurate and fast. Nobody uses it. Dispatchers already knew where shipments were. Their pain was 40 minutes a day **writing exception emails** about late trucks, and the VP was judged on late-delivery complaints, which had doubled. Nobody asked either of them.

The engineering was excellent. The discovery was missing.

## Asks vs. needs

| The ask | What might be underneath |
|---|---|
| "We need a chatbot for our support team." | Agents search too long; new hires take 3 months to ramp. |
| "Can you build a dashboard of all our shipments?" | The COO is blindsided by late shipments and wants early warning. |
| "We want AI to read our contracts." | Legal misses auto-renewal dates, costing ~$400k a year. |
| "Integrate with Salesforce." | Reps won't use any tool that makes them leave Salesforce. |

The ask is often part of the answer. Understand the need well enough to know whether the ask solves it, and to measure whether it did.

> **A useful reflex:** when you hear "we need X", ask *"What would X let you do that you can't do today?"* then *"What does that cost you now?"*

## Do your own discovery

Treat sales discovery as a hypothesis. It optimizes for winning the deal, the buyer is rarely the user, and things change between the sales call and your kickoff (reorgs, failed internal projects). You're accountable for the outcome, so you need your own understanding.

| When you find out you built the wrong thing | Typical cost |
|---|---|
| During discovery | One conversation |
| During prototyping | A few days of rework |
| During pilot | Weeks, plus lost trust |
| After launch | The renewal |

## What discovery produces

| Output | Lesson | Exercise |
|---|---|---|
| Problem statement with numbers (who, cost, baseline, target, deadline) | Running a discovery call | Analyze a call transcript |
| Stakeholder map | Stakeholder mapping | Build an engagement plan |
| Success metrics and acceptance criteria | Metrics | Measure a baseline |
| Requirements | Structured outputs with Claude | Extract requirements |
| Scope: what you'll build first, and what you won't | Scope and saying no | Change-request calculator |

**Timebox the first pass to about a week**, with real data and something rough by early week two. Then keep discovering: users react to working software more honestly than to questions.

> **Key takeaways**
> - Most failed engagements fail at discovery, not engineering.
> - Customers describe solutions; uncover and quantify the need beneath.
> - Sales discovery is a hypothesis. Do your own, in about a week.
