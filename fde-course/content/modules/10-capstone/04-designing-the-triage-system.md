---
title: "Designing the Triage System"
type: reading
minutes: 3
---

> **By the end of this lesson you will be able to:**
> - Justify a workflow or agent design for a real customer problem
> - Turn customer rules into tools, guardrails and approval gates
> - Plan evaluation and production pieces before building

Marcus says never promise a refund and reroutes need a person's yes; Sam says audit everything and keep data in NorthStar's cloud. Your design must make those rules impossible to break.

## Start from the work

| Exception | What a good coordinator does |
|---|---|
| Delay | Send the new ETA; for platinum, also open a watch ticket |
| Damage | Open a claim ticket, tell the customer |
| Customs hold | Ticket for the broker team, tell the customer |
| Address issue | Ask the customer for the correct address |
| Missed pickup | Book a backup carrier (with approval), tell the customer |

## Workflow or agent?

Module 7's rule: if you can draw it as a flowchart, write it as code, and much of this table is one. The capstone builds an agent because inputs are messy text, paths depend on tool results (unknown shipment, already delivered, declined reroute, blocked message), and NorthStar wants to add types without a rewrite.

The middle ground: **a workflow with Claude inside each step**, cheaper and easier to test; the agent wins if paths keep multiplying. Guardrails and evals are the same either way. Present both and let the sponsor choose.

## Rules become code

| Customer rule | Where it lives |
|---|---|
| Never promise refunds or credits | `notify_customer` blocks such messages (guardrail in the tool), **plus** the prompt |
| Reroutes need approval | `guarded_execute` calls the approver; fail closed |
| Audit every automated action | Every tool call appends an audit entry with approval status |
| Platinum customers get P1 | The prompt states it; the **eval** checks it (P1 recall must be 100%) |
| Data stays in their cloud | Deploy in their AWS account; logs hold metadata, not messages |

Mechanical rules go in code; judgment calls are measured by the eval, and the gate blocks shipping if platinum cases fail.

## The tools

`get_shipment` (shipment, tier, SLA, latest event in one call), `notify_customer` (the only path to customers, guardrail inside), `create_ops_ticket`, `reroute_shipment` (behind approval) and `record_decision` (structured, so evals read a field, not prose).

## Eval and production plan

- **Cases:** every exception type and tier, plus "nothing to do" and "unknown shipment"; labels from the ops lead.
- **Checks:** action, priority, notified when required, no forbidden actions, decision recorded.
- **Gates:** pass rate ≥ 90%, P1 recall = 100%, average cost ≤ $0.05 per exception.
- **Later:** real-traffic cases, repeated trials (pass^k), sampled message review.
- **Config** (model, limits, kill switch) in env vars, validated at startup.
- **Logging:** shipment ID, decision, tools, tokens, cost, latency, **not** message text.
- **Fallback:** if the API fails or the breaker opens, exceptions go to the coordinators' queue as today.
- **Rollout:** shadow mode, then a Chicago pilot, then expand.

## The one-page design doc

Problem and goals · architecture and why · tools and permissions · guardrails · evaluation · operations · risks and open questions.

> **Key takeaways**
> - Start from what a good coordinator does; choose workflow or agent by how much paths depend on tool results, and present the trade-off.
> - Enforce mechanical rules in tools; measure judgment with evals and gate on critical slices.
> - Plan evals and production before building.
