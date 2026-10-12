---
title: "Deploying into Customer Environments"
type: reading
minutes: 8
---

> **By the end of this lesson you will be able to:**
> - Map a customer's environment before writing deployment code
> - Choose with the customer how they reach Claude
> - Prepare a security brief and a rollout plan

Jordan Lee wants Brightway's ticket-triage assistant live before the holiday peak. It works on your laptop, but production is Brightway's cloud account, behind their proxy, under their change board.

## Map the environment first

Their allowlists, secrets manager, logging tools, identity provider and change tickets set the rules. In week one, ask:

| Area | Ask |
|---|---|
| **Compute** | Containers, serverless or VMs? Who operates it? |
| **Network** | Allowed outbound hosts? Proxy with custom TLS certificate? |
| **Data** | What may leave? Residency rules? Personal data? |
| **Identity** | How do users and services authenticate? |
| **Secrets** | Which manager? Env vars or files? Who rotates? |
| **Observability** | Where do logs and alerts go? Who is on call? |
| **Change process** | Approvals, change windows, freezes? |

Put the answers in a one-page **environment doc**. It prevents the week-six surprise: "production can't reach the internet."

## How the customer reaches Claude

Claude is available five ways. Using a cloud the customer already has can skip months of procurement and stay inside an approved security setup.

| Platform | Who operates it | Auth and billing | Model IDs |
|---|---|---|---|
| **Claude API** | Anthropic | Anthropic API key; Anthropic billing | `claude-opus-5-5` |
| **Claude Platform on AWS** | Anthropic, on AWS infrastructure | AWS IAM with SigV4 signing; AWS Marketplace billing | Bare IDs, same as the Claude API |
| **Amazon Bedrock** | AWS | AWS IAM; AWS billing | Provider-prefixed (`anthropic.…`) |
| **Google Cloud Vertex AI** | Google | Google Cloud IAM; Google billing | Platform-specific; check its model list |
| **Microsoft Foundry** | Microsoft (some deployments hosted by Anthropic) | Azure identity; Azure billing | Platform-specific; check its model list |

**Claude Platform on AWS** is the option to know for the very common "we only buy through AWS" customer. Anthropic runs it, so the API matches the Claude API feature for feature on the same day, but access is controlled with the customer's own IAM roles and billed through their AWS Marketplace account. In Python it's `AnthropicAWS()` from the `anthropic[aws]` package, configured with an AWS region and a workspace ID. It is not the same thing as Bedrock: Bedrock is operated by AWS, with its own release timing and feature subset.

**Features differ by platform.** Check every feature you depend on before building. A few gaps that change designs:

| Feature | Claude API and Claude Platform on AWS | Bedrock | Vertex AI | Foundry |
|---|---|---|---|---|
| Message Batches (50% off) | Yes | No | No | No |
| MCP connector (Claude calls a remote MCP server for you) | Beta | No | No | Beta |
| Agent Skills | Yes | No | No | Beta (Anthropic-hosted deployments only) |
| Code execution tool | Yes | No | No | Anthropic-hosted deployments only |
| Server-side refusal `fallbacks` | Beta | No | No | No |
| `inference_geo` (data residency control) | Yes | No | No | No |

Availability moves fast; treat this table as a snapshot and confirm on the current platform docs. The [platform fit checker](/learn/a2-enterprise-deployment/03-exercise-platform-fit-checker) in the Architect track turns this into code. Regulated data adds another axis: HIPAA readiness, for example, is not offered on every platform (Module 1 covers Brightline's case), so confirm it with the customer's Anthropic account team and the cloud provider's compliance docs.

The SDKs have a client per platform, so most code stays the same. In a locked-down account, prefer the platform's IAM roles over long-lived API keys wherever the platform supports them.

## The security brief

Write it before the questionnaire arrives:

- **Data flow diagram:** what goes to the model, what is logged.
- **Data handling:** personal data touched, fields minimized, retention (yours and the provider's published terms).
- **Access control:** who can reach the system, logs and secrets; least privilege.
- **Secrets:** where they live, how they rotate, none in code or logs.
- **LLM threat model:** prompt injection, exfiltration through tools, over-permissioned agents, and your guardrails (Module 7).
- **Logging and audit:** metadata not conversations, redaction, audit trails for actions.

Early answers cut reviews from months to weeks.

## Packaging and rollout

- **One container image** with pinned dependencies, configured only through environment variables, running in dev, staging and prod.
- **Health checks:** `/healthz` for liveness, plus a readiness check that verifies config and dependencies at startup.
- **Infrastructure as code** (Terraform, CloudFormation, Helm) their platform team can review.
- **Staged rollout:** dev → staging → pilot group → everyone, with shadow and canary from Module 8.
- **A tested rollback plan** before the first deploy.

> **Key takeaways**
> - Map compute, network, data, identity, secrets, observability and change process in week one.
> - Claude runs on the Claude API, Claude Platform on AWS, Bedrock, Vertex AI and Foundry. Batches, the MCP connector and Skills are missing on Bedrock and Vertex; check every feature on the customer's platform first.
> - Have a security brief ready before the questionnaire.
> - One configurable image, health checks, IaC, staged rollout, tested rollback.
