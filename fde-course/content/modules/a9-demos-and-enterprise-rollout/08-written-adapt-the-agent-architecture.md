---
title: "Written: Adapt the Agent Architecture for a University Finance Office"
type: written
minutes: 45
contextFrom: ["a9-demos-and-enterprise-rollout/06-written-90-day-plan-for-5000-staff"]
sections:
  - key: design
    label: 1. The adapted architecture
    prompt: "A diagram (ASCII or Mermaid) plus a numbered flow: which MCP servers, what the gateway enforces, where approvals sit, and what runs the agent loop."
    words: [180, 450]
  - key: platform
    label: 2. Platform and runtime choice
    prompt: "What the university's Google Cloud standard allows and rules out, and what you'd confirm before committing."
    words: [80, 250]
  - key: portal
    label: 3. The funder portal
    prompt: "Whether to use computer use for the grant funder's portal, and how you'd contain it or avoid it."
    words: [80, 250]
  - key: controls
    label: 4. Permissions, approvals and records
    prompt: "Per-user access, which actions need approval and by whom, and how the design supports audit and freedom-of-information requests."
    words: [100, 300]
  - key: evals
    label: 5. Evals and phase 1 scope
    prompt: "The golden set, end-state and trajectory checks, and the narrow phase 1 you'd launch."
    words: [80, 250]
rubric:
  - name: Architecture adapted, not copied
    points: 20
    lookFor: "Keeps the core of the reference architecture (narrow MCP servers per system with read and write tools separated, a gateway, an approval queue, traces) and adapts it to the university's systems: finance ERP, procurement system, grants system, document store and the funder portal. A diagram that matches the numbered flow."
  - name: Platform and runtime correct
    points: 20
    lookFor: "Recognises that on Vertex AI, Managed Agents and the API-side MCP connector aren't available, so the university runs its own loop (Agent SDK or a custom loop) with the MCP client on its side. Messages, tool use and structured outputs are available. Says to recheck current platform availability before committing."
  - name: Computer use judged honestly
    points: 15
    lookFor: "Prefers asking the funder for an API or export first; if computer use is needed, runs it in an isolated sandbox, read-only account, single allowed domain, screen content treated as untrusted. Checks the portal's terms of use. Does not let the agent submit to the funder."
  - name: Permissions, approvals and records
    points: 25
    lookFor: "Per-user tokens so a grants officer only sees their faculty's grants; separation of duties (the person who approves a payment hold isn't the one who raised it); every write through the approval queue with stored arguments; procurement thresholds enforced in code at the gateway; a retained audit log and decision record that can answer a freedom-of-information request or an auditor, with retention set by the university's records policy."
  - name: Evals and narrow phase 1
    points: 20
    lookFor: "A golden set from past cases with known outcomes, including mismatches and missing documents; end-state checks (right hold, right amount, right grant) and trajectory checks (no write before reads, no write without approval). Phase 1 is narrow (one faculty or one supplier category, read-only plus drafted holds) with numbers to beat."
passScore: 70
graderNotes: "Mark down heavily: proposing Managed Agents or the API's MCP connector on Vertex AI as if available (the claude-api skill's platform table lists both as not available on Vertex); letting the agent write to the ERP or submit to the funder without approval; computer use with no containment; no audit or records story for a public body. If the learner's earlier 90-day plan is provided as context, reward consistent use of a single connector or gateway policy, but don't require it. Don't require exact product names for the gateway; it is a pattern. Invented compliance facts (for example, asserting a specific certification for Vertex AI) should lose points under platform; the right move is to confirm."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Design: Use Claude Managed Agents with the MCP connector to connect directly to the ERP, procurement and grants systems, all on Vertex AI. The agent matches invoices and pays or holds them automatically.\nPlatform: Vertex supports everything Claude does.\nPortal: Use computer use to log in and submit claims on the funder portal.\nControls: The agent has an admin account so it can see everything. Logs are kept.\nEvals: We'll test it on a few invoices and go live across the university."
  - label: strong
    expect: [75, 100]
    answer: "Design: Grants officer UI -> agent loop (Agent SDK in the university's GCP project) -> Claude on Vertex AI. All tools go through an MCP gateway the university runs: per-user OAuth tokens, an allowlist, threshold checks, audit log to the records store. Servers: ERP (read; place_hold as a proposed action), procurement (read), grants (read), document store (read), portal worker (read). Writes create pending actions in an approval queue with stored arguments and evidence; a second officer approves; the gateway executes.\nPlatform: Vertex rules out Managed Agents and the API MCP connector, so we run the loop and MCP client ourselves; messages, tool use and structured outputs are available. I'd recheck the platform table and confirm the Claude models and region with the account team before committing.\nPortal: First ask the funder for an export or API. If not, a sandboxed browser with a read-only account and only the portal domain, screen text treated as untrusted, and a check of the portal's terms. It reads award status; it never submits.\nControls: Officers see only their faculty's grants via per-user tokens. Separation of duties on holds. Procurement thresholds in gateway code. Every tool call and decision retained per the records policy so we can answer an FOI request.\nEvals: 300 past cases with known outcomes including missing POs and wrong cost codes. End state: right hold, right amount, right grant; trajectory: no write before reads. Phase 1: Faculty of Engineering, read-only plus drafted holds, 8 weeks, target 90% correct holds against today's manual baseline."
---

Grace's note: *"Same pattern, different customer. A public university wants the back-office agent, and almost every assumption from the Halberd version changes. Show me you can adapt it rather than paste it."*

## The brief

> **Corran University** (fictional) is a public university with a central finance office of 60 people. Henrietta Oduya, Director of Finance Operations (fictional), wants an agent to handle **research-grant expense exceptions**: about 2,500 a month where a supplier invoice doesn't match a purchase order or is charged to the wrong grant.
>
> - **Systems:** a finance ERP (API), a procurement system (API), a grants-management system (API, read-only for now), a document store with contracts and grant terms, and one major research funder's **web portal with no API**, where award budgets and allowed cost categories are listed.
> - **Platform:** the university's IT standard is **Google Cloud**; all model use must go through **Vertex AI** in its own project.
> - **Rules:** public procurement thresholds; separation of duties (the person who raises a hold can't approve it); records must be kept for audit and **freedom-of-information requests**.
> - **Ask:** "Fix the exceptions automatically. Our officers only want to see the hard ones."

## What to write

Five sections, on the right. Start from the reference architecture in lesson 07 and change what the brief forces you to change. If your 90-day plan from lesson 06 is saved, the grader sees it too; you may reuse its connector policy idea.

Things to think about:

1. Which runtime options does Vertex AI leave you? Check the platform table in lesson 07.
2. How do per-user tokens and separation of duties show up in the gateway and the queue?
3. Is there a way to avoid computer use for the funder portal? If not, how do you contain it?
4. What would an auditor or an FOI request need to see, months later?
5. What's the smallest phase 1 that proves value with a number?
