---
title: "Written: Answer a Security Questionnaire"
type: written
minutes: 35
sections:
  - key: data_flow
    label: 1. Data flow
    prompt: "Describe, step by step, where a claim document goes from the adjuster's screen to the summary and back. Name every system that touches it and who operates each one."
    words: [120, 300]
  - key: retention
    label: 2. Data retention and training
    prompt: "What is stored, where, for how long, and is it used for training? Cover the vendor side and Wrenfield's own systems."
    words: [100, 280]
  - key: access_controls
    label: 3. Access controls and encryption
    prompt: "How are users and workloads authenticated and authorized? How is data protected in transit and at rest? What's documented, and what must be confirmed?"
    words: [80, 250]
  - key: incident_response
    label: 4. Incident response and audit
    prompt: "If a credential leaks or a bad summary harms a claimant, what happens? What logs exist, who holds them, and how would Wrenfield reconstruct an event?"
    words: [80, 250]
  - key: residual_risks
    label: 5. Residual risks and open items
    prompt: "List the risks that remain after these controls, and the open items with an owner and a date."
    words: [80, 250]
rubric:
  - name: Accuracy and sourcing
    points: 30
    lookFor: "Every vendor claim is correct for the stated architecture and is sourced or qualified: Anthropic as processor on the Claude API; ZDR scope (per organization, eligible features only); Commercial Terms on training; inference_geo us and its price effect; flagged content may be retained up to 2 years. No invented certifications, no 'never stored', no guarantees."
  - name: Complete, concrete data flow
    points: 20
    lookFor: "Names every hop: adjuster UI, Wrenfield backend and gateway (redaction, allowlist, logging), Claude API with inference_geo us, response validation, storage of the summary, and the human review step. Says who operates each."
  - name: Specific controls
    points: 20
    lookFor: "Workload Identity Federation or identity-backed keys with expiration, workspace allowed_inference_geos, gateway feature allowlist, redaction before the call, encryption in transit, CMEK considered with its tradeoffs, log retention aligned to Wrenfield policy."
  - name: Spots the conflicts and gaps
    points: 20
    lookFor: "Flags that the planned Batches backlog job is not ZDR-eligible (29-day retention) and proposes an alternative or an explicit decision; flags that medical documents may be PHI and HIPAA readiness needs a BAA and a separate organization; turns each unknown into an open item with an owner and date."
  - name: Clear for a security reader
    points: 10
    lookFor: "Short, plain answers a questionnaire reviewer can paste into their risk register. No marketing language."
passScore: 70
graderNotes: "Mark down hard for overclaiming. Any certification named as held (SOC 2, ISO 27001, PCI DSS, HITRUST, FedRAMP or similar) without saying it must be confirmed from the Trust Center caps Accuracy at 10/30. 'Data is never stored' or 'no retention' without the ZDR scope and the flagged-content exception caps Accuracy at 15/30. Saying the model is immune to prompt injection, or that Anthropic has a specific incident-notification SLA, without a source, is overclaiming. An answer that misses the Batches/ZDR conflict cannot score above 10 on 'Spots the conflicts and gaps'. Reward 'to be confirmed by [owner] by [date]' over confident unsourced detail."
---

Security questionnaires are where enterprise deals slow down. They're also where an architect's credibility is set: the customer's security team will hold you to every sentence. This lesson is practice at writing answers that are complete, specific and true.

## The situation

Grace Liu forwards you a questionnaire from **Wrenfield Insurance** (fictional), a US property and casualty insurer. Their claims team wants Claude to summarize incoming claim packets (forms, photos described in text, repair estimates, and sometimes medical bills for injury claims) so adjusters can triage faster. Adjusters always review the summary before acting.

The proposed architecture, agreed with Wrenfield's platform team last week:

- **Platform:** the Claude API (first-party), model `claude-sonnet-5-5`, through the Messages API.
- **Residency:** Wrenfield requires US-only processing. The workspace sets `allowed_inference_geos: ["us"]` and `default_inference_geo: "us"`.
- **Retention:** Wrenfield asked for zero data retention. The request is with the Anthropic account team and **not yet confirmed**.
- **Identity:** Wrenfield's backend runs on AWS and will use Workload Identity Federation, so there's no static API key.
- **Gateway:** a small Wrenfield service in front of the API redacts Social Security numbers and policy numbers, pins the model and residency settings, and logs the `request-id` of every call.
- **Backlog:** a planned nightly job will clear a backlog of 40,000 old claims using the **Message Batches API** to halve the cost.

## Your task

Answer the five sections on the right as you'd send them to Wrenfield's security team. Use only facts you can source from lessons 01 and 02 (or Anthropic's current docs). For everything else, write an open item with an owner and a date.

Before you write, check the architecture yourself. At least two things in it don't fit together, or fit only if someone makes a decision. A good answer finds them and says so plainly, without waiting to be asked.

## Tips

- Write for a reader who will paste your sentence into a risk register. "Anthropic does not store prompts or responses at rest after the response is returned, under a zero data retention arrangement **once enabled for Wrenfield's organization (pending, account team, by 15 Nov)**" beats "We don't keep your data."
- Separate three owners in every section: Anthropic, Wrenfield, and open items.
- Don't name certifications. Offer to send the current reports from Anthropic's Trust Center.
- Incident response has two halves: what Wrenfield can do immediately (revoke federation rules or keys, stop the gateway, pull logs by request ID), and what you'd confirm with Anthropic (support and notification process). Don't invent the second half.

When you submit, Claude grades your answers against the rubric below.
