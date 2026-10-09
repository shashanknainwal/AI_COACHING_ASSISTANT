---
title: "Workflows vs Agents, Guardrails and MCP"
type: reading
minutes: 3
---

> **By the end of this lesson you will be able to:**
> - Choose between a single call, a workflow and an agent
> - Layer guardrails so a mistaken or manipulated agent can't cause serious harm
> - Explain what MCP is and when an FDE uses it

Jordan's next message: *"Can the agent just handle refunds end to end?"* Before you answer, you need two things: the simplest architecture that does the job, and the guardrails that keep a wrong answer from costing Brightway money.

## The simplest thing that works

| Level | What it is | Example at Brightway |
|---|---|---|
| **Single call** | One request, maybe with retrieved context or structured output | Classify a support email; answer a policy question |
| **Workflow** | Your code decides the steps; Claude handles some | Look up the order, track the shipment, then Claude writes the reply |
| **Agent** | Claude decides the steps in a loop | "Sort out whatever is wrong with my order" |

Each step up adds cost, latency and testing effort. **If you can draw it as a flowchart, write it as code.**

Common workflow patterns:

| Pattern | Use when |
|---|---|
| Prompt chaining | Fixed steps, with code checks between them |
| Routing | Different inputs need different prompts, models or teams (Module 6) |
| Parallelization | Independent calls at once, or several runs and a vote |
| Orchestrator-workers | Subtasks can't be predicted in advance |
| Evaluator-optimizer | You can state what "good" means, so one call critiques another |

A useful hybrid: a fixed workflow (receive ticket → resolve → survey) with an agent inside only the "resolve" step.

## Guardrails: defense in depth

Assume the agent will eventually do the wrong thing (a misunderstanding, a prompt injection, a tool bug). Layer guardrails:

1. **Least privilege.** Only the tools it needs; read-only credentials for read tools. A support agent doesn't need `delete_customer`.
2. **Validate inside tools.** Amount limits, allowed states ("can't refund an order twice"), and **authorization**.
3. **Hard limits in code.** Max per call, per customer per day. The model can't talk its way past an `if`.
4. **Human approval for risky actions,** designed to **fail closed**: if the approval system is down or the answer is unclear, the action doesn't happen.
5. **Bounded loops** (lesson 3).
6. **Audit everything:** call, input, approver, result.
7. **Undo paths.** Prefer reversible actions (store credit you can claw back, a draft instead of a sent email).

Write approval requests for busy reviewers: one line with who, how much, why and current state, not raw JSON. A reviewer who can't understand a request rubber-stamps it or blocks it.

## MCP: connecting agents to systems

The **Model Context Protocol (MCP)** is an open standard for packaging tools and data sources as **servers** that any MCP client (Claude Code, the Claude apps, the Claude Agent SDK, your own app) can use. The Messages API can also connect to remote MCP servers directly through its MCP connector (beta).

Expose Brightway's order system as an MCP server once and every Claude-based tool they use can call it, with permissions in one place. The same safety rules apply.

## When a customer asks for an agent

1. Collect 20 real examples. Often 80% follow two or three fixed paths: workflows.
2. List every write action, its worst case, and who must approve it.
3. Agree an eval set and success measures before building (Module 8).
4. Define the hand-off to a human and the undo path.

> **Key takeaways**
> - Single call, then workflow; an agent only when the steps can't be predicted.
> - Layer guardrails: least privilege, validation and hard limits in tools, fail-closed approval, bounded loops, audit logs, undo paths.
> - MCP packages tools as reusable servers; the same safety rules apply.
