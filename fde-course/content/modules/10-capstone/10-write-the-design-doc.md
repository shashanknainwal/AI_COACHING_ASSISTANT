---
title: "Write the One-Page Design Doc"
type: written
minutes: 45
diagram: true
sections:
  - key: problem
    label: 1. Problem and goals
    prompt: "The problem in NorthStar's terms, the baseline numbers, and the targets Dana agreed (SLA breaches, platinum breaches, coordinator time). Say what is out of scope for these 20 days and why."
    words: [80, 200]
  - key: architecture
    label: 2. Architecture and why
    prompt: "The components and how an exception flows through them, from carrier message to customer email or ops ticket. Why an agent rather than a workflow with Claude in each step (or the reverse), and what would change your mind. Use the diagram box for the picture."
    words: [100, 250]
  - key: tools
    label: 3. Tools, permissions and guardrails
    prompt: "Each tool, what it may and may not do, and which customer rules are enforced in code (no compensation promises, approved reroutes) versus measured by the eval (platinum gets P1)."
    words: [80, 220]
  - key: security
    label: 4. Security, identity and data
    prompt: "Sam's requirements, one by one: how people sign in (SSO), how approvals are tied to a person, what the audit log records and where it lives, where data stays, which AWS route to Claude you'd use and what you'd check on it, and what you keep out of logs."
    words: [80, 220]
  - key: evaluation
    label: 5. Evaluation and release gate
    prompt: "The eval set, the checks, the gates (pass rate, P1 recall, cost per exception) and what happens when a gate fails. Be honest about the size of the set."
    words: [60, 180]
  - key: operations
    label: 6. Operations, rollout, risks and open questions
    prompt: "Config and kill switch, logging, fallback when the API or the breaker fails, the rollout (shadow, Chicago pilot, then other hubs), the top risks with mitigations, and the questions you still need answered and from whom."
    words: [80, 220]
rubric:
  - name: Problem, goals and scope
    points: 15
    lookFor: "Uses NorthStar's baseline and the agreed targets, not adjectives. States what is out of scope (proactive ETAs, invoice reconciliation) and why."
  - name: Architecture and trade-off
    points: 15
    lookFor: "A clear flow from carrier message to action, with a diagram that matches the text. Justifies agent versus workflow with Claude inside each step from how much paths depend on tool results, and says what would change the choice."
  - name: Rules enforced in code
    points: 15
    lookFor: "Compensation promises blocked inside notify_customer, reroutes behind an approval that fails closed, narrow tools with no extra permissions, structured decisions for evals. Distinguishes rules in code from judgement measured by the eval."
  - name: Sam's security requirements
    points: 25
    lookFor: "Addresses every one of Sam's requirements explicitly. SSO: the review and approval screens sit behind NorthStar's identity provider, approvals are recorded against the approver's SSO identity, and groups decide who may approve what. Audit log: every automated action and approval, with who, what, when and the decision, stored in NorthStar's account and protected from edits. Data: stays in NorthStar's AWS account; Claude is reached through the AWS route they already buy (Amazon Bedrock or Claude Platform on AWS), with feature availability checked for that route; logs hold metadata, not message text."
  - name: Evaluation and gate
    points: 15
    lookFor: "Describes the eval set and its size honestly, names the gates (pass rate at least 90%, P1 recall 100%, average cost at most $0.05 per exception), says the gate blocks a release, and plans to grow the set from real traffic."
  - name: Operations, risks and open questions
    points: 15
    lookFor: "Kill switch and config validated at startup, fallback to the coordinator queue, staged rollout, and specific risks (small eval set, hub differences, wrong customer emails) with mitigations. Open questions name who must answer them."
passScore: 70
graderNotes: "Sam's requirements are the point of this doc. If SSO is not mentioned at all, cap 'Sam's security requirements' at 8, even if everything else is strong. If SSO is mentioned only as a word, with no link between approvals and a person's SSO identity, cap that line at 15. If the audit log is missing, cap it at 12. If the doc sends customer data outside NorthStar's AWS account, or calls the Claude API directly with no mention of the AWS constraint, cap it at 10. Claims that a specific AWS route supports a specific feature should be framed as something to confirm, not stated from memory. If the eval section presents 100% P1 recall on 13 cases as proof of safety, with no caveat about sample size, cap 'Evaluation and gate' at 8. Mark down any rule that should be in code but lives only in the prompt (cap 'Rules enforced in code' at 8). Reward a doc that fits on one page in spirit: specific, short, and decision-ready."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Problem: coordinators are busy and SLAs are bad. Architecture: we use Claude as an agent with tools to handle exceptions automatically. Tools: get_shipment, notify_customer, reroute_shipment. The prompt tells it never to promise refunds. Security: we follow best practices and the data is secure. Evaluation: we tested it and it works well. Operations: we will monitor it. Risks: the model could make mistakes."
  - label: strong
    expect: [75, 100]
    answer: "Problem: 20.7% SLA breaches (39% platinum) and about 20 coordinator hours a day on exceptions; targets agreed with Dana. ETAs and invoice reconciliation are out of scope for 20 days. Architecture: carrier message -> agent with five narrow tools -> notify_customer or ops ticket; an agent because paths depend on tool results, and I'd move to a workflow if types stabilise. Rules in code: notify_customer blocks credit or refund language; reroute_shipment goes through guarded_execute, which fails closed. Security (Sam): approvals happen in a review screen behind NorthStar's SSO; each approval is logged with the approver's SSO identity, and only the ops-leads group may approve reroutes. Every tool call writes an append-only audit entry in NorthStar's account. The service runs in their AWS account and calls Claude through the AWS route they already buy (Bedrock or Claude Platform on AWS); I'll confirm the features we use are on it. Logs hold IDs, decisions, tokens and cost, never message text. Eval: 13 labelled cases is small; gates are pass rate at least 90%, P1 recall 100%, cost at most $0.05, and we'll grow the set from shadow traffic. Ops: kill switch in config, coordinator queue as fallback, shadow then Chicago then Detroit. Open: Kansas City's ticketing system (Marcus), audit retention period (Sam)."
---

Every earlier step of the capstone built a piece. Now write the document that explains the whole thing to the people who have to approve it. Dana reads it for the decision, Marcus for the operating rules, and Sam Ortiz, NorthStar's IT security lead, reads every line of the security section.

Lesson 04 gave you the outline. Use your own results from the build, eval and readout exercises. Keep it to what fits on one page if it were printed: specific, short and decision-ready. The diagram box is for the architecture picture (Mermaid or ASCII).

Remember Sam's words from the brief: *"Anything automated needs SSO and an audit log of every action. Customer data stays in our cloud account; we use Claude through our existing AWS setup."* A design doc that doesn't answer each of those won't get past him.

This doc is about the in-course capstone. For a design doc on a project you own, built against the real API in your own repository, see the portfolio capstone in Foundations module C8. Sam, Dana, Marcus and NorthStar Logistics are fictional.
