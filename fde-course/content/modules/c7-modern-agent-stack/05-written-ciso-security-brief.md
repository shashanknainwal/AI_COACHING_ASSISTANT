---
title: "Write It: The CISO Security Brief for an MCP Server"
type: written
minutes: 40
contextFrom: ["c7-modern-agent-stack/04-exercise-secure-the-mcp-server"]
sections:
  - key: summary
    label: What the server is and what it exposes
    prompt: "In plain language for a CISO: what the shipments MCP server does, which tools it exposes, and the read and write tiers. Name the one tool that can lose money or data."
    words: [60, 160]
  - key: authz
    label: Authentication and authorization
    prompt: "How a caller is authenticated and authorized: tokens, the audience check, per-tool scopes, and least privilege at both the server and the client. What a read-only caller can and cannot do."
    words: [90, 220]
  - key: injection
    label: Prompt injection and tool poisoning
    prompt: "The third-party injection risks for an agent that uses this server (injected instructions in tool output or retrieved docs, exfiltration, a poisoned tool description) and the layered defences you rely on."
    words: [90, 220]
  - key: audit
    label: Audit, data handling and platform
    prompt: "What every call records, how customer data is kept out of logs, where credentials live, and any platform limits that affect the design (for example the MCP connector's availability)."
    words: [80, 200]
  - key: residual
    label: Residual risk and what you would not ship yet
    prompt: "As you would say it to the CISO: the top residual risk, what still needs a human, and the one control you would add next."
    words: [40, 120]
rubric:
  - name: Accurate, concrete description
    points: 15
    lookFor: "Describes the server and its tools correctly, names the read and write tiers, and identifies the destructive tool (cancel) as the one needing the tightest control. No hand-waving about what it does."
  - name: Authorization and least privilege
    points: 25
    lookFor: "Signature-checked tokens, an audience check so a token for another service is rejected, per-tool OAuth scopes (read, write, admin), and least privilege enforced at two layers: the server rejects out-of-scope calls and the connector exposes only the tools an agent needs. States that a read-only caller sees and can call only the read tools."
  - name: Injection defence in depth
    points: 25
    lookFor: "Treats tool output, retrieved docs and third-party tool descriptions as untrusted. Names layered defences: data marking or spotlighting, an output URL allowlist, least-privilege tool allowlists so a dangerous tool can't be called, and human approval on irreversible actions. Says that no single layer is enough and measures attack success rate on a fixed set. Flags tool poisoning from third-party MCP servers as a trust-boundary issue."
  - name: Audit, data handling and platform honesty
    points: 20
    lookFor: "Every decision (allowed, denied, invalid) is logged with who, which tool and a digest, but not raw arguments, because notes can carry personal data. Credentials live in a vault or secret store and never enter the sandbox. Names a real platform limit (the MCP connector is beta and not on Bedrock or Vertex) and says what must be confirmed in current docs rather than stated from memory."
  - name: Clear, honest residual-risk framing
    points: 15
    lookFor: "Leads with the top residual risk in plain words a CISO can act on, says what still needs a human, and names one concrete next control. Doesn't claim the system is perfectly safe."
passScore: 70
graderNotes: |
  This is the brief for the MCP server the learner secured in the previous exercise. The learner's saved answer there is available as context; reward consistency with the scopes and tiers they chose.
  Mark down: treating annotations as a security control (they are hints only); logging raw tool arguments (personal data leak); relying on prompt-injection defence from a single layer; claiming the MCP connector works everywhere (it is not on Bedrock or Vertex); forgetting the audience check so a token minted elsewhere would work; putting credentials in the sandbox rather than a vault; stating platform or product facts with false certainty. Cap 'Authorization and least privilege' at 12 if scopes are mentioned but least privilege is enforced at only one layer. Cap 'Injection defence in depth' at 12 if only one defence is named or attack success rate is never measured. Do not require the learner to name specific beta header strings; reward naming the limit and saying to confirm it in current docs. Reward a brief that is honest about what it would not ship yet over one that claims to have solved injection.
anchors:
  - label: weak
    expect: [0, 45]
    answer: "The MCP server exposes shipment tools to Claude. It is secure because we use OAuth and the tools have annotations marking the dangerous ones as destructive, so Claude knows not to misuse them. We validate inputs. Prompt injection is handled by telling the model in the system prompt to ignore instructions in documents. Everything is logged for audit. It works on the Claude API and on Bedrock and Vertex. There is no significant residual risk."
  - label: strong
    expect: [75, 100]
    answer: "The server fronts Cindervale's shipment system: read tools (get, search), write tools (add_note, reroute) and one destructive tool (cancel), which carries the tightest scope. Callers present an OAuth access token; we check the signature, that it hasn't expired, and that its audience is this server, so a token minted for another internal service is rejected. Each tool maps to a scope (read, write, admin). Least privilege runs at two layers: the server denies any out-of-scope call, and the Messages API connector is configured in allowlist mode to expose only the read tools to the first agent, so a read-only dispatch bot can see and call nothing else. Annotations (readOnly, destructive) drive the client's confirmation UX only; permissions are enforced in code. For injection we treat every tool output, retrieved document and third-party tool description as untrusted: data marking on retrieved content, an allowlist filter on any URL in the output, least-privilege tool sets so send or cancel aren't even present on read agents, and human approval on cancel. We measure attack success rate on a fixed red-team set before and after, because no single layer is complete: a poisoned tool description, for instance, never passes the output filter and is stopped only by not holding the tool. Every call, allowed or denied, is logged with the caller, the tool, the decision and a hash of the arguments, never the raw arguments, because notes can contain personal data; real credentials live in a vault and are injected at egress, never in the sandbox. Platform note: the MCP connector is beta and not on Bedrock or Vertex, so a customer there uses their own MCP client; I would confirm the current beta status in the docs. Top residual risk: a valid-but-compromised write token. It still needs a human on cancel, and the next control I'd add is short-lived tokens with per-tool rate limits and anomaly alerts on the audit stream."
---

In the last exercise you secured Cindervale's shipments MCP server: scopes, validation, an audit log and an allowlisted connector. Now write the one-page brief Rhea's CISO asked for before it goes to production. The audience is a security leader who will not read your code but will decide whether this ships.

Rhea Petrakis is a fictional platform-engineering lead at Cindervale Freight, a fictional company. Write for her CISO.

## What to cover

Work through the five sections. Be specific and honest. A CISO trusts a brief that names its own residual risk more than one that claims everything is handled. Your answer from the secure-the-server exercise is available to the grader as context, so keep your scopes and tiers consistent with what you built.

Ground every claim in how the server actually works. Where a fact depends on a platform or a product feature, say so and say you would confirm it in current documentation rather than asserting it from memory.
