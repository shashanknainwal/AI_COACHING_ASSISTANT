---
title: "Rolling Out Claude Enterprise, Claude Code and Connectors"
type: reading
minutes: 20
---

> **By the end of this lesson you will be able to:**
> - Lay out the admin controls a seat rollout needs: identity, connectors, Skills, Claude Code policy and analytics.
> - Govern connectors and MCP servers for both the Claude apps and Claude Code.
> - Plan Claude Code through Amazon Bedrock or Google Vertex AI, and explain why that changes how policy is delivered.
> - Separate what you can state from current docs from what you confirm with the account team.

Module A3 made the point that many "AI for our employees" requests are met by seats plus connectors, not a custom build. Module C7 (lesson 12) covered Claude Code inside a customer repo and the managed-settings keys. This lesson is the architect's view of a whole-company rollout: which controls exist, who owns each one, and where the sharp edges are.

Everything below comes from Anthropic's pricing page, help centre and Claude Code docs, checked on 2026-10-10. Plans and admin features change often. Before you put any of it in front of a customer, check the current page, and for anything not listed here, say "I'll confirm with the account team."

## 1. Identity and access

From [claude.com/pricing](https://claude.com/pricing) (October 2026):

- **Team** includes Claude Code, SSO, central billing, admin controls for connectors and usage analytics.
- **Enterprise** adds role-based access, SCIM, audit logs, the Compliance API, custom data retention, IP allowlisting and network-level access control.

What that means in the plan:

| Control | Why it matters | Who owns it at the customer |
|---|---|---|
| SSO | One identity, one place to switch someone off | Identity team |
| SCIM | Joiners and leavers flow from the HR system automatically; no orphaned seats | Identity team plus HR systems |
| Role-based access | Owners, admins and members see different settings | IT, with the AI programme lead |
| Audit logs and Compliance API | Security and legal can see who did what | Security, legal, records management |

What you confirm with the account team rather than state: exact SCIM provider support, how roles map to the customer's groups, Compliance API scope and how access is authorised, and retention options for their contract.

## 2. Connectors: one policy, two places

Connectors bring the customer's systems into Claude. They are also the biggest risk in a seat rollout, because they decide what data a conversation can reach.

From Anthropic's help centre article on custom connectors (remote MCP):

- On **Team**, only Owners and Primary Owners can add a custom connector for the organisation. On **Enterprise**, so can people with a custom role that includes managing Libraries.
- Members then **connect individually**, so Claude reaches only what that person can already reach, unless the connector uses a **shared credential** such as an API key. A shared credential gives every user the same access, so scope it to what every member should see.
- Custom connectors are **not verified by Anthropic**. Review each one like any third-party integration.
- Owners can disable specific tool calls. The article warns that research mode runs connector tools without asking again, so turn off write tools on custom connectors used there.

Claude Code has its own MCP configuration, and managed settings govern it (C7/12): `allowedMcpServers` and `deniedMcpServers` (deny wins), and `managedMcpServers` to provide servers to everyone. Your connector policy should be **one list** applied in both places: which systems, read or write, per-user OAuth or shared credential, and who approved it.

A good default for month one: read-only connectors to the document store and the ticketing system, per-user OAuth only, no write tools, and a named owner for each connector.

## 3. Skills and Projects

From the help centre article on Skills: Skills are available on Free, Pro, Max, Team and Enterprise. They need code execution turned on in the admin settings. Owners of Team and Enterprise organisations can **provision skills for all users**, turn off user-created skills, and control whether members can share or publish skills to the organisation. Enterprise organisations may have skill scanning.

Use this in the rollout. A small set of org-provisioned Skills (the house style for customer letters, the finance close checklist, the incident write-up template) gives every department a useful first week and a consistent output. Module C7 (lesson 08) covers how a Skill is built.

Projects let a team keep shared instructions and documents together. The admin controls for Projects aren't in the sources above: confirm them with the account team before you promise anything about them.

## 4. Claude Code across the engineering org

C7/12 gave you the settings layers and the managed keys. Three rollout decisions sit on top.

**Which provider.** Engineers can sign in with their Team or Enterprise account, or Claude Code can run through Amazon Bedrock or Google Vertex AI (now called Google Cloud's Agent Platform in the Claude Code docs) when the customer wants model traffic and billing in their own cloud account.

- Bedrock: `CLAUDE_CODE_USE_BEDROCK=1` plus an AWS region and the customer's credential chain (SSO profiles work). The IAM policy needs `bedrock:InvokeModel`, `bedrock:InvokeModelWithResponseStream` and the inference-profile read actions. The docs recommend a dedicated AWS account for cost tracking. The WebSearch tool isn't available on Bedrock.
- Vertex: `CLAUDE_CODE_USE_VERTEX=1`, `CLOUD_ML_REGION` (`global`, a multi-region such as `eu`, or a specific region) and `ANTHROPIC_VERTEX_PROJECT_ID`, with the `roles/aiplatform.user` role. The docs recommend a dedicated project.

**Pin the models.** On both clouds the docs warn: without pinning, the `opus` and `sonnet` aliases resolve to Claude Code's built-in defaults, which change between releases. Pin with `ANTHROPIC_DEFAULT_OPUS_MODEL`, `ANTHROPIC_DEFAULT_SONNET_MODEL` and `ANTHROPIC_DEFAULT_HAIKU_MODEL`, and use `availableModels` with `enforceAvailableModels` in managed settings to restrict what people can pick. The docs also warn that an unpinned deployment is billed at the Opus rate once it moves to an Opus default. Pinning is a cost control as much as a stability one.

**How policy reaches laptops.** This is the sharp edge. There are two delivery channels:

| Channel | How it works | Fits |
|---|---|---|
| Server-managed settings | Owners edit JSON in the claude.ai admin console; clients fetch it at startup and hourly. Team and Enterprise. | Orgs without MDM, engineers signing in with their Claude account |
| Endpoint-managed settings | IT deploys `managed-settings.json` or OS policy through MDM | Orgs with MDM; stronger, because the OS can protect the file |

The Claude Code docs say server-managed settings are **skipped** when a session uses a third-party provider (`CLAUDE_CODE_USE_BEDROCK`, `CLAUDE_CODE_USE_VERTEX` and similar) or a custom base URL. So a Bedrock or Vertex rollout needs endpoint-managed settings through MDM, or a self-hosted gateway the docs describe for that case. The docs also call server-managed settings a client-side control, not a security boundary. Real enforcement still lives in IAM, network egress and repository permissions.

## 5. Measuring use

From the Claude Code analytics docs:

- Team and Enterprise admins get a Claude Code dashboard: lines of code accepted, suggestion accept rate, daily active users and sessions, a leaderboard and CSV export.
- **Contribution metrics** (PRs and lines shipped with Claude Code) need the GitHub app. They're in public beta, cover github.com repositories, count only users in the claude.ai organisation (not Console API keys or third-party providers) and aren't available with Zero Data Retention.
- On Enterprise, an Analytics API returns per-user engagement, usage and cost reports.
- For per-user tokens and cost on any provider, Claude Code can export OpenTelemetry.

Plan for the gap: if engineers run through Bedrock, the claude.ai dashboard won't see them. Decide up front whether you'll measure through OpenTelemetry and the cloud bill instead.

Adoption numbers are inputs, not outcomes. Lesson 05 turns them into a plan with real outcome measures.

> **Key takeaways**
> - Team gives SSO, connector controls and analytics; Enterprise adds SCIM, roles, audit logs, the Compliance API and retention controls. Check the pricing page before quoting.
> - Write one connector policy and apply it to both the Claude apps and Claude Code's MCP settings. Prefer per-user OAuth; treat shared credentials as a privilege grant.
> - Provision a few org Skills for week one; confirm Project controls with the account team.
> - On Bedrock or Vertex, pin models and deliver policy through MDM: server-managed settings are skipped for third-party providers.
> - The claude.ai analytics don't see third-party-provider usage; plan OpenTelemetry if you need it.
