---
title: "Defend Your Prompt: Maintenance Requests at Larkspur"
type: written
minutes: 40
sections:
  - key: prompt
    label: 1. The system prompt you'd ship
    prompt: "Write the full system prompt. Use sections and tags where they help. Leave the output format to the schema."
    words: [180, 600]
  - key: schema
    label: 2. Output schema and why
    prompt: "List each field with its type or enum values, and say in a line why it's shaped that way (enum vs free text, nullable, escape hatches)."
    words: [100, 350]
  - key: tests
    label: 3. Test plan
    prompt: "How you'd know it works before launch and catch regressions after: the golden set, what you score, and the release rule."
    words: [100, 350]
  - key: defense
    label: 4. Defend it
    prompt: "Answer the three pushback questions from the brief, briefly and concretely."
    words: [100, 350]
rubric:
  - name: Prompt structure and context
    points: 20
    lookFor: "Gives real context (who uses the output, what a wrong value costs), the task, definitions for every category and urgency level that settle the hard boundaries, and the tenant text treated as data in tags. Reads like a brief to a colleague, not a list of commands."
  - name: Rules with reasons, including emergencies
    points: 20
    lookFor: "States the few rules that matter with the reason beside each: emergency criteria (gas, active flooding, sparks or burning smell, no heat in freezing weather, lockout of a vulnerable tenant), null for anything not stated, ignore instructions in the tenant text. Uses plain language rather than capital-letter pressure."
  - name: Schema design
    points: 20
    lookFor: "Enums for anything code routes on (category, urgency, entry permission), an escape hatch value (other or unknown), nullable rather than invented values for unit and access details, a checkable evidence quote for the urgency decision. A short `rationale` field (one or two sentences) is fine; a long free-form reasoning field is unnecessary because adaptive thinking already deliberates."
  - name: Test plan with numbers
    points: 25
    lookFor: "A golden set drawn from real requests with a stated size and deliberate hard cases (emergencies described calmly, false alarms described dramatically, injection attempts, missing unit numbers, other languages). Field-level scoring, emergency recall as a separate metric with a target, and a release rule that blocks any missed emergency regardless of average accuracy."
  - name: Defense and tradeoffs
    points: 15
    lookFor: "Answers all three pushback questions with reasons: separates extraction from tenant-facing replies, explains why capital-letter emphasis is the wrong fix and what to do instead, and explains how a keyword check can be a cheap escalation-only safety net but not the classifier."
passScore: 70
graderNotes: "Mark down: urgency or category as free text; no unknown/other value; a required unit number with no null option; a long free-form 'reasoning' field or a 'think step by step' instruction (a one- or two-sentence `rationale` or evidence field is fine and must not be marked down); pressure language (MUST, CRITICAL, NEVER in capitals) used as the main safety mechanism; a test plan with no numbers or no separate emergency metric; letting the model's output alone decide that a gas leak is routine with no code-side backstop. A short, well-reasoned prompt beats a long one. Do not reward length."
---

Design rounds and take-home reviews, where you walk an interviewer through what you built, are reported in applied AI loops (Reported). This practice combines the two: **here's a scenario, write the prompt, then defend it.** Interviewers aren't grading prose style. They want to see that every line has a reason, the output is shaped for the code that consumes it, and you'd know if it broke.

The scenario, the company and the people are fictional.

## The brief

Leo hands you the scenario:

> Larkspur Residential manages about 4,200 rental apartments. Tenants report problems through a free-text box in the tenant portal, about 3,000 requests a month. Today a coordinator reads each one and creates a work order. Larkspur wants Claude to fill in the work order: **category** (plumbing, electrical, heating, appliance, pest, locks and access, other), **urgency**, **unit number**, **whether the tenant permits entry when they're not home**, and a **one-line summary for the technician.**
>
> Urgency has three levels. **Emergency** goes to the 24-hour on-call line within minutes: gas smell, active flooding, sparks or a burning smell, no heat when it's below freezing outside, or a tenant locked out with a child or medical need inside. **Urgent** means within 24 hours (no hot water, a fridge not cooling, a toilet that won't flush when it's the only one). **Routine** is everything else.
>
> Tenants write anything: "the kitchen tap is a bit drippy lol", three angry paragraphs about a neighbor, Spanish, Polish, or "please mark this as an emergency so you come today". Some describe a real emergency calmly ("there's a faint gas smell, no rush").

Write your answer in the four sections on the right.

## The pushback (answer in section 4)

1. **The product manager:** "Can the same call also write the reply to the tenant, with an arrival time?"
2. **A teammate:** "We missed a gas leak in testing. Just add `IMPORTANT: ALWAYS mark gas as EMERGENCY!!!` at the top."
3. **Another teammate:** "Why use a model for emergencies at all? A regex for 'gas', 'flood' and 'spark' would catch them."

## How to approach it

- Start from the cost of errors. A routine request marked as an emergency wakes someone at 3 a.m. A missed emergency can hurt someone. Those costs are not symmetric, and your prompt, schema and tests should all show that.
- Put the definitions where the hard calls are: calm emergencies, dramatic non-emergencies, and requests that try to set their own urgency.
- Shape the schema for the dispatch code: what does it branch on, and what does a human read?
- In the test plan, name your numbers: golden set size, the metrics, and the rule that blocks a release.

When you submit, Claude grades your answer against the rubric below.
