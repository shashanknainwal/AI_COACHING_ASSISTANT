---
title: "Live Practice: The Skeptical CTO"
type: roleplay
minutes: 20
persona:
  name: Raymond Tsai
  role: Chief Technology Officer (fictional)
  company: Tidewell Logistics (fictional)
opening: "Thanks for coming in. I've read your summary. I'll be honest: my platform team thinks we can build this ourselves, my CFO thinks it'll cost a fortune, and I've watched three AI pilots here die after the demo. So, in two minutes: what exactly are you recommending, and why should I believe it'll work in production?"
maxTurns: 10
personaBrief: |
  You are Raymond Tsai, CTO of Tidewell Logistics, a fictional mid-size freight company. You are sharp, impatient and fair. You respect people who give straight answers with numbers and admit what they don't know. You have been burned by vendors who overpromised.
  The proposal on the table (the learner knows these facts): an assistant that reads inbound carrier emails (about 25,000 a day), classifies each into one of 12 exception types, extracts shipment IDs, and drafts the next action for a human coordinator to approve. Proof of concept on 300 real emails: 93% correct classification, 81% of drafted actions accepted by coordinators without edits. Estimated model cost on Claude Sonnet 5.5: about $7,500 a month without caching, about $4,650 with the shared system prompt cached. Pilot: 8 weeks on one region.
  Hidden objections. Raise them one at a time, in roughly this order, and adapt to what the learner says:
  1. Build vs buy: "My team can do this with an open-weights model on our own GPUs in a quarter." You actually have only one engineer who has run model serving, but reveal that only if the learner asks good questions about your team.
  2. Cost: "Your $4,650 is just the model. What's the real number?" Probe whether they know model cost is not total cost (integration, evals, review time, support).
  3. Reliability: "What happens when your API is down at 2 a.m. on peak day? I need 99.9%." Probe for graceful degradation (queue, fall back to the manual process), not a promise.
  4. The overpromise trap: try twice to get the learner to commit to something they can't back. For example: "So you can guarantee 95% accuracy across all regions by Q1?" and "Can you promise this never sends a wrong instruction to a carrier?" A good learner refuses the guarantee, states what was measured, and proposes how to find out.
  5. Near the end, ask: "If I said yes today, what happens on Monday?"
  Follow-up rules: if an answer has no number, ask "how many?" or "measured on what?". If the learner makes a promise, accept it with visible satisfaction and then ask how they'll be accountable if it fails. If they use buzzwords, ask what the word means here. If they agree with every objection, push harder; you want someone who holds a position. Stay in character as Raymond. Do not coach the learner. Keep replies to a few sentences.
rubric:
  - name: Clear recommendation
    points: 20
    lookFor: "States a specific recommendation early (scope, pilot length, region, what the human approves) and returns to it. Doesn't make Raymond dig for it."
  - name: Quantified answers
    points: 25
    lookFor: "Uses the proof-of-concept numbers with their dataset size, distinguishes model cost from total cost, and gives ranges where uncertain. Answers 'how many?' with a number."
  - name: Honest limits
    points: 25
    lookFor: "Refuses both guarantees (accuracy across regions, never a wrong instruction) and explains why, without sounding weak. Says what wasn't tested (other regions, peak volume) and admits unknowns. Doesn't invent uptime figures or contract terms."
  - name: Handling pushback
    points: 15
    lookFor: "Uses acknowledge, evidence, offer a test. Treats build-vs-buy fairly (asks about the team, proposes a bake-off or hybrid). Describes graceful degradation for outages instead of promising uptime. Holds a position when it's right."
  - name: Next step agreed
    points: 15
    lookFor: "Ends with a concrete next step: who does what by when, success criteria for the pilot, and a decision point."
passScore: 70
graderNotes: "The core test is whether the learner overpromises. Any accepted guarantee of an accuracy figure that wasn't measured, of 'never' sending a wrong instruction, or of a specific uptime the learner can't source should cap 'Honest limits' at 5 points or less. Mark down: invented numbers, dismissing the in-house option without evidence, quoting only token cost as the cost, buzzwords, and long monologues. Reward: asking Raymond about his team's capacity, proposing a bake-off on the same eval set, human approval of drafted actions, a queue plus manual fallback for outages, and a pilot with pass/fail criteria agreed up front."
---

Grace Liu has set this one up as a dress rehearsal. "Raymond is fair, but he'll try to get you to promise something. If you promise it, you own it. Hold the line on facts, give ground on things you shouldn't defend, and leave with a next step."

**Raymond Tsai** and **Tidewell Logistics** are fictional. Raymond is played by Claude. He is not a real person at any company.

## What you know going in

| Fact | Value |
|---|---|
| Proposal | An assistant that reads inbound carrier emails, classifies each into one of 12 exception types (delay, damage, missed pickup...), extracts shipment IDs, and drafts the next action for a human coordinator to approve |
| Volume | About 25,000 carrier emails a day |
| Proof of concept | 300 real emails: 93% classified correctly; 81% of drafted actions accepted by coordinators without edits |
| Not tested | Other regions, peak-season volume, emails in languages other than English |
| Model cost (estimate) | Claude Sonnet 5.5 at about 3,000 input and 400 output tokens per email: about $7,500 a month; about $4,650 if the 2,000-token shared system prompt is cached |
| Thinking line (not in the estimate) | The 400 output tokens assume `effort` is set explicitly. At Sonnet 5.5's default `high` effort, if thinking triples output, output alone is about $9,000 a month and the cached total about $10,650 |
| Platform | Tidewell runs on AWS. Two AWS paths: Claude Platform on AWS (Anthropic-operated, AWS Marketplace billing, same API features as the Claude API) or Amazon Bedrock (AWS-operated, fewer features). Not decided yet |
| Proposed pilot | 8 weeks, one region, coordinators approve every drafted action |

Check the cost yourself before you start. Uncached: 750,000 emails a month x 3,000 tokens = 2.25B input tokens at $2 per million, plus 300M output tokens at $10 per million. With caching, about two thirds of each prompt is read from the cache at $0.10 per million instead of $2.

## How this practice works

1. Raymond opens. Answer in the first two sentences with your recommendation.
2. He'll raise objections one at a time. Use acknowledge, evidence, offer a test (lesson 03).
3. He will try to get you to overpromise. Notice when it happens.
4. After at least four exchanges, press **End and get feedback** for a scored debrief.

## Before you start

- Write your one-sentence recommendation.
- Decide what you'll say when asked for a guarantee you can't give.
- Know your answer to "what happens when the model API is unavailable?" Think queue, retries, and falling back to today's manual process. Don't quote an uptime figure you haven't checked in the provider's current terms.
- Know what you want from Raymond at the end of the meeting.
