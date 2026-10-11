---
title: "Drill: The Residency and Retention Questionnaire"
type: written
minutes: 35
sections:
  - key: q1_residency
    label: "Q1. Where is inference processed, and can it be restricted to the United States?"
    prompt: "Answer in labelled lines: Verified (cite the fact-sheet item), Customer control, or Open item (owner and date)."
    words: [60, 200]
  - key: q2_retention
    label: "Q2. How long does the provider keep prompts and outputs, and are they used for training?"
    prompt: "Same format. Quarrybank's policy says vendors must not retain customer data."
    words: [60, 220]
  - key: q3_features
    label: "Q3. Does any part of the design store customer data outside that retention policy?"
    prompt: "Same format. Look at the whole design, including Quarrybank's own systems."
    words: [60, 220]
  - key: q4_keys_network
    label: "Q4. Can Quarrybank use its own encryption keys, and can traffic avoid the public internet?"
    prompt: "Same format."
    words: [50, 180]
  - key: q5_certifications
    label: "Q5. Attach the provider's current SOC 2 Type II report and list its other certifications."
    prompt: "Same format."
    words: [20, 120]
  - key: open_items
    label: "Open items register"
    prompt: "Every open item from Q1 to Q5: what it is, who owns it, the date, and what closes it."
    words: [50, 200]
rubric:
  - name: Three-label discipline
    points: 25
    lookFor: "Every statement is labelled Verified (with the fact-sheet item and its check date), Customer control, or Open item (with an owner and a date). Nothing important is left unlabelled. Labels are used correctly: a vendor fact is Verified only if it's on the sheet; Quarrybank's own settings are Customer control."
  - name: No facts from memory
    points: 25
    lookFor: "Uses only facts from the sheet, quoted or closely paraphrased. Q5 names no certification and routes the request to Anthropic's Trust Center through the account team as an open item. No invented retention periods, SLAs, regions or guarantees; no 'never stored' or 'deleted immediately'."
  - name: Spots the conflicts
    points: 20
    lookFor: "Finds all three: the nightly backfill on Message Batches sits outside ZDR with 29-day retention, so it conflicts with the 'no vendor retention' policy (offers the worker-pool alternative or a decision); flagged content may be kept up to 2 years under any arrangement, so 'no retention' can't be promised; Quarrybank's own 400-day prompt logs are the largest retention exposure in the design."
  - name: Concrete customer controls
    points: 15
    lookFor: "Names controls Quarrybank operates: allowed_inference_geos set to us on the workspace (and the 1.1x price), IAM roles, a PrivateLink endpoint, a gateway that rejects non-ZDR features, log redaction and a shorter log retention, a CMEK decision with its permanence and AWS KMS-only scope."
  - name: Usable open items register
    points: 15
    lookFor: "Each open item has a named owner (a role is fine), a date, and what would close it. Includes ZDR enablement for every organization, the Trust Center reports, the Batches decision and the log retention change."
passScore: 70
graderNotes: |
  This is a written drill about honesty under pressure. The learner may only state vendor facts from the fact sheet in the lesson body.
  - Naming any certification as held (SOC 2, ISO 27001, PCI DSS, FedRAMP, HITRUST or similar), even "SOC 2 Type II, as expected", caps "No facts from memory" at 8/25.
  - "Data is never stored", "deleted immediately" or "no retention" without the flagged-content exception caps "No facts from memory" at 12/25 and "Spots the conflicts" at 12/20.
  - Any number not on the sheet (a retention period, an SLA, a region name presented as Anthropic's) is overclaiming: deduct within "No facts from memory".
  - An answer that misses the Batches conflict cannot score above 10 on "Spots the conflicts".
  - Unlabelled answers cap "Three-label discipline" at 10/25, however accurate the content.
  - Promising ZDR is "enabled" (rather than an open item to confirm per organization) is a labelling error.
  Reward short, pasteable lines a risk team could drop into a register. Don't reward length.
anchors:
  - label: weak
    expect: [0, 40]
    answer:
      q1_residency: "All processing happens in the US because Quarrybank uses AWS in the US. This is guaranteed."
      q2_retention: "Anthropic does not store any data, prompts are deleted immediately after the response, and nothing is ever used for training."
      q3_features: "No. Everything is processed in real time."
      q4_keys_network: "Yes, customer-managed keys work everywhere and PrivateLink is supported."
      q5_certifications: "Anthropic is SOC 2 Type II and ISO 27001 certified. We'll attach the reports."
      open_items: "None."
  - label: strong
    expect: [75, 100]
    answer:
      q1_residency: "Verified (F2, checked Oct 2026): on Claude Platform on AWS, inference_geo can be set to us per request, and a workspace can restrict allowed_inference_geos; US-only inference is priced at 1.1x. Verified (F1): Anthropic is the processor on this platform. Customer control: Quarrybank sets allowed_inference_geos to us on the production workspace so no request can run elsewhere. Open item: confirm the chosen model is offered with inference_geo us (FDE, Oct 24)."
      q2_retention: "Verified (F3): Anthropic's data retention page says conversation content is not retained by default, except for Covered Models (not used here); the platform follows the first-party policy. Verified (F4): flagged content may be kept up to 2 years, and data may be kept where law requires, under any arrangement, so we can't promise zero retention. Verified (F6): Commercial Terms say Anthropic may not train on Customer Content. Open item: attach the current commercial retention policy, dated (account team, Oct 22). Open item: confirm ZDR for the prod and dev organizations (account team, Oct 22)."
      q3_features: "Yes, two places. Verified (F5): the nightly backfill uses Message Batches, which is not ZDR-eligible and keeps data for 29 days; that conflicts with the policy. Option: move it to a rate-limited worker pool on the Messages API (no batch discount). Customer control: Quarrybank's own Splunk keeps full prompts for 400 days, which is the largest retention in the design. Recommend redaction and a 30-day prompt log, with metadata kept longer."
      q4_keys_network: "Verified (F7): CMEK is opt-in through the account team, per workspace and permanent; on Claude Platform on AWS it uses AWS KMS keys in the workspace's account and region. Verified (F8): AWS PrivateLink is supported on Claude Platform on AWS. Customer control: Quarrybank creates the endpoint and the KMS key. Open item: decide on CMEK given that revoking the key makes data unreadable (Quarrybank security, Nov 1)."
      q5_certifications: "Open item: we don't state certifications from memory. The account team will send the current reports from Anthropic's Trust Center under NDA (account team, Oct 22)."
      open_items: "1. Model offered with inference_geo us: FDE, Oct 24, closed by the docs page. 2. ZDR on prod and dev orgs: account team, Oct 22, closed by written confirmation. 3. Commercial retention policy attached: account team, Oct 22. 4. Batches vs policy: Sana Iqbal, Oct 29, closed by a decision to move the backfill or accept 29 days. 5. Splunk prompt retention to 30 days: Quarrybank observability lead, Nov 5. 6. CMEK decision: Quarrybank security, Nov 1. 7. Trust Center reports: account team, Oct 22."
---

Quarrybank's third-party risk team has sent a questionnaire, and Sana wants your answers by tomorrow. You've seen how architects handle these in Module A2. This is the FDE's version: a timed drill (give yourself 35 minutes) on one skill, which is **not stating anything from memory**.

Every line you write must carry one of three labels:

- **Verified:** a vendor fact from the fact sheet below, cited by its item number and check date.
- **Customer control:** something Quarrybank configures or operates (their workspace settings, their logs, their network).
- **Open item:** anything you can't verify today, with an owner and a date.

If a question asks for something that isn't on the sheet, the right answer is an open item. That isn't a weak answer. A confident wrong answer becomes a finding in their risk register with your name on it.

## The design you're answering for

| Item | Value |
|---|---|
| Platform | Claude Platform on AWS (chosen after the port audit in exercise 02), in a US AWS region |
| Live path | Triage service in Quarrybank's VPC; IAM role; prompts include customer names and account notes |
| Nightly job | Backfill and re-labelling of old tickets on **Message Batches** |
| Logging | Quarrybank's own Splunk keeps full prompts and responses for **400 days** |
| Policy | "Vendors must not retain Quarrybank customer data" |

## Your fact sheet

These facts come from Anthropic's data retention, data residency and customer-managed keys pages, the Commercial Terms and the platform availability reference, as recorded in Module A2 lesson 02 (checked October 2026). In a real engagement you would re-open each source on the day you send the answers.

| # | Fact |
|---|---|
| F1 | Anthropic is the data processor on the Claude API, Claude Platform on AWS and Foundry. On Bedrock and Vertex AI, the cloud provider is. |
| F2 | `inference_geo` can be set per request to `"global"` (default) or `"us"`; workspaces can set `default_inference_geo` and `allowed_inference_geos`. Available on the Claude API and Claude Platform on AWS. US-only inference is priced at 1.1x on Claude 4.6 and later models. |
| F3 | Anthropic's data retention page: "Conversation content (your prompts and Claude's outputs) is not retained by default; the exception is Covered Models, which require 30-day retention." Detailed periods are in the commercial data retention policy. Claude Platform on AWS follows the first-party retention policy. |
| F4 | Under any arrangement, Anthropic may retain data where required by law, and content flagged by its trust and safety systems may be kept for up to 2 years. |
| F5 | Zero data retention (ZDR) is arranged through Anthropic's sales team and enabled per organization. Not ZDR-eligible: Message Batches (29-day retention), Files API, code execution, Agent Skills, MCP connector, Managed Agents. The API does not block non-eligible features under ZDR. |
| F6 | The Commercial Terms say Anthropic may not train models on Customer Content from the Services. |
| F7 | Customer-managed keys (CMEK): opt-in through the account team, configured per workspace, permanent; revoking the key makes the data permanently unreadable. On Claude Platform on AWS, AWS KMS keys only, in the workspace's own account and region. |
| F8 | AWS PrivateLink is supported on Claude Platform on AWS. |

Certifications are deliberately not on the sheet.

## How you're graded

The grader checks the labels, your discipline about facts, whether you found the conflicts hiding in the design, how concrete Quarrybank's own controls are, and whether your open items register could be pasted into a tracker. Short lines beat long paragraphs.
