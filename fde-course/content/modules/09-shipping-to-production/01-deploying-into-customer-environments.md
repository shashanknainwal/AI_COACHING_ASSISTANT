---
title: "Deploying into Customer Environments"
type: reading
minutes: 16
---

> **By the end of this lesson you will be able to:**
> - Map out a customer's environment and its constraints before you write deployment code
> - Choose how the customer reaches Claude (the Claude API or their cloud provider) and why it matters to them
> - Get through a security review by preparing answers before the questions arrive
> - Plan a rollout that customers' IT and change-management processes will accept

## You don't own production

At a startup you deploy to your own cloud account, with your own rules. As an FDE, production usually belongs to the **customer**: their cloud account, their network, their identity system, their change-approval board. The code that worked on your laptop now has to run where:

- Outbound internet is blocked except for an **allowlist** of hosts, often through a proxy.
- Secrets live in **their** secrets manager (AWS Secrets Manager, Google Secret Manager, Azure Key Vault, HashiCorp Vault).
- Logs must go to **their** logging and monitoring tools (Datadog, Splunk, CloudWatch, Grafana).
- Users sign in through **their** identity provider (Okta, Microsoft Entra ID) with single sign-on.
- Every production change needs a ticket, a reviewer, and sometimes a weekly change window.

None of this is a nuisance to work around. It's how a large company keeps its customers' data safe, and fitting into it is a core FDE skill.

## Map the environment first

In week one, before deployment code, get answers to these questions:

| Area | Ask |
|---|---|
| **Compute** | Where will this run? Containers (Kubernetes, ECS, Cloud Run), serverless functions, or VMs? Who operates it? |
| **Network** | Which outbound hosts are allowed? Is there a proxy (and a custom TLS certificate)? How do internal services reach ours? |
| **Data** | Which data may leave their environment? Is there a data-residency requirement (EU only, US only)? What personal data is involved? |
| **Identity** | How do users and services authenticate? Who grants access to production? |
| **Secrets** | Which secrets manager? How are secrets injected (environment variables, mounted files)? Who rotates them? |
| **Observability** | Where do logs, metrics and alerts go? Who is on call, us or them? |
| **Change process** | How does a change reach production? Approvals, change windows, freeze periods? |

Write the answers in a one-page **environment doc**. It prevents the classic week-six surprise: "Oh, production can't reach the internet."

## How the customer reaches Claude

Claude is available directly through the **Claude API** and through major cloud platforms: **Amazon Bedrock**, **Google Cloud Vertex AI** and **Microsoft Foundry**. For many enterprises, that choice matters a lot:

- **Existing contracts and billing.** Spending through a cloud provider they already have a contract with can avoid months of new-vendor procurement.
- **Security and network posture.** Traffic and access controls can stay within the cloud environment and identity system their security team already approved.
- **Data residency.** Regional options may help meet residency requirements.

The trade-off: features and model availability can differ by platform and arrive at different times, and each platform has its own client class, model IDs and authentication. Check that every feature your design depends on (structured outputs, prompt caching, batches, specific tools) is available on the customer's platform **before** you build on it. The Anthropic SDKs have dedicated clients for each platform, so most application code stays the same.

## The security review

Expect a security questionnaire, often long. Prepare a short **security brief** before anyone asks:

- **Data flow diagram:** what data goes where, including what is sent to the model and what is logged.
- **Data handling:** what personal data the system touches, how it's minimized (send only the fields needed), and how long anything is retained, by you and by the model provider (point to the provider's published data-retention terms).
- **Access control:** who can access the system, the logs and the secrets; least privilege for service accounts.
- **Secrets:** where they live, how they're rotated, and that none are in code or logs.
- **Threat model for LLM features:** prompt injection, data exfiltration through tools, over-permissioned agents, and the guardrails from Module 7.
- **Logging and audit:** what's logged (metadata, not conversations, unless agreed), redaction of personal data, and audit trails for actions.

Answering clearly and early shortens reviews from months to weeks.

## Packaging and rollout

- **Ship a container image** with pinned dependency versions, and configure it entirely through environment variables (next lesson). The same image runs in dev, staging and prod.
- **Health checks:** a `/healthz` endpoint that checks the service itself, and a readiness check that verifies required configuration and dependencies at startup.
- **Infrastructure as code** (Terraform, CloudFormation, Helm charts), so the customer's platform team can review and reproduce the deployment.
- **Staged rollout:** dev → staging (with realistic data) → a pilot group → everyone. Pair it with the shadow and canary techniques from Module 8.
- **A rollback plan** written before the first deploy. "Redeploy the previous image tag" is fine, as long as someone has tested it.

> **Key takeaways**
> - In customer environments, their network, secrets, identity, observability and change process set the rules; map them in week one.
> - Claude is available through the Claude API, Amazon Bedrock, Google Cloud Vertex AI and Microsoft Foundry. Choose with the customer, and check feature availability before you depend on it.
> - Prepare a security brief (data flow, data handling, access, secrets, LLM threat model, logging) before the questionnaire arrives.
> - Ship one configurable container image, add health checks and infrastructure as code, roll out in stages, and test the rollback.
