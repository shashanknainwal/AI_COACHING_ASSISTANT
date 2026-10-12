---
title: "The Agent Stack Map: Who Supplies the Harness, Who Supplies the Deployment"
type: reading
minutes: 16
---

> **By the end of this lesson you will be able to:**
> - Place the four ways to build an agent on Claude on two axes: who writes the loop, and who runs the infrastructure.
> - Choose between a manual loop, the SDK tool runner, Managed Agents and the Claude Agent SDK for a given customer problem.
> - Answer the build-or-buy question a customer will ask, and say what each choice costs you to own.

The Anthropic FDE posting names MCP servers, sub-agents and agent skills in the same breath. Behind all three sits one decision you will make on almost every engagement: how much of the agent do you build, and how much do you let Anthropic run? Get this map right and the rest of the module is detail.

## Two questions separate the options

Every way to build an agent on Claude answers two independent questions.

1. **Who supplies the harness?** The harness is the agent loop plus context management: the code that calls the model, runs the tools it asks for, feeds results back and decides when to stop.
2. **Who supplies the deployment?** The infrastructure the agent runs on: the process, the container where tools execute, the scheduler, the state.

Two tools that feel alike, the SDK tool runner and the Claude Agent SDK, both answer "the SDK supplies the harness, you deploy it." That shared answer is why people confuse them. The second question tells them apart from Managed Agents, which is the only option that supplies both.

## The four approaches

| Approach | You write | Harness | Deployment | Reach for it when |
|---|---|---|---|---|
| **Manual loop** (Claude API) | The `while stop_reason == "tool_use"` loop yourself | You | You | You need control the tool runner doesn't expose: a custom transport, an unusual control flow, or no beta dependency |
| **Tool runner** (`client.beta.messages.tool_runner`) | Just the tool functions | SDK (harness only) | You | A custom-tool agent without hand-writing the loop. The default for most API agents |
| **Managed Agents** (REST, beta) | An agent config plus your tool results | Anthropic | Anthropic (per-session sandbox) | You want Anthropic to run the loop and host the workspace: persisted configs, long sessions, schedules |
| **Claude Agent SDK** (`claude-agent-sdk`) | A prompt plus options | SDK (Claude Code harness, built-in tools) | You | A batteries-included coding or filesystem agent on your own infrastructure |

The tool runner and the Agent SDK are different packages. The tool runner is part of the ordinary Anthropic SDK and loops over tools *you* define, with no built-in tools and no sandbox. The Claude Agent SDK is Claude Code packaged as a library: it ships file, bash and search tools, subagents, permissions and sessions, and you call `query(prompt, options)`. Both leave deployment to you. Managed Agents is the one that also hosts the run.

## "I need control" rarely means the manual loop

The most common mistake is dropping to a hand-written loop for control the tool runner already gives you. Each iteration of the runner hands you the assistant message *before* the tools run, so you can:

- **Gate a destructive action** by inspecting the pending tool call and denying it, or by returning a "user declined" result from inside the tool function.
- **Intercept or rewrite a tool result** before it goes back to the model, for example to attach `cache_control` or redact a field.
- **Retry a truncated turn** with a higher `max_tokens`, and bound the whole thing with `max_iterations`.

Approval gates, logging, result modification and conditional execution do not need a manual loop. Keep the manual loop for a genuinely custom transport, a request shape the SDK can't build, or when you simply don't want the beta dependency.

## Hooks as approval gates

An FDE's agents touch customer systems, so the interesting control is almost always "stop before you do something irreversible." Three of the four approaches give you a place to stand:

- **Tool runner:** gate inside the tool function, or take over the message history before the tool runs.
- **Managed Agents:** set a tool's permission policy. `always_allow` runs it, `always_ask` pauses the session until you send a confirmation, and `auto` lets the server judge each call and run it, deny it, or pause for you. Leave a third-party MCP toolset at its `always_ask` default unless the customer explicitly wants fewer approvals.
- **Manual loop:** gate inline, before you call the function.

The gate belongs wherever the irreversible action is: an email sent, a record deleted, a credit issued.

## Build or buy: the conversation you will actually have

A customer asks "should we build this ourselves or use Managed Agents?" The honest answer turns on ownership, not features.

| If the customer... | Lean toward |
|---|---|
| Has a platform team and wants the loop in their own VPC on their own schedule | Tool runner or manual loop, deployed by them |
| Wants the agent hosted, scheduled, versioned, with a per-session workspace, and no loop code to maintain | Managed Agents |
| Needs a coding or filesystem agent inside their repos | Claude Agent SDK |
| Has one well-specified deliverable that must meet a quality bar | Managed Agents with an outcome and a rubric |

Two caveats shape the recommendation. Managed Agents is in beta, and it is not available on Amazon Bedrock or Google Vertex AI, so a customer committed to one of those clouds for data-residency reasons builds the harness themselves with the API and the tool runner. And the simplest tier that meets the need wins: most "agent" requests are really a single call or a short workflow, and only open-ended, model-driven tool use justifies an agent at all.

## What "buy" still leaves you owning

Choosing Managed Agents does not end your work. You still write the agent's system prompt and tool surface, decide the permission policies, wire the credentials through vaults rather than into the sandbox, and reconcile every action in the task against a configured tool or MCP server before the first run. The platform runs the loop; the judgement is still yours.

> **Key takeaways**
> - Two questions place every option: who writes the harness, and who runs the deployment.
> - The tool runner and the Claude Agent SDK both supply a harness only; Managed Agents supplies harness and deployment; the manual loop supplies neither.
> - Reach for the manual loop rarely: the tool runner's per-turn hooks already cover approval, logging, interception and retries.
> - Build-or-buy turns on who owns the infrastructure and the schedule, and on platform limits (Managed Agents is beta and not on Bedrock or Vertex), not on a feature checklist.
> - Whichever you choose, you still own the prompt, the tool surface, the permissions and the credentials.
