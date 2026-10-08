---
title: "Written: Adapt a Pattern for a Customer That Doesn't Fit One"
type: written
minutes: 45
sections:
  - key: fit
    label: 1. Which patterns, and why
    prompt: "Which reference architecture(s) from this module you start from, what you keep, what you change, and what you'd leave out of phase 1."
    words: [100, 300]
  - key: architecture
    label: 2. Adapted architecture
    prompt: "A numbered data flow from request to submission. Name the model per step, where people review, and how it connects to their systems."
    words: [150, 450]
  - key: evals
    label: 3. Evals and launch gate
    prompt: "The golden set, the metrics, and the numbers that must be met before phase 1 goes live."
    words: [80, 300]
  - key: cost
    label: 4. Cost estimate
    prompt: "A worked monthly estimate with your token assumptions, plus the cost line that really decides the business case."
    words: [80, 300]
  - key: risks
    label: 5. Risks and what you'd push back on
    prompt: "What could go wrong, what you'd tell Dr. Okafor plainly, and what you'd need confirmed before signing off."
    words: [80, 300]
rubric:
  - name: Pattern fit and adaptation
    points: 20
    lookFor: "Recognises the request as a blend: document processing (assembling and extracting from clinical records into payer forms) plus a knowledge assistant over payer policies (retrieval with freshness and citations). Says explicitly what is kept, changed and dropped from each pattern, and scopes phase 1 narrowly (for example a few high-volume payers or procedures)."
  - name: Architecture with human review
    points: 20
    lookFor: "A coherent numbered flow: intake, pulling records, retrieving the current payer policy with its version, extraction into the payer's form schema with source references, a criteria check with cited evidence, code validation, a nurse review screen showing uncertain fields and evidence, then submission. Models are named per step with reasons. A clinician approves every submission in phase 1; portals without APIs are handled honestly."
  - name: Evals and launch gate
    points: 20
    lookFor: "A golden set built from past requests with known outcomes (approved, denied with reason), including missing-documentation and outdated-policy cases. Field-level accuracy, criteria-match accuracy with citation support, and zero invented clinical facts. A gate with agreed numbers, compared with today's nurse baseline (time per request, denial rate)."
  - name: Cost estimate
    points: 15
    lookFor: "Explicit token assumptions multiplied by correct prices (for example Sonnet 5.5 at $2 input and $10 output per million) to a per-request and monthly figure. Recognises that nurse time (25 minutes per request today) dominates and that the business case is minutes saved and denials avoided, not token price. Bonus for noting Message Batches isn't listed for Vertex AI, or that most of this flow is interactive anyway."
  - name: Risks, pushback and honesty
    points: 15
    lookFor: "Names realistic risks (invented or misread clinical facts, stale payer policy, permission and privacy handling, portal automation fragility, nurses rubber-stamping) with mitigations. Pushes back on 'fully automated submission' for phase 1 and explains why. Says that compliance questions (for example health-data agreements and data handling on Google Cloud) must be confirmed with the vendors' current documentation rather than asserted."
  - name: Executive clarity
    points: 10
    lookFor: "Readable by a Chief Nursing Officer: leads with the recommendation, uses short sections and numbers, avoids jargon or explains it, and ends with clear next steps."
passScore: 70
graderNotes: "This is a recommendation memo, not a code design. Mark down heavily: proposing autonomous submission to payers in phase 1 with no clinician approval; inventing compliance facts (for example stating as fact that a specific certification or agreement is in place) instead of saying they must be confirmed; no numbers at all in the cost section; wrong prices (Sonnet 5.5 is $2/$10, Haiku 5.5 is $0.10/$0.50, Opus 5.5 is $4/$20 per million tokens). Don't require the batch-on-Vertex point. Reward answers that keep phase 1 small and measurable. An answer that copies the support-automation pattern without adapting it (for example, a customer chatbot) should score low on fit."
---

Grace again. This one is from a real-looking pipeline review, and it's the kind of case that separates architects who know patterns from architects who can **adapt** them. The customer's problem isn't any single reference architecture from this module. Your job is to write the recommendation memo you'd send after discovery.

## The brief

> **Brookline Regional Health** (fictional) is a four-hospital network. Its prior-authorization team of 40 nurses handles about **1,400 requests a day**: before certain procedures and drugs, the hospital must show the patient's insurer that the case meets the insurer's criteria.
>
> Today a nurse spends about **25 minutes** per request: reading the patient's chart (notes, labs, imaging reports) in the electronic health record, finding the insurer's current policy for that procedure, checking which criteria are met, filling in the insurer's form, and submitting through the insurer's portal. About 60 insurers matter; their policies change often. About **12% of requests are denied**, many for missing documentation, and each appeal costs another hour.
>
> The health record system has a read API. About half the insurers accept electronic submission through an API; the rest have web portals only. The hospital's IT standard is **Google Cloud**. The hospital has 2 years of past requests with their outcomes.
>
> **Dr. Amara Okafor, Chief Nursing Officer** (a fictional person), says: "I want this fully automated. A nurse should only see the denials."

## What to write

A memo to Dr. Okafor and her CIO, in the five sections on the right. Aim for what you'd actually send: a clear recommendation up front, a phase 1 that can be measured in 8–12 weeks, honest numbers, and plain pushback where needed.

Things to think about:

1. **Which patterns are hiding in here?** Gathering facts from records into a form sounds like one pattern. Checking a request against an insurer's current policy, with evidence, sounds like another. Which parts of each do you keep?
2. **Where must a person stay in the loop,** and how do you make their review fast rather than a rubber stamp?
3. **What does "correct" mean** for a prior-authorization packet, and how would you measure it from two years of history?
4. **What actually drives cost?** Run the token math, then compare it with 1,400 x 25 minutes of nurse time.
5. **What would you refuse to promise?** And which questions (health-data handling, agreements, where processing happens) must be confirmed with the vendors rather than answered from memory?

Useful facts, from Anthropic's [pricing page](https://platform.claude.com/docs/en/about-claude/pricing) and platform docs (checked 2026-10-08):

| Fact | Value |
|---|---|
| Claude Haiku 5.5 | $0.10 input / $0.50 output per million tokens (prompts up to 100K tokens) |
| Claude Sonnet 5.5 | $2 / $10 per million; cache reads $0.10 |
| Claude Opus 5.5 | $4 / $20 per million; cache reads $0.20 |
| Claude on Google Cloud | Available through Vertex AI; PDF input, citations and structured outputs are listed as supported there |
| Message Batches API | Listed for the Claude API and Claude Platform on AWS, not for Vertex AI |
| Citations with structured outputs | Can't be combined in one request |

When you submit, Claude grades your memo against the rubric below. The rubric rewards adaptation, honest scoping and numbers, not length.
