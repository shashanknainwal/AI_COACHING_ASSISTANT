---
title: "Deploying into Customer Environments"
type: reading
minutes: 3
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

Claude is available through the **Claude API**, **Amazon Bedrock**, **Google Cloud Vertex AI** and **Microsoft Foundry**. Using a cloud they already have can skip months of procurement, stay inside an approved security setup, and offer regional options.

The trade-off: features and models can differ or arrive later by platform, and each has its own client, model IDs and auth. **Check every feature you depend on (structured outputs, caching, batches, specific tools) on their platform before building.** The SDKs have a client per platform, so most code stays the same.

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
> - Claude runs on the Claude API, Bedrock, Vertex AI and Foundry; check feature availability on the customer's platform first.
> - Have a security brief ready before the questionnaire.
> - One configurable image, health checks, IaC, staged rollout, tested rollback.
