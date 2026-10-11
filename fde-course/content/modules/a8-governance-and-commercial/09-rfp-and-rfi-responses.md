---
title: "RFP and RFI Responses: Comply, Partial, Not Supported, To Confirm"
type: reading
minutes: 16
---

> **By the end of this lesson** you'll be able to answer RFP and RFI questions with one of four honest statuses, write answers that a procurement evaluator can score and a lawyer can live with, handle the recurring hard questions (SLA, data residency, model deprecation, indemnity), and spot the roadmap promises that turn a winning bid into a broken contract.

## Why architects get pulled in

Large enterprises and public bodies buy through formal processes. An **RFI** (request for information) gathers facts about vendors before a shortlist. An **RFP** (request for proposal) asks for a priced, binding proposal, often with hundreds of questions in a spreadsheet. The sales team owns the response, but the technical questions land on the architect.

Your answers often end up in the contract. Many RFPs say responses become part of the agreement, or are relied on in it. Treat every cell as a written commitment.

## Four statuses, used honestly

Most response templates ask for a compliance status. Use these four, and only these:

| Status | Use it when | The answer must include |
|---|---|---|
| **Comply** | Fully met today, as documented | How it's met, and a link to the public documentation |
| **Partial** | Met with limits, on some platforms, or with a workaround | Exactly what's met, what isn't, and the workaround |
| **Not supported** | Not available today | A plain "no", and an alternative if there is one |
| **To confirm** | You don't know, or it depends on contract terms or the customer's choices | Who will confirm it and by when |

Three rules:

1. **No roadmap promises.** "Planned", "coming soon", "on the roadmap" and "will be available by Q2" don't belong in an RFP answer. If a feature isn't available today, the status is "Not supported" or "Partial". If the customer asks about direction, the account team can arrange a separate roadmap briefing under the right terms; your RFP answer describes today.
2. **The status must match the text.** "Comply" followed by "except on Bedrock" is a partial. Evaluators score the status column; lawyers read the text. When they disagree, you lose either the score or the argument.
3. **"To confirm" is not a weakness.** A guessed "Comply" that turns out wrong is worse than an honest "To confirm" with an owner and a date. Contract terms (SLA credits, indemnity, liability caps) are almost always "To confirm" for the architect: they're the account team's and legal's.

## The recurring hard questions

### Service level agreements

What's public: the service tiers page says Priority Tier targets **99.5% uptime**, for organisations that already have a Priority Tier commitment; Priority Tier is no longer available for new purchase. Anthropic's status page shows incident history. Contractual SLAs for enterprise agreements, and any service credits, are contract terms.

So: "Uptime SLA of 99.9% with service credits?" is **To confirm** (account team and legal), with a note on what you can describe about architecture for resilience (retries with backoff, a fallback model, multiple regions or platforms where residency allows). Don't quote the Priority Tier target as the customer's SLA.

On Bedrock or Google Cloud, the cloud provider's own service terms apply to the service it operates. Say which platform the answer is for.

### Data residency

Use the residency table from module A2 lesson 01 and answer per platform: `inference_geo` with `"us"` or `"global"` on the Claude API and Claude Platform on AWS; EU options through Bedrock or Vertex AI; no EU data zone on Foundry; no documented option that pins current models to a single country such as Germany. "Inference in the EU" is usually **Partial** for a multi-platform question (yes on some platforms, no on others) and must say which. Also be precise about what residency covers: inference location is not the same as every log, support and abuse-monitoring process.

### Model deprecation

What's public: Anthropic's deprecations page says customers with active deployments get **at least 60 days' notice** before a publicly released model retires, and lists tentative retirement dates. Those dates apply to the Claude API, Claude Platform on AWS and Foundry; Bedrock and Google Cloud set their own. Anthropic has also published commitments about preserving model weights. A question like "Guarantee that the model will remain available for five years" is **Not supported** as written; offer the documented notice period and a change-control process (lesson 01).

### Indemnity and IP

Questions about intellectual property indemnity, liability caps and warranties are contract terms. The architect's answer is **To confirm**, owned by legal and the account team. Don't paraphrase what you think the commercial terms say; point to the current terms and let legal answer.

### Certifications and audits

"Do you hold ISO 27001 / SOC 2 / ISO/IEC 42001?" Answer from the vendor's Trust Center on the day, with the link, or mark **To confirm**. Never list a certification from memory.

## Writing an answer an evaluator can score

A good RFP cell is short, specific and checkable:

> **Q17. The solution must support customer-managed encryption keys.** Status: To confirm. Owner: Anthropic account team, by 21 November. Note: depends on the platform chosen; we'll confirm availability and scope for the platform in our proposal.

> **Q22. The solution must allow inference to be restricted to the United States.** Status: Comply (Claude API and Claude Platform on AWS). How: set `inference_geo: "us"` per request, or enforce it per workspace with `allowed_inference_geos`. US-only inference is priced at 1.1x on Claude 4.6 and later models. Source: platform.claude.com data residency documentation.

Patterns to avoid:

- **Marketing in the answer.** "Industry-leading security" scores nothing and invites a clarification question.
- **Hedged "Comply".** If you need "generally", "typically" or "in most cases", the status is Partial.
- **Answering a different question.** If the question asks for an SLA and you describe redundancy, say first that the SLA itself is To confirm.
- **Copy-paste from last year's response.** Platform facts change every few months. Re-check every answer against current documentation.

## Working the response

1. **Triage** the questionnaire with the account team: who owns each row (architect, security, legal, account team).
2. **Build a fact sheet** of documented answers with sources and the date you checked. Reuse it across responses, and re-check it before each one. The next exercise turns this into a checker.
3. **Draft every technical row** with a status, a short answer and a source.
4. **Review for consistency:** status matches text, no roadmap language, every "To confirm" has an owner and a date.
5. **Hand legal and the account team** the contract-term rows, flagged.

> **Key takeaways**
> - Use four statuses: Comply, Partial, Not supported, To confirm. The status must match the text.
> - No roadmap promises in an RFP. Describe today; route direction questions to a separate briefing.
> - SLAs, indemnity and liability are contract terms: To confirm, owned by legal and the account team. The Priority Tier uptime target isn't the customer's SLA, and Priority Tier isn't sold to new customers.
> - Answer residency and deprecation per platform: Anthropic's 60-day notice and retirement dates apply to its own platforms; Bedrock and Google Cloud set their own.
> - Keep a dated, sourced fact sheet, and re-check it before every response.
