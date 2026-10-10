---
title: "Data Handling and Security Reviews: What You Can Actually Say"
type: reading
minutes: 22
---

> **By the end of this lesson** you'll be able to explain where a customer's prompts go and how long they stay on each platform, describe zero data retention (ZDR), HIPAA readiness and customer-managed keys accurately, lay out identity, network and logging controls, and answer a CISO's questions using only facts you can source, with honest open items for the rest.

## Why this lesson is strict about sources

In a security review, one wrong sentence costs more than ten vague ones. If you tell a bank "your data is never stored" and the design uses the Batches API, you've made a false statement to a regulated customer. It will surface in their audit, and it will be your name on the email.

So this lesson only states facts taken from pages you can open: Anthropic's [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention), [data residency](https://platform.claude.com/docs/en/manage-claude/data-residency), [customer-managed keys](https://platform.claude.com/docs/en/manage-claude/cmek), [authentication](https://platform.claude.com/docs/en/manage-claude/authentication) and platform pages, and the [Commercial Terms of Service](https://www.anthropic.com/legal/commercial-terms). Everything was checked in October 2026. Anything else is marked "confirm with current docs". Your habit in a real review should be the same: every answer carries its source and its date.

**How this shows up in interviews:** the Solutions Architect posting describes a trusted technical advisor to large enterprises (**Official**, job posting). No public account confirms a dedicated security round, so treat security questions as likely material for case discussions and customer role-plays rather than a known format. The skill being tested is the one in this lesson: accuracy under pressure.

## Step 1: Who is the processor?

From lesson 01, and stated directly on Anthropic's data retention page:

- **Anthropic is the data processor** on the Claude API, Claude Platform on AWS and Claude in Microsoft Foundry. Anthropic's arrangements (ZDR, HIPAA readiness) and terms apply there. On Foundry the exact wording is that Anthropic acts as an "independent processor for Microsoft" and Foundry customers are subject to Anthropic's data use terms. Use that phrase in a review rather than inventing a subprocessor chain.
- **The cloud provider is the data processor** on Amazon Bedrock and Google Cloud's Vertex AI. Anthropic's page sends you to the provider's own retention and compliance documentation for equivalent controls.

This one fact routes the review. If the customer chose Bedrock, half of the data questions are AWS questions, and your job is to point to AWS's documentation and help the customer's team find the answer, not to answer for AWS.

## Step 2: Training and ownership

Two statements you can quote, with the source:

- Anthropic's [Commercial Terms of Service](https://www.anthropic.com/legal/commercial-terms) say Anthropic may not train models on Customer Content from the Services, and that the customer retains its rights to inputs and owns its outputs. Data is processed under Anthropic's Data Processing Addendum, which the terms incorporate.
- Anthropic's data retention page commits that retained data "is never used for model training without your express permission."

Say exactly that. Don't paraphrase it into "Anthropic never sees your data," which is a different and false claim (see flagged content below).

## Step 3: Retention, and what ZDR does and doesn't cover

**Standard retention.** The data retention page currently says, among its commitments: "Conversation content (your prompts and Claude's outputs) is not retained by default; the exception is Covered Models, which require 30-day retention." That sentence is the headline, but it comes with caveats you must state alongside it:

- The detailed periods live in Anthropic's commercial data retention policy, linked from the same page. **Quote the current commercial policy** in writing, with its date, rather than a number from memory.
- The customer-managed keys page talks about encrypting workspace data at rest, and the data retention page describes enabling 30-day retention for a workspace. So "not retained by default" depends on the organization's and workspace's retention settings, the models used, and the features used (Batches, Files API and code execution all store data; see below).
- Flagged content and legal holds are exceptions under any arrangement (see the end of this step).

A safe sentence for a questionnaire: "Per Anthropic's data retention page (checked on [date]), conversation content isn't retained by default except for Covered Models; feature-specific retention applies to Batches, Files API and code execution; flagged content may be kept up to 2 years. We'll attach the current commercial retention policy." 

**Zero data retention (ZDR).** Under a ZDR arrangement, Anthropic does not store customer prompts or responses at rest after the API response is returned. Key facts from the docs:

| Fact | Why it matters in a review |
|---|---|
| ZDR is arranged through Anthropic's sales team and enabled **per organization**. A new organization under the same account is not covered automatically. | Check every org the customer uses, including dev and test. |
| It covers the Messages and Token Counting APIs **for eligible features**. | A feature list is part of the answer. |
| **Not ZDR-eligible:** Message Batches (29-day retention), Files API (kept until deleted or expired), code execution and programmatic tool calling (container data up to 30 days), Agent Skills, MCP connector, Claude Managed Agents, Claude Console usage. | If the design uses any of these, "ZDR" isn't the full answer for that data. |
| Under ZDR the API **does not block** non-eligible features. Using one steps outside ZDR for that data. | Enforce the feature allowlist in your own gateway. |
| "Yes (qualified)" features store a bounded artifact, not prompts or outputs: for example, structured outputs cache the JSON schema for up to 24 hours. | Keep sensitive data out of schemas. |
| Claude Fable 5.1, Fable 5, Mythos 5.1 and Mythos 5 are "Covered Models" that **require 30-day retention**; they aren't available under ZDR unless Anthropic expressly authorizes it. A ZDR org can enable 30-day retention for one workspace. | Model choice and retention policy interact. |
| CORS (calling the API from a browser) isn't supported for ZDR organizations. | Route calls through a backend. |
| Claude Platform on AWS follows the first-party retention policy; ZDR is available on request. | Same story on that platform. |

**Retention regardless of arrangement.** Even with ZDR or HIPAA readiness, Anthropic may retain data where required by law or where content is flagged by its automated trust and safety systems; flagged inputs and outputs may be kept for up to 2 years. Put this in every questionnaire answer about retention. Leaving it out is overclaiming.

## Step 4: Regulated data

**HIPAA readiness.** With a signed Business Associate Agreement and a HIPAA-enabled organization, customers can process protected health information through eligible Claude API features. Eligible organizations can execute Anthropic's standard BAA in the Claude Console; negotiated BAAs go through sales. Once enabled it is permanent for that organization, and the API returns a 400 for non-eligible features. The docs also say:

- HIPAA readiness is **not available** on Claude Platform on AWS or Microsoft Foundry. For Bedrock and Vertex AI, use those platforms' compliance documentation.
- Don't put PHI in JSON schema definitions (property names, enum values, patterns), because schemas are cached separately from message content.
- Use separate organizations for HIPAA and non-HIPAA workloads.

For a hospital, this is often the deciding constraint on platform choice. Your answer is a mapping: "on the Claude API, here's the BAA path; on Bedrock, here's AWS's page to review with your compliance team."

**Other frameworks (SOC 2, ISO, PCI and so on).** This lesson deliberately doesn't list Anthropic's certifications. Certification lists change, and the authoritative source is Anthropic's Trust Center (linked from the data retention page) and each cloud provider's compliance pages. In a review: "I'll send you the current reports from the Trust Center under NDA" is a strong answer. Naming a certificate from memory is the most common way architects overclaim.

## Step 5: Keys and encryption

[Customer-managed encryption keys (CMEK)](https://platform.claude.com/docs/en/manage-claude/cmek) let a customer keep a key in AWS KMS, Google Cloud KMS or Azure Key Vault and have Anthropic use it to encrypt certain workspace data at rest. What to know before you mention it:

- It's opt-in through the Anthropic account team, configured per workspace, and **permanent**. Revoking the key makes the protected data permanently unreadable; Anthropic keeps no copy.
- It protects data written after the key takes effect, not earlier data.
- Except on Claude Platform on AWS, CMEK is currently available in US regions only. On Claude Platform on AWS it works with AWS KMS keys only, in the workspace's own account and region.
- Revocation can take up to 1 hour to take effect. Some features change: for example, the Console playground is disabled.
- Data not at rest (such as cache) and data with a TTL under 24 hours isn't encrypted under the customer's key.

For Bedrock and Vertex AI, encryption controls are the cloud provider's; confirm with their docs.

## Step 6: Identity, network and logging

| Control | Claude API | Platform on AWS | Bedrock | Vertex AI | Foundry |
|---|---|---|---|---|---|
| Workload identity | Workload Identity Federation (AWS IAM, Google Cloud, OIDC issuers such as Entra ID or Okta) exchanges a short-lived token; no static key | AWS IAM / SigV4; short-term API keys (max 12 h) | Service role, IAM roles assumed through SAML/OIDC/Identity Center; short-term bearer tokens (max 12 h) | Google Cloud credentials | Entra ID with Azure RBAC, or API keys |
| Keys | Personal and service-account keys tied to an identity; expiration settable at creation | IAM policies on workspace ARNs | IAM | IAM | Azure-issued keys |
| Private networking | Confirm with current docs | AWS PrivateLink supported | Confirm with AWS docs | Confirm with Google Cloud docs | Azure Virtual Network supported |
| Activity logs | Compliance API and its Activity Feed (Activity Feed retained 6 years) | Compliance API: confirm availability and how access is authorized with current docs | CloudWatch and CloudTrail | Request-response logging service | Azure Monitor and Log Analytics |

Anthropic recommends keeping activity logs on at least a 30-day rolling basis on every platform. Every Claude API response carries a `request-id` header; Foundry adds `apim-request-id`. Log both; support needs them.

On SSO for people using the Claude Console: this lesson doesn't state what's supported. Confirm with current docs before answering.

## Step 7: What you control, not the vendor

Many CISO questions are really about the customer's own architecture. These are design patterns, not vendor claims:

- **Data minimization.** Send only the fields the task needs. Redact or tokenize identifiers (account numbers, national IDs) before the call, and re-insert them after if needed.
- **Your logs are the bigger risk.** Teams enable ZDR and then write every prompt to an application log kept for seven years. Apply the same classification and retention to your own prompt logs, traces and eval sets.
- **Prompt injection.** Treat retrieved documents, emails and web pages as untrusted data. Give tools least privilege, keep write actions behind human approval or hard limits, validate outputs before acting on them, and allowlist where agents can send data. Never tell a customer the model "can't be tricked."
- **Feature allowlist at a gateway.** Because ZDR doesn't block non-eligible features, put a thin gateway in front of the API that rejects them, pins the model and `inference_geo`, and attaches the request ID to your audit log.
- **Human accountability.** For decisions about customers (credit, claims, diagnosis), keep a person accountable and log what the model suggested versus what the person decided.

## The three-column answer

For each question in a review, answer in three columns. It keeps you honest and makes the customer's job easier:

| Question | Verified fact (source, date) | Customer's control | Open item (owner, date) |
|---|---|---|---|
| "Do you train on our data?" | Commercial Terms: Anthropic may not train on Customer Content (link, Oct 2026) | Contract review by their legal team | None |
| "How long are prompts kept?" | ZDR available per org on request; Batches, Files API and code execution are outside ZDR; flagged content up to 2 years | Feature allowlist at their gateway | Confirm ZDR enablement for prod and dev orgs (Anthropic account team, before pilot) |
| "Can inference stay in the EU?" | Claude API `inference_geo` offers `us` and `global` only; Foundry offers Global or US Data Zone only; Bedrock (EU profile or in-region in listed regions) and Vertex AI (`eu` multi-region) offer EU options | Platform choice | Confirm the needed model is offered in the EU geography (architect, this week). If they say "Germany only", say no documented option pins current models to one country |
| "Which certifications do you hold?" | Not stated from memory | | Send current Trust Center reports (account team, under NDA) |

An open item with an owner and a date is a strong answer. A confident guess is a weak one.

## Practice prompts (original, in the style of a customer security review)

1. "If we turn on zero data retention, can we still use the Batches API for our overnight job?" (Answer: you can call it, but that data is outside ZDR; Batches retains for 29 days. Offer the alternative.)
2. "We're a hospital network on Azure. Can we send PHI to Claude through Foundry?" (Answer: HIPAA readiness isn't available on Foundry per Anthropic's docs; discuss the Claude API path with a BAA, or the customer's compliance review of other platforms.)
3. "Prove to me that a malicious PDF can't make your agent wire money." (Answer with controls, not guarantees.)

> **Key takeaways**
> - First establish who processes the data: Anthropic on the Claude API, Platform on AWS and Foundry; the cloud provider on Bedrock and Vertex AI.
> - Quote the Commercial Terms on training precisely, and never stretch it into "Anthropic never sees your data."
> - ZDR is per organization and covers eligible features only. Batches, Files API, code execution, Skills, MCP connector and Managed Agents fall outside it, and the API won't stop you using them.
> - Flagged content may be retained up to 2 years under any arrangement. Include it.
> - HIPAA readiness needs a BAA and isn't available on Platform on AWS or Foundry. CMEK is permanent and opt-in.
> - Certifications come from the Trust Center, never from memory.
> - Answer in three columns: verified fact with source, customer control, open item with owner and date.
