---
title: "Module Quiz: The Modern Agent Stack"
type: quiz
minutes: 15
questions:
  - q: "Which approach supplies both the agent harness and a managed deployment?"
    options:
      - "The SDK tool runner"
      - "Managed Agents"
      - "The Claude Agent SDK"
      - "A hand-written manual loop"
    answer: 1
    explain: "Managed Agents runs the loop and hosts a per-session sandbox. The tool runner and the Agent SDK supply a harness you deploy yourself, and the manual loop supplies neither."
  - q: "An MCP tool call asks for a shipment ID that doesn't exist. How should the server respond?"
    options:
      - "A JSON-RPC error with code -32601"
      - "A JSON-RPC error with code -32700"
      - "No response, like a notification"
      - "A result with isError true and a message"
    answer: 3
    explain: "A problem while the tool runs is a tool error returned inside the result, so the model can read it and recover. JSON-RPC errors are for protocol problems such as unknown methods."
  - q: "What happens if you send mcp_servers to the Messages API without a matching mcp_toolset entry?"
    options:
      - "The request is rejected as invalid"
      - "All the server's tools load by default"
      - "Only read-only tools are exposed"
      - "The server connects without auth"
    answer: 0
    explain: "The MCP connector needs both halves: the server definition and an mcp_toolset that references it by name. Without the toolset the request fails validation."
  - q: "Why aren't MCP tool annotations such as destructiveHint a security control?"
    options:
      - "Clients ignore them completely"
      - "They only apply to stdio servers"
      - "A server can claim any hint it likes"
      - "They expire after each session"
    answer: 2
    explain: "Annotations are hints a server declares about itself. Use them for UX such as confirmations, and enforce permissions in code."
  - q: "A customer runs Claude only through Amazon Bedrock. Which feature can you still use there?"
    options:
      - "The Messages API MCP connector"
      - "Tool use with the SDK tool runner"
      - "Managed Agents sessions"
      - "Agent Skills on the Messages API"
    answer: 1
    explain: "Core tool use works on every platform. The MCP connector, Managed Agents and Messages API Skills are not available on Bedrock."
  - q: "Which model is the current cheap tier for bulk extraction workers?"
    options:
      - "Claude Haiku 5.5"
      - "Claude Haiku 4.5"
      - "Claude Fable 5.1"
      - "Claude Sonnet 5"
    answer: 0
    explain: "Haiku 5.5 costs $0.10 input and $0.50 output per million tokens for prompts up to 100K tokens. Haiku 4.5 is legacy, Fable 5.1 is the most expensive tier, and Sonnet 5 is the previous Sonnet."
  - q: "Your Haiku 5.5 worker cost estimate counts only the visible output. What is it missing?"
    options:
      - "Cache writes, which Haiku always bills"
      - "A per-request platform surcharge"
      - "Tool schemas, which are billed as output"
      - "Thinking, billed as output at medium effort"
    answer: 3
    explain: "Current models think by default and thinking is billed as output. Haiku 5.5 defaults to medium effort, so set effort explicitly or count the thinking."
  - q: "In a Skill, where should the description of when to use it go?"
    options:
      - "At the top of the SKILL.md body"
      - "In a reference file named when.md"
      - "In the frontmatter description field"
      - "In a comment inside the bundled script"
    answer: 2
    explain: "Only the name and description are always in context. The body loads after the skill triggers, so trigger guidance in the body is never read when it matters."
  - q: "On Opus 5.5, which change keeps later thinking blocks valid mid-session?"
    options:
      - "Appending a role system message"
      - "Editing the top-level system prompt"
      - "Trimming old tool results client-side"
      - "Removing issue_credit from tools"
    answer: 0
    explain: "Appended system messages keep history append-only. Editing the system prompt, trimming earlier turns or changing the tools array invalidates every later thinking block."
  - q: "What is the critical rule when you enable server-side compaction?"
    options:
      - "Send the compaction beta only on turn one"
      - "Keep thinking display set to summarized"
      - "Delete the compaction block after reading"
      - "Append the full response.content each turn"
    answer: 3
    explain: "The compaction block in the response replaces earlier history on the next request. Appending only the text silently loses the compaction state."
  - q: "In Claude Code, which hook can block a tool call before it runs?"
    options:
      - "PostToolUse"
      - "PreToolUse"
      - "SessionStart"
      - "PostCompact"
    answer: 1
    explain: "A PreToolUse hook sees the pending call and can deny it, which makes it the place for deterministic customer rules."
  - q: "In the red-team exercise, why did no single defence reach zero attack success?"
    options:
      - "The simulated model ignored every defence"
      - "Each defence needed a different model"
      - "Each layer covers some attack paths only"
      - "Attack success rate can't be measured"
    answer: 2
    explain: "Data marking misses strong injections and poisoned tool descriptions, the URL filter covers only the output channel, and least privilege covers only tools. Layering them closes the gaps."
---

Twelve questions on the module. You need ten correct to pass.
