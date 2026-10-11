---
title: "Module A5 Quiz"
type: quiz
minutes: 8
questions:
  - q: "Which opening sentence works best at the top of a one-pager for a CTO?"
    options:
      - "Generative AI is transforming how enterprises process documents."
      - "Approve a 10-week build of supplier-document extraction on Claude Sonnet 5.5, with human review for low-confidence fields; decision needed by 14 November."
      - "We have completed an extensive proof of concept with very promising results."
      - "This document describes our proposed architecture in detail."
    answer: 1
    explain: "Lead with the recommendation and the decision. The others are context, adjectives or a table of contents."
  - q: "What is a CFO's core question about an AI proposal?"
    options:
      - "Which model architecture you chose"
      - "Whether the demo looks impressive"
      - "What it costs, what it returns, and how wrong those numbers could be"
      - "Whether the security team has approved it"
    answer: 2
    explain: "The CFO wants unit cost, run cost, payback and the assumptions behind them. Fit is the CTO's question and risk is the CISO's."
  - q: "A proposal processes 40,000 claims a month at 6,000 input and 800 output tokens each on Claude Sonnet 5.5 ($2 / $10 per million tokens). What is the approximate monthly model cost?"
    options:
      - "About $80"
      - "About $480"
      - "About $8,000"
      - "About $800"
    answer: 3
    explain: "240M input tokens x $2/M = $480, plus 32M output tokens x $10/M = $320. About $800 a month, roughly 2 cents a claim."
  - q: "A CTO asks how confident you are. Which answer is strongest?"
    options:
      - "On 400 of your claims, routing was 91% correct, likely 88-94% given the sample size. Commercial claims weren't in the set, so the pilot measures those in week two."
      - "Very confident. The model is state of the art."
      - "It's AI, so it's hard to say."
      - "We've never had a customer complain."
    answer: 0
    explain: "It gives what was measured and on what, how much to trust it, and how the unknown will be found out."
  - q: "What are the three steps of the objection method in this module?"
    options:
      - "Deflect, reframe, close"
      - "Acknowledge, evidence, offer a test"
      - "Agree, apologise, escalate"
      - "Listen, demo, discount"
    answer: 1
    explain: "Agree with what is true, give specific evidence with its limits, then propose a time-boxed test with a pass/fail line agreed in advance."
  - q: "A customer says a competitor is cheaper per token. What's the best response?"
    options:
      - "Point out the competitor's weaknesses"
      - "Offer a discount immediately"
      - "Compare cost per correct outcome on the customer's own eval set"
      - "Say price doesn't matter for enterprise customers"
    answer: 2
    explain: "A cheaper model that needs more retries or human review can cost more per correctly handled case. Let the measurement decide."
  - q: "A CISO asks which certifications the provider holds and what the retention period is. You're not sure of the current details. What do you do?"
    options:
      - "List the certifications you remember from last year"
      - "Say it's fully compliant with all relevant regulations"
      - "Change the subject to the architecture"
      - "Say you won't quote them from memory, point to the provider's current trust and legal documents, and commit to sending them by a specific date"
    answer: 3
    explain: "Compliance facts change, and a CISO writes down what you say. Precise sourcing plus a dated follow-up is a complete answer."
  - q: "The sponsor wants a full launch on December 1st. The eval is 89% against an agreed 95% bar; two categories pass, one is at 82%. What should you do?"
    options:
      - "Say no to the full launch, and offer a December 1st launch of the passing categories with the weak one routed to people and a dated plan to add it"
      - "Agree, and add a disclaimer to the weak category"
      - "Say no and leave the decision to the sponsor"
      - "Say the project is on track and fix it after launch"
    answer: 0
    explain: "Say no to the plan and yes to the person: a phased launch she can still announce, with a checkpoint and owners."
  - q: "Which statement about Anthropic's Commercial Terms is correct, according to the terms themselves?"
    options:
      - "They guarantee customer data never leaves the customer's cloud account"
      - "They state that Anthropic may not train models on customer content from its services"
      - "They list every certification Anthropic holds"
      - "They promise a specific accuracy level for each model"
    answer: 1
    explain: "The terms contain the no-training clause. They don't make the other promises, so don't attribute those to them."
---

Nine questions on executive communication: who needs what, the one-pager, numbers over adjectives, confidence, objections, and saying no. You need 8 of 9 to pass.
