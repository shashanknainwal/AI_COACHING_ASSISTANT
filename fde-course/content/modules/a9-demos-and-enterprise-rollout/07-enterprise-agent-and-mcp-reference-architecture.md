---
title: "Reference Architecture: A Back-Office Agent Across Systems of Record"
type: reading
minutes: 20
---

> **By the end of this lesson you will be able to:**
> - Draw a back-office agent that reads and writes across several systems of record.
> - Place an MCP gateway, per-user permissions and approval queues in that design.
> - Decide when computer use is the right tool for a portal-only system, and how to contain it.
> - Choose a runtime (your own loop, the Agent SDK or Managed Agents) given the customer's platform.

Module A6 gave you four reference architectures, all centred on one model task. Module C7 taught MCP, sub-agents, Skills and computer use as building blocks. This lesson puts them together in the shape enterprises now ask for most: an agent that does back-office work across the systems they already run, with people approving what matters.

The worked example is Halberd Freight Group (fictional) again: after the seat rollout, Bas Achterberg wants an agent that handles carrier-invoice disputes end to end.

## The job

For each flagged invoice, the agent must: read the invoice and the agreed rate, look up the shipment in the transport-management system (TMS), check proof of delivery in the carrier's web portal (no API), draft a dispute to the carrier, and, after approval, put the invoice on hold in the ERP and log the dispute. About 1,500 disputes a month.

## The architecture

```text
 Auditor UI ── task ──> Agent runtime (loop, budget, trace)
                            │  model calls (Claude)
                            ▼
                     MCP gateway  (authN, allowlist, per-user tokens, policy, audit log)
           ┌───────────────┬───────────────┬───────────────┐
           ▼               ▼               ▼               ▼
      TMS server      ERP server      Doc store       Computer-use worker
      (read)          (read; write    (read)          (sandboxed browser,
                       via approval)                    carrier portals, read)
                            │
                     Approval queue ──> auditor approves ──> write executes
```

Five ideas carry the design.

### 1. One MCP server per system of record

Each system gets a narrow server with a few well-named tools (`get_shipment`, `get_agreed_rate`, `place_invoice_hold`), not a generic "run SQL" tool. Read and write tools are separate, so policy can treat them differently. C7 lessons 02 to 04 cover building and securing these servers.

### 2. An MCP gateway in front of them

The gateway is a pattern, not a product name: a service the customer runs between agents and MCP servers. It does what an API gateway does for microservices:

- **Authentication** of the calling agent or user, and **per-user tokens** to the downstream system, so the agent can only reach what the requesting auditor can reach.
- **An allowlist** of servers and tools, matching the connector policy from lesson 04.
- **Tool-level policy:** which tools need approval, rate limits, and argument checks (an amount above a threshold, an invoice outside the user's region).
- **An audit log** of every tool call with the user, arguments and result, kept where the customer's records rules say.

Without a gateway, every agent team re-implements these controls, and security reviews each one separately.

### 3. Approval queues for writes

The model proposes; a person approves; code executes. A write tool doesn't write. It creates a pending action with the exact arguments, the evidence and a diff ("ERP invoice 55021: status open to on hold, reason: overcharge 280 EUR"). An auditor approves or rejects in the queue, and only then does the gateway call the real system with the stored arguments. The model can't change them after approval.

Start with every write approved. Loosen it only for a narrow, rule-defined class with an eval behind it (for example, holds under 100 EUR on carriers with a signed rate card), enforced in code at the gateway.

### 4. Computer use only where there is no API

Carrier portals often have no API. Computer use lets Claude operate a browser from screenshots. It's the right tool when the alternative is a person clicking through the portal, and the wrong tool when an API exists or the vendor can provide one.

Contain it:

- Run it in an isolated, disposable sandbox with only the portal's domain reachable.
- Give it read-only portal accounts where possible.
- Treat everything on screen as untrusted input. A page can carry injected instructions (C7 lesson 14 covers this). The worker returns extracted facts to the agent, not free text with instructions.
- Check the portal's terms of use. Some forbid automated access. That is a contract question for the customer, not a technical one.

Platform note from the claude-api skill: computer use is beta on all five platforms. Claude Opus 5.5 accepts only the newer computer toolset on the Claude API and Google Cloud, while Amazon Bedrock still accepts the earlier computer tool version. Check the computer-use docs before promising it on a given platform.

### 5. Budgets, traces and evals

Each task gets a step and token budget, a full trace (every model call and tool call), and a final state you can check. Eval the end state ("hold placed on the right invoice, dispute sent with the right amount") and the trajectory ("didn't call the write tool before the read tools"). Module E8 covers agent evals in depth.

## Choosing the runtime, by platform

The customer's platform often decides the runtime. From the claude-api skill's platform table (checked 2026-10-10):

| Capability | Claude API | Claude Platform on AWS | Amazon Bedrock | Google Vertex AI | Microsoft Foundry |
|---|---|---|---|---|---|
| Messages, tool use, your own loop | Yes | Yes | Yes | Yes | Yes |
| Managed Agents | Beta | Beta | No | No | No (inferred; not documented) |
| MCP connector (remote MCP from the API) | Beta | Beta | No | No | Beta |
| Agent Skills via the API | Yes | Yes | No | No | Beta (Hosted on Anthropic only) |
| Computer use | Beta | Beta | Beta | Beta | Beta |

What that means:

- **On the Claude API or Claude Platform on AWS**, Managed Agents can host the loop, sandbox and session state for you. Weigh that against where tool calls run and what the security review needs.
- **On Bedrock or Vertex**, you run the loop: the Agent SDK or your own loop, with your MCP client talking to the gateway. The API-side MCP connector isn't available there, so MCP stays on your side.
- **Everywhere**, the gateway, approval queue and audit log are the customer's own components. They don't depend on the model platform, which is one more reason to build them as shared services.

Recheck this table before every design. It moves.

## What to say in the room

- "The agent never writes to the ERP on its own. It proposes, an auditor approves, code executes."
- "Every tool call goes through one gateway that your security team configures once."
- "We use the portal through a browser only because the carrier has no API. If they offer one, we switch."

> **Key takeaways**
> - One narrow MCP server per system of record, read and write tools separate.
> - An MCP gateway gives one place for authentication, per-user tokens, allowlists, tool policy and audit.
> - Writes go through an approval queue; code executes the approved arguments.
> - Computer use is for portal-only systems, sandboxed, read-only where possible, with screen content treated as untrusted.
> - The platform decides the runtime: Managed Agents on the Claude API and Claude Platform on AWS only; your own loop on Bedrock and Vertex.
