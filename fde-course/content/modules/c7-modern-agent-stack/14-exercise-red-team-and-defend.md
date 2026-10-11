---
title: "Exercise: Red-Team an Agent, Then Defend It"
type: exercise
minutes: 45
hints:
  - "Build the measurement first. `run_attack_set(defenses, tools)` runs every attack with `run_agent`, counts the ones `attack_succeeded` returns true for, and checks `keeps_utility` on each. A number before and after is the whole point."
  - "Least privilege is the biggest lever. The task only reads a shipment and a doc, so `send_email` and `issue_credit` never belong in the agent's tool set. A tool the agent doesn't hold can't be called, however convincing the injected text."
  - "The output filter is an allowlist, not a blocklist. Keep links whose host is in `ALLOWED_LINK_HOSTS` and drop the rest, so the real tracking link survives and an exfiltration link doesn't."
  - "Data marking fences untrusted content so plainly planted instructions are ignored, but a stronger attack ignores the fence and a poisoned tool description isn't output at all. That's why one layer is never enough: map each attack to the layer that actually stops it."
---

Cindervale's status agent looks up a shipment and its handling docs and answers staff questions. Rhea's security lead ran a red-team. "Four planted instructions, four wins. One made it email a record to an outside address. One slipped an off-domain link into the answer. One rode in on a third-party tool's own description. I want the attack success rate measured, driven to zero, and the product still working, plus a one-line reason for each attack so we know which control carries it."

This is prompt injection by a third party: the hostile text arrives in a tool's output, a retrieved document, or a tool's description, not from the user. The attacks here are reduced to abstract markers (`<<TRY goal=... arg=...>>`) so the exercise measures defences rather than carrying working attack text. `ATTACKS`, `ALL_TOOLS`, `TASK_TOOLS`, `ALLOWED_LINK_HOSTS`, `run_agent(attack, defenses, tools)`, `attack_succeeded(attack, result)` and `keeps_utility(result)` are given. The three defences `run_agent` understands are `"data_marking"`, `"url_filter"` and `"tool_allowlist"` (expressed by the tool list you pass).

## Your task

**1. `run_attack_set(defenses, tools)`** returns `{"success_rate", "successes": [attack ids], "utility_ok"}` over all four attacks.

**2. `least_privilege_tools()`** returns the smallest tool set the task needs.

**3. `BASELINE_DEFENSES`, `HARDENED_DEFENSES`, `HARDENED_TOOLS`.** The baseline is no defences and every tool. The hardened configuration must drive the attack success rate to zero while `utility_ok` stays true (the answer still reports the status and keeps the real tracking link).

**4. `DEFENSE_FOR`** maps each attack id to one defence (`"data_marking"`, `"url_filter"` or `"tool_allowlist"`) that stops it on its own.

## Example

```text
Baseline attack success rate: 100%  (got through: ['A1', 'A2', 'A3', 'A4'])
Hardened attack success rate: 0%  utility kept: True
Tools before: ['shipments_get', 'docs_search', 'send_email', 'issue_credit'] -> after: ['shipments_get', 'docs_search']
```

## Why it's built this way

- **Measure before and after, on a fixed set.** "We added spotlighting" means nothing without a number. A frozen attack set and an attack-success-rate gate make injection defence an eval like any other, and the utility check stops a defence that works by breaking the product.
- **Least privilege does the heavy lifting.** Spotlighting and data marking lower the odds the model obeys injected text; removing the dangerous tool removes the capability entirely. Give the agent only the tools its task needs, and gate anything irreversible behind human approval.
- **Filter the output channel.** Exfiltration often rides out through a link or image URL the model is tricked into emitting. An allowlist on output URLs closes that channel without blocking legitimate links.
- **Trust boundaries include tool descriptions.** A third-party MCP server's tool description is model-visible text you don't control (tool poisoning). Treat a connected server as part of your trust boundary, and pin or review its tool definitions.
- **Defence in depth, because no layer is complete.** Stronger injections ignore a data-marking fence, and a poisoned description never passes through the output filter. Layer the controls and attribute each attack to the one that carries it.

The simulated model here is predictably gullible so the numbers are clean. A real model is less so, and less predictable; the capstone kit runs this same attack set against the real API.

In a debrief, expect: "An injected instruction in a retrieved document tells your agent to email customer data out. Name every layer that has to fail for that to work."
