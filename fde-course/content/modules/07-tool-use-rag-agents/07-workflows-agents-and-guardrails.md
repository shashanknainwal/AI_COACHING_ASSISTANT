---
title: "Workflows vs Agents, Guardrails and MCP"
type: reading
minutes: 18
---

> **By the end of this lesson you will be able to:**
> - Choose between a single call, a workflow, and an agent for a customer's problem
> - Name the common workflow patterns and when each fits
> - Layer guardrails so a mistaken or manipulated agent can't cause serious harm
> - Explain what the Model Context Protocol (MCP) is and when an FDE would use it

## The simplest thing that works

Customers often ask for "an agent" when what they need is one good prompt. As the FDE, your job is to match the architecture to the problem. There are three levels, in order of complexity:

| Level | What it is | Example at Brightway |
|---|---|---|
| **Single call** | One request, maybe with retrieved context or structured output | Classify a support email; answer a policy question from the help center |
| **Workflow** | Your code decides the steps; Claude handles some of them | Look up the order, track the shipment, then ask Claude to write the reply |
| **Agent** | Claude decides the steps in a loop, using tools | "Sort out whatever is wrong with my order", where the steps aren't known in advance |

Each step up adds cost, latency, unpredictability, and testing effort. Move up only when the simpler level can't do the job.

**Rule of thumb:** if you can write the steps as a flowchart, write them as code (a workflow). Use an agent when the path really depends on what the tools return, and the number of possible paths is too large to code by hand.

## Workflow patterns

These patterns cover most production LLM features:

- **Prompt chaining:** split a task into fixed steps, each a call whose output feeds the next (extract facts → draft reply → check tone). Add code checks between steps.
- **Routing:** classify the input, then send it to a specialized prompt, model, or team. You built this in Module 6.
- **Parallelization:** run independent calls at the same time (summarize 20 documents at once), or run the same call several times and vote, for higher confidence on important decisions.
- **Orchestrator-workers:** one call breaks a task into subtasks, workers handle them, and a final step combines the results. Useful when the subtasks can't be predicted in advance.
- **Evaluator-optimizer:** one call drafts, another critiques against clear criteria, and the first revises. Works when you can state what "good" means.

A useful hybrid: a **workflow with an agent inside one step**. The overall process (receive ticket → resolve → send survey) is fixed code, and only the "resolve" step is an agent.

## Guardrails: defense in depth

Assume that, sooner or later, the agent will do the wrong thing: a misunderstanding, a prompt injection hidden in an email, a bug in a tool. Guardrails limit the damage. Layer them, so that no single failure is enough:

1. **Least privilege.** Give the agent only the tools it needs, with the narrowest permissions. A support agent doesn't need `delete_customer`. Use read-only database credentials for read tools.
2. **Validate inside tools.** Schemas check shape; your code checks meaning: amount limits, allowed states ("can't cancel a shipped order"), and **authorization** ("does this order belong to the signed-in customer?").
3. **Hard limits in code.** Maximum credit per call, per customer per day, emails per hour. The model can't talk its way past an `if` statement.
4. **Human approval for risky actions.** Above a threshold, or for irreversible actions, pause and ask a person (next exercise). Design approvals to **fail closed**: if the approval system is down or the answer is unclear, the action doesn't happen.
5. **Bounded loops.** Maximum steps, tokens, and time (lesson 3).
6. **Audit everything.** Log every tool call, its input, who approved it, and the result. Audit logs are how you investigate incidents and how your customer's compliance team learns to trust the system.
7. **Undo paths.** Prefer reversible actions (a credit you can claw back, a draft instead of a sent email). Where possible, let the agent prepare actions and let people commit them.

When writing approval requests, remember that reviewers are busy. Show them a **one-line summary with the facts needed to decide** (who, how much, why, current state), not raw JSON. A reviewer who can't understand a request will either rubber-stamp it or block it.

## MCP: connecting agents to systems

Every tool you've written so far lives inside your application. The **Model Context Protocol (MCP)** is an open standard for packaging tools (and data sources) as **servers** that any MCP-compatible application can connect to.

- An **MCP server** exposes tools like `lookup_order` over a standard protocol. It can run locally or as a remote service.
- An **MCP client** (Claude Code, the Claude apps, the Claude Agent SDK, or your own application) discovers those tools and lets Claude call them.
- The Messages API can connect to remote MCP servers directly through its MCP connector (a beta feature), so Claude can use a server's tools without you writing the tool-calling code.

Why an FDE cares: if Brightway exposes its order system as an MCP server once, every Claude-based tool they use (the support assistant, an internal ops agent, an analyst's Claude app) can use it, with permissions managed in one place. When a customer says "we want Claude connected to our systems," MCP is often the shape of the deliverable.

The same rules apply to MCP tools as to your own: least privilege, validation inside the server, approval for writes, and treating tool output as untrusted data.

## Reading an agent request like an FDE

When a customer asks for an agent, ask:

1. **What are the actual tasks?** Collect 20 real examples. Often 80% follow two or three fixed paths, which become workflows.
2. **What actions are involved, and which are risky?** List every write action, its worst case, and who must approve it.
3. **How will we know it works?** Agree on an evaluation set and success measures before building (Module 8).
4. **What happens when it fails?** Define the hand-off to a human and the undo path.

> **Key takeaways**
> - Use the simplest level that works: a single call, then a workflow, and an agent only when the steps can't be predicted.
> - Workflow patterns (chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer) cover most features.
> - Layer guardrails: least privilege, validation and hard limits in tools, fail-closed human approval, bounded loops, audit logs, undo paths.
> - MCP packages tools as reusable servers that any MCP client can use; the same safety rules apply.
