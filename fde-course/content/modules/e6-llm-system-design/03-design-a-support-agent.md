---
title: "Design It: A Support Agent at 10,000 Tickets a Day"
type: written
minutes: 45
sections:
  - key: requirements
    label: 1. Requirements and assumptions
    prompt: "What you'd ask the interviewer, what you assume, and the numbers you design for."
    words: [80, 250]
  - key: architecture
    label: 2. Architecture
    prompt: "Components and the request flow, step by step. Name models, tools, data stores and where humans come in."
    words: [150, 450]
  - key: quality
    label: 3. Evals and the quality bar
    prompt: "How you'd know it works before launch and keep knowing after."
    words: [80, 300]
  - key: risks
    label: 4. Failure modes, cost and latency
    prompt: "What breaks, how you'd detect it, and a rough cost per ticket."
    words: [80, 300]
rubric:
  - name: Scoping
    points: 20
    lookFor: "Asks or states the questions that change the design (ticket mix, channels, systems of record, what 'resolved' means, escalation rules) and commits to explicit numbers."
  - name: Architecture with tradeoffs
    points: 25
    lookFor: "A coherent flow (triage, retrieval, tools, action, escalation) with reasons for each choice and at least one alternative considered and rejected."
  - name: Evals and quality bar
    points: 20
    lookFor: "Concrete offline evals (golden set from real tickets, graded criteria) plus online signals (escalation rate, reopen rate, CSAT), and a launch gate."
  - name: Failure modes and safety
    points: 20
    lookFor: "Names realistic failures (hallucinated policy, wrong refunds, prompt injection through ticket text, outages) with detection and mitigation, including human review for risky actions."
  - name: Cost and latency math
    points: 15
    lookFor: "A rough but explicit cost-per-ticket and latency estimate from token counts and model prices, and at least one lever to reduce it (caching, model routing, batching)."
passScore: 70
graderNotes: "Reward explicit numbers and reasoning over long component lists. An answer that never estimates cost, never mentions evals, or lets the model issue refunds without limits should not pass."
---

System design rounds for applied AI roles are reported at every lab in this course. They rarely want a perfect diagram. They want to see you **scope an ambiguous problem, make tradeoffs out loud, and prove you'd know whether it works.**

## The prompt

> A consumer electronics retailer gets about 10,000 support tickets a day by email and chat: order status, returns, warranty claims, troubleshooting, and the occasional angry escalation. They want an AI agent that resolves as many tickets as possible end to end, using their order system, returns API and help-centre articles. Design it.

Answer in the four sections on the right, as you would talk through it in a 45-minute round.

## How to approach it

1. **Scope first (5 minutes in the real round).** What share of tickets is each type? Which actions are safe to automate (order status) and which need limits (refunds)? What counts as resolved? Write your assumptions down as numbers.
2. **Draw the flow.** Triage, then retrieve the right context, call tools, decide, act or escalate. Say which model handles which step, and why.
3. **Define the quality bar before launch.** Build a golden set from real historical tickets, decide what "correct" means for each type, and set a launch gate.
4. **Break it on purpose.** Hallucinated policy, a refund loop, prompt injection hidden in an email, the order API timing out. For each: how do you notice, and what happens next?
5. **Do the math.** Estimate tokens per ticket, multiply by model prices and volume. A rough number with stated assumptions beats no number.

Useful facts for the math: Claude Opus 5.5 costs $4 per million input tokens and $20 per million output tokens; Claude Sonnet 5.5 is $2 and $10; Claude Haiku 5.5 is $0.10 and $0.50. Cached input is much cheaper than fresh input, so a long, stable system prompt and help-centre context are good candidates for prompt caching.

When you submit, Claude grades your design against the interviewer rubric below.
