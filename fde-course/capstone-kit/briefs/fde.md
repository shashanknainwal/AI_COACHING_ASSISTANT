# Capstone brief: Forward Deployed Engineer track

**Goal:** an agent working inside a fake "customer system", reached through an MCP server, with evals running in CI against the real model and the deployment pieces a customer's platform team would ask for.

**Time:** about 15 to 24 hours. **Budget:** under $5.

## Build

1. **The customer system.** Invent a small fictional customer (a paragraph: sector, systems, the workflow that hurts). Build their system as data plus functions: a SQLite file or JSON records and at least four operations, one of which writes. Start from `app/customer_system.py`.
2. **The MCP server.** Expose the operations as MCP tools. `app/mcp_server.py` is a hand-written minimal stdio server you may extend; using an official MCP SDK instead is a good decision to record (check its current docs). Writes are refused unless the operator enables them.
3. **The agent.** The tool loop in `app/agent.py` driven through MCP (`app/mcp_client.py`), with an approval step for writes, append-only history, explicit effort, and every `stop_reason` handled.
4. **Evals in CI against the real model.** Golden set of 40+ cases including injection attempts in tool results; `evals/run_evals.py` and `evals/gate.py` in `.github/workflows/evals.yml`, reading the key from repository secrets.
5. **Deployment skeleton.** `infra/Dockerfile` builds and runs the service; `infra/terraform/` describes where it would run (fill in the variables, run `terraform validate`, do not apply unless you want to pay for it).

## Documents

| Deliverable | What it must contain |
|---|---|
| Design doc (2 to 4 pages) | The customer problem, architecture diagram, tools and their permissions, data flows, failure modes and fallbacks, the eval plan and results, cost per task, rollout plan |
| 3-minute demo script | Minute by minute: the problem in one sentence, a happy path, a failure the agent handles (a declined write or an injection), the eval dashboard or gate, the ask. Record it once. |
| Failure log and decision record | As in the engineer brief |
| Cost and latency table | From measured usage, per task, at two configs |

## The deep-dive questions to be ready for

Original practice questions, in the style of a customer-facing technical deep dive: What can the agent do without a human, and why that line? What happens when the customer's API is down for an hour? A tool result contains "ignore your instructions": walk me through what happens. How would you hand this over to the customer's team?
