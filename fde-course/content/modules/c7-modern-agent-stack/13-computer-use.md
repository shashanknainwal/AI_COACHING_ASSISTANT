---
title: "Computer Use: When GUI Automation Beats an API"
type: reading
minutes: 12
---

> **By the end of this lesson you will be able to:**
> - Decide when computer use is the right tool and when an API or MCP server is better.
> - Describe the screenshot loop, its cost and latency per step, and how to sandbox it.
> - Explain on-screen prompt injection and how to contain it.

Computer use lets Claude operate a desktop: it looks at screenshots and asks for mouse and keyboard actions. It is a client-side tool: your application provides the environment and executes the actions; Anthropic processes the screenshots and requests but does not host your environment.

## When GUI automation is the right call

Use computer use when there is no better interface: a legacy insurance portal with no API, a vendor desktop app, a workflow that spans several GUIs. If the system has an API, wrap it as a tool or an MCP server instead. That is faster, cheaper, more reliable and easier to permission. Computer use is the fallback for the long tail, not the default.

## The screenshot loop

Each step is a round trip: send a screenshot, Claude returns one or more actions (click, type, scroll, zoom, take another screenshot), you execute them and return results. Every screenshot is image input, every step adds latency, and a task of 30 steps is 30 model turns. Before proposing it, estimate steps per task times tokens per step, with thinking counted as output and `effort` set explicitly, and compare it against a person doing the same task.

## Tool versions

The current request shape is the computer toolset, `computer_toolset_20260801`: one `tools` entry with no `name`, whose member tools (`screenshot`, `left_click`, `type`, `zoom` and so on) come back as tool calls carrying `toolset_name: "computer"`. On the Claude API and Google Cloud, Opus 5.5 and Sonnet 5.5 accept only the toolset; the earlier `computer_20251124` version still works on the models and platforms that offer it, such as Amazon Bedrock. Check the computer-use docs for the current member list.

## Sandbox it

Run the environment in an isolated VM or container with no access to anything the task doesn't need: no personal accounts, no saved credentials beyond the task's, network limited to the target application. Gate irreversible actions (submit, pay, delete) behind human confirmation, and log every action with its screenshot.

## On-screen injection

Anything on screen is input the model reads: a web page, an email, a document. Text there can contain instructions aimed at the agent. Treat the screen as untrusted, keep the agent's privileges to the task, restrict which sites and apps it can reach, and require confirmation before actions with consequences.

> **Key takeaways**
> - Use computer use only when no API exists; wrap real APIs as tools or MCP servers instead.
> - Every step is a screenshot round trip: estimate steps, tokens and thinking before you propose it.
> - Opus 5.5 and Sonnet 5.5 use `computer_toolset_20260801` on the Claude API and Google Cloud.
> - Sandbox the environment, limit its network, and confirm irreversible actions.
> - Treat everything on screen as untrusted input.
