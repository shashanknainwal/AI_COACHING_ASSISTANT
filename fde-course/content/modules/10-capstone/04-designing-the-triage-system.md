---
title: "Designing the Triage System"
type: reading
minutes: 15
---

> **By the end of this lesson you will be able to:**
> - Justify an architecture choice (workflow or agent) for a real customer problem
> - Turn customer rules into tools, guardrails and approval gates
> - Plan the evaluation and production pieces before building
> - Write a one-page design that the customer's engineers and security team can review

## Start from the work, not the technology

You have clean data and a scoped plan. Before writing the agent, write down what a good coordinator does today for each exception type (Marcus walked you through it):

| Exception | What a good coordinator does |
|---|---|
| Delay | Tell the customer the new ETA. For platinum customers, also open a ticket so someone watches it. |
| Damage | Open a claim ticket, tell the customer the claim is open. |
| Customs hold | Open a ticket for the broker team, tell the customer. |
| Address issue | Ask the customer for the correct address. |
| Missed pickup | Book a backup carrier (with approval), tell the customer. |

## Workflow or agent?

Module 7's rule: if you can draw it as a flowchart, write it as code. Much of this table **is** a flowchart. So why does the capstone build an agent?

- **The inputs are messy text.** Carrier details vary ("Weather closure on I-80", "Driver hours limit reached"), and customer messages must be written from them.
- **The paths depend on what tools return:** an unknown shipment, a delivered shipment, a declined reroute, a message blocked by the guardrail that must be rewritten.
- **NorthStar wants to add exception types later** without a developer rewriting the flow.

A defensible middle ground, worth presenting as an option: **a workflow with Claude inside each step** (code decides the steps by exception type; Claude writes messages and summaries). It's cheaper and easier to test. The agent wins if the paths keep multiplying. Either way, the evaluation, guardrails and approval gates are the same. In a real engagement, you'd show both options with their trade-offs and let the sponsor decide.

## Rules become code

Every hard rule from discovery should be enforced where the model can't get around it:

| Customer rule | Where it lives |
|---|---|
| Never promise refunds or credits | `notify_customer` blocks messages containing those words (a guardrail in the tool), **plus** the prompt instruction |
| Reroutes need a coordinator's approval | `guarded_execute` calls the approver; fail closed |
| Audit every automated action | Every tool call appends an audit entry with approval status |
| Platinum customers get P1 | The prompt states it; the **eval** checks it (P1 recall must be 100%) |
| Customer data stays in their cloud | Deployment through their AWS account; logs contain metadata, not messages |

Notice that some rules are enforced in code and others are measured by the eval. "Never promise a refund" can be checked mechanically, so it's code. "Choose the right priority" is a judgment, so it's measured, and the release gate blocks shipping if it's wrong for platinum customers.

## The tools

Small, specific tools with clear descriptions (Module 7):

- `get_shipment`: one call returns the shipment, customer tier, SLA and latest event, because fewer round trips mean lower cost and latency.
- `notify_customer`: the only way to contact customers, with the guardrail inside.
- `create_ops_ticket`: hands work to people.
- `reroute_shipment`: the only expensive action, behind approval.
- `record_decision`: a structured final decision, so evals and reports read a field instead of parsing prose.

## Plan the evaluation before building

Write the eval plan into the design:

- **Cases:** every exception type, every tier, plus "nothing to do" (delivered) and "unknown shipment" cases. Labels from the ops lead.
- **Checks:** action, priority, notified when required, no forbidden actions, a decision recorded.
- **Gates:** pass rate ≥ 90%, P1 recall = 100%, average cost ≤ $0.05 per exception.
- **Later:** a larger set from real traffic, repeated trials for flakiness (pass^k), and sampled review of customer messages by a coordinator.

## Production pieces

From Module 9, decided up front:

- **Config:** model, limits and the kill-switch flag in environment variables, validated at startup.
- **Logging:** each run logs the shipment ID, decision, tools called, tokens, cost and latency, and **not** the customer message text.
- **Fallback:** if the API fails or the circuit breaker is open, the exception goes to the coordinators' queue as today. Nothing is lost.
- **Rollout:** shadow mode first (the agent decides, coordinators act, you compare), then a pilot in Chicago, then expand.

## The one-page design doc

Bring it together for NorthStar's engineers and security team:

1. **Problem and goals:** baseline, targets, scope.
2. **Architecture:** a diagram of the data flow, workflow vs agent and why.
3. **Tools and permissions:** each tool, what it can touch, which need approval.
4. **Guardrails:** each customer rule and where it's enforced.
5. **Evaluation:** cases, checks, gates.
6. **Operations:** config, logging, fallback, rollout, rollback.
7. **Risks and open questions.**

> **Key takeaways**
> - Start from what a good coordinator does; choose workflow vs agent by how much the paths depend on tool results, and present the trade-off.
> - Enforce mechanical rules in tools and gates; measure judgment calls with evals and block releases on critical slices.
> - Keep tools few and specific; make the final decision structured.
> - Plan evaluation and production (config, logging, fallback, staged rollout) in the design, before building.
