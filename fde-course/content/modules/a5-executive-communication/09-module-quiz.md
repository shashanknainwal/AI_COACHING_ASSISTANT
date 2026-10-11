---
title: "Module A5 Quiz"
type: quiz
minutes: 10
questions:
  - q: "Which opening sentence works best at the top of a one-pager for a CTO?"
    options:
      - "Generative AI is transforming how enterprises like ours process supplier documents at scale."
      - "Approve a 10-week build of document extraction on Sonnet 5.5; decision by 14 November."
      - "We have completed an extensive proof of concept, and the results are very promising overall."
      - "This document describes our proposed architecture, its components and the integration plan."
    answer: 1
    explain: "Lead with the recommendation and the decision. The others are context, adjectives or a table of contents."
  - q: "What is a CFO's core question about an AI proposal?"
    options:
      - "Which model architecture and retrieval design the team has chosen for the build"
      - "Whether the demo looks impressive enough to show the board next quarter"
      - "What it costs, what it returns, and how wrong those numbers could be"
      - "Whether the security team has already reviewed and approved the vendor"
    answer: 2
    explain: "The CFO wants unit cost, run cost, payback and the assumptions behind them. Fit is the CTO's question and risk is the CISO's."
  - q: "A proposal processes 40,000 claims a month at 6,000 input and 800 output tokens each on Claude Sonnet 5.5 ($2 / $10 per million tokens), with effort set explicitly. What is the approximate monthly model cost?"
    options:
      - "About $80"
      - "About $480"
      - "About $8,000"
      - "About $800"
    answer: 3
    explain: "240M input tokens x $2/M = $480, plus 32M output tokens x $10/M = $320. About $800 a month, roughly 2 cents a claim. At Sonnet 5.5's default high effort, thinking (billed as output) could raise the output line."
  - q: "A CTO asks how confident you are. Which answer is strongest?"
    options:
      - "91% routing on 400 of your claims, likely 88-94%; commercial claims untested yet."
      - "Very confident. The model is state of the art and does well on public benchmarks."
      - "It's AI, so honestly it's hard to say until it has been running in production."
      - "Very confident, because we've never had a customer complain about accuracy before."
    answer: 0
    explain: "It gives what was measured and on what, how much to trust it, and how the unknown will be found out."
  - q: "What are the three steps of the objection method in this module?"
    options:
      - "Deflect the worry, reframe it as an opportunity, then close the deal"
      - "Acknowledge, evidence, offer a test"
      - "Agree with everything, apologise for the risk, then escalate to sales"
      - "Listen carefully, show a live demo, then offer a discount on the spot"
    answer: 1
    explain: "Agree with what is true, give specific evidence with its limits, then propose a time-boxed test with a pass/fail line agreed in advance."
  - q: "A customer says a competitor is cheaper per token. What's the best response?"
    options:
      - "Point out the competitor's weaknesses and recent outages in detail"
      - "Offer a matching discount immediately so the price stops being an issue"
      - "Compare cost per correct outcome on their own eval set"
      - "Explain that price doesn't really matter much to enterprise customers"
    answer: 2
    explain: "A cheaper model that needs more retries or human review can cost more per correctly handled case. Let the measurement decide."
  - q: "A CISO asks which certifications the provider holds and what the retention period is. You're not sure of the current details. What do you do?"
    options:
      - "List the certifications you remember from a similar deal last year"
      - "Say the solution is fully compliant with all relevant regulations"
      - "Move the conversation back to the architecture and the data flow"
      - "Decline to quote from memory; send the current documents by a date"
    answer: 3
    explain: "Compliance facts change, and a CISO writes down what you say. Precise sourcing plus a dated follow-up is a complete answer."
  - q: "The sponsor wants a full launch on December 1st. The eval is 89% against an agreed 95% bar; two categories pass, one is at 82%. What should you do?"
    options:
      - "Say no to the full launch; offer the passing categories on the date"
      - "Agree to the full launch, and add a disclaimer to the weak category"
      - "Say no to the full launch and leave the next step entirely to the sponsor"
      - "Say the project is on track and plan to fix the weak category after launch"
    answer: 0
    explain: "Say no to the plan and yes to the person: a phased launch she can still announce, with the weak category routed to people, a checkpoint and owners."
  - q: "In a steering committee, the CISO insists on 'AWS as the processor' and the CTO's design needs Message Batches. What's the best first move?"
    options:
      - "Side with the CTO, since the board deadline matters more than the CISO's preference"
      - "Ask the CISO what risk it addresses, then lay out Bedrock versus Platform on AWS"
      - "Promise that Message Batches will arrive on Bedrock soon, so both are satisfied"
      - "Side with the CISO and tell the CTO to drop the nightly job from the design"
    answer: 1
    explain: "Find the interest under the position. Bedrock keeps AWS as processor but lacks Batches; Claude Platform on AWS has Batches with IAM and Marketplace billing, but Anthropic is the processor. Present that as a choice with a cost, and never promise roadmap dates."
  - q: "Your own account executive asks you to start a pilot on real customer data before the customer's security review finishes. What's the best response?"
    options:
      - "Agree, as long as the account executive takes responsibility if it goes wrong"
      - "Refuse, and report the account executive to your manager straight away"
      - "Decline that, and offer faster legitimate steps such as a signed pilot agreement"
      - "Agree, but use only a small sample of the real data to keep the risk low"
    answer: 2
    explain: "Hold the line on the review, explain the risk in terms of the deal, and help with what the account executive actually needs: a forecastable commitment, a pre-filled security pack, a dated start."
---

Ten questions on executive communication: who needs what, the one-pager, numbers over adjectives, confidence, objections, saying no, and meetings with several stakeholders. You need 8 correct to pass.
