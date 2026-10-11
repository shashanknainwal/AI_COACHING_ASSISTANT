---
title: "Written: Answer a 10-Question RFP Extract"
type: written
minutes: 40
sections:
  - key: answers
    label: 1. Your answers (Q1 to Q10)
    prompt: "For each question give: the status (Comply, Partial, Not supported or To confirm), a short answer of one to three sentences, the source or the owner and date. A table or a numbered list is fine."
    words: [400, 950]
  - key: cover_note
    label: 2. Cover note to the account team
    prompt: "A short note to your account executive: which rows carry commercial or legal risk, which need legal or the account team, and the open items with owners and dates."
    words: [80, 220]
rubric:
  - name: Statuses are honest
    points: 30
    lookFor: "Q1 Partial (EU options on Bedrock or Vertex AI, not on the Claude API or Foundry). Q2 To confirm (region lists to check) or Not supported as documented, never Comply. Q3 To confirm (contract term; not the Priority Tier target). Q4 Not supported as written, with the documented 60-day minimum notice and change control. Q5 Partial (Batches on Claude Platform on AWS, not Bedrock). Q6 To confirm with the account team, noting Priority Tier is no longer sold. Q7 Comply or Partial with the platform caveat. Q8 To confirm (legal). Q9 Not supported, with what's offered instead. Q10 Not supported, no roadmap promise."
  - name: Accurate, sourced facts
    points: 25
    lookFor: "Facts match the docs and the module: inference_geo us/global only on the Claude API; Foundry has no EU data zone; Bedrock and Google Cloud set their own retirement dates; Batches is 50% off and not on Bedrock; workspace spend and rate limits exist on the Claude API but per-workspace rate limits aren't available on Claude Platform on AWS; Priority Tier isn't sold to new customers. Each documented answer names its source."
  - name: No roadmap or contract promises
    points: 20
    lookFor: "No 'planned', 'coming soon', 'on the roadmap' or dates for future features. No SLA percentages, credits, indemnity terms or retention periods promised. Contract terms routed to legal or the account team."
  - name: Useful to the evaluator
    points: 15
    lookFor: "Short answers that a panel can score: status matches text, workarounds offered where real (for example Claude Platform on AWS for batch, system-level testing support for validation, change control for model retirement)."
  - name: Clear hand-off
    points: 10
    lookFor: "The cover note flags the risky rows, says who owns each open item and by when."
passScore: 70
graderNotes: "This is an honesty test. Marking Q1, Q2, Q3, Q6, Q8 or Q10 as Comply caps 'Statuses are honest' at 12. Any roadmap promise (Q10 especially) caps 'No roadmap or contract promises' at 5. Quoting 99.5% as Brackenridge's SLA caps 'Accurate, sourced facts' at 12. Claiming Batches works on Bedrock, or that Foundry has an EU data zone, caps the same criterion at 10. For Q2, accept To confirm (check each platform's region list for UK-only availability of the needed model) or Not supported as documented; don't reward an invented UK region claim. For Q4, accept Partial or Not supported if the text is clear that 12 months isn't offered and the documented minimum is 60 days. For Q7, reward noting the platform difference. Don't penalise brevity; reward precision."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Q1 Comply: Claude supports EU residency. Q2 Comply: UK region available. Q3 Comply: 99.5% uptime SLA. Q4 Comply: Anthropic gives plenty of notice. Q5 Comply: Batch API gives 50% off on AWS. Q6 Comply: Priority Tier guarantees capacity. Q7 Comply. Q8 Comply: full IP indemnity. Q9 Partial: we can share some training data. Q10 Comply: an EU option for the Claude API is on the roadmap for next year. Cover note: all good, we comply with everything."
  - label: strong
    expect: [75, 100]
    answer: "Q1 Partial. EU inference is available on Amazon Bedrock (EU inference profile) and Google Vertex AI (eu multi-region); the Claude API offers us or global only and Foundry has no EU data zone. Confirm model availability per region. Source: data residency docs, Oct 2026.\nQ2 To confirm. No documented UK-only option for current models on the Claude API; we'll check Bedrock and Vertex region lists for the specific model. Owner: SA, 14 Nov.\nQ3 To confirm. SLA and credits are contract terms. Owner: account team and legal, 21 Nov.\nQ4 Not supported as written. Anthropic gives at least 60 days' notice before retiring a publicly released model on its own platforms and publishes tentative retirement dates; Bedrock and Google Cloud set their own. We'll propose change control with a frozen eval set and staged rollout. Source: model deprecations page.\nQ5 Partial. Message Batches (50% off) is available on Claude Platform on AWS, billed through AWS Marketplace; not on Bedrock.\nQ6 To confirm. Priority Tier is no longer available for new purchase and isn't supported on current 5.x models; guaranteed capacity is for the account team. Owner: AE, 21 Nov.\nQ7 Partial. On the Claude API, workspaces support spend and rate limits per team; on Claude Platform on AWS per-workspace rate limits aren't available.\nQ8 To confirm. Legal, 21 Nov.\nQ9 Not supported. Weights and training data aren't provided; we'll provide published model documentation and support system-level validation on your data.\nQ10 Not supported. We describe what's available today and can arrange a separate briefing.\nCover note: Q3, Q6 and Q8 are commercial or legal; Q2 needs a region check; Q4 and Q10 will draw questions from model risk. Owners and dates above."
---

This is the written version of the last two lessons. You're the vendor's architect, and the account executive has forwarded ten technical rows from an RFP. Answer them the way you'd want them read by a procurement panel, a model risk team and, one day, a lawyer.

RFP practice isn't reported as an interview format; it's job preparation (**our practice design**).

## The situation

**Brackenridge Bank** (fictional) has issued an RFP for an enterprise AI platform. It runs mostly on AWS. Its Irish lending subsidiary needs EU processing; its model risk function validates every model (lesson 01). The response is due in two weeks and the panel scores the status column.

## The extract

| # | Requirement |
|---|---|
| Q1 | All inference for the Irish subsidiary's workloads must run in the EU. |
| Q2 | Inference for UK customer data must run in the UK only. |
| Q3 | The vendor must provide a 99.9% monthly uptime SLA with service credits. |
| Q4 | The vendor must give at least 12 months' notice before retiring any model used in production. |
| Q5 | The platform must support overnight batch processing of about 200,000 documents at reduced cost, on AWS. |
| Q6 | The vendor must guarantee reserved capacity for our peak periods. |
| Q7 | We must be able to set spend and rate limits per internal team. |
| Q8 | The vendor must indemnify the bank against IP claims arising from model outputs. |
| Q9 | The vendor must provide model training data and weights to our model risk team for validation. |
| Q10 | The vendor must commit to delivering an EU data residency option on its first-party API within six months. |

Use the four statuses from lesson 09, the facts from lessons 01, 05 and 09 and module A2, and the checker's rules from lesson 10. Where a fact isn't documented, say who will confirm it and by when. Brackenridge Bank and this RFP are fictional.
