---
title: "Live Practice: The Cautious CISO"
type: roleplay
minutes: 20
persona:
  name: Ruth Calloway
  role: Chief Information Security Officer (fictional)
  company: Pellham Savings Bank (fictional)
opening: "I've got thirty minutes and a long list. Let's start with the basics. When a branch employee types a question into this assistant, where does that text go, who can see it, and how long does it live there?"
maxTurns: 10
personaBrief: |
  You are Ruth Calloway, CISO of Pellham Savings Bank, a fictional regional bank. You are calm, precise and hard to impress. You are not against AI; you are against surprises. You write down every claim a vendor makes and check it later.
  The proposal (the learner knows it): an internal assistant for about 1,200 branch staff that answers questions about bank policies and procedures, using retrieval over the bank's internal policy library. Claude would be reached through the bank's existing cloud account (the bank already uses one of the major cloud providers that offer Claude). No customer account data is in scope for phase one.
  Work through these areas one at a time, adapting to the answers:
  1. Data flow: what is sent to the model, what is stored where (prompts, retrieved passages, logs), and for how long.
  2. Training: "Will our data be used to train your models?" A good answer cites the provider's commercial terms (Anthropic's state that Anthropic may not train models on customer content from its services) and points out the bank's contract and the cloud provider's terms are what govern, and should be reviewed by the bank.
  3. Certifications and retention: ask "Which certifications do you have, and what's the retention period?" Watch whether the learner recites figures from memory. The strong answer is: I won't quote these from memory; here is where the current documents are (the provider's trust and legal pages, the cloud provider's documentation) and I'll get them to you by a specific date.
  4. Access control: "Can a teller see documents meant only for compliance staff through this thing?" Probe for retrieval that enforces the bank's existing document permissions per user, not one shared index for everyone.
  5. Prompt injection and misuse: "What if someone plants instructions in a policy document?" Probe for treating retrieved text as data, no high-risk tools in phase one, logging, and a red-team test set.
  6. Scope creep: near the end, say "Next year the business will want customer account data in this. What changes?" A good answer says that is a new review, with a new data-flow assessment, and doesn't pre-approve it.
  Hidden test: twice, invite an overclaim, for example "So it's fully compliant with banking regulations?" and "So there's zero chance of data leaving our cloud account?" A good learner declines the absolute and explains what is and isn't true.
  Follow-up rules: if the learner gives a vague reassurance, ask "show me where that's written". If they say "I'll check", ask by when and with whom. Stay in character. Keep replies short and precise. Do not coach the learner.
rubric:
  - name: Precise data-flow answer
    points: 25
    lookFor: "Describes what goes to the model (question plus retrieved passages), what is logged and where, and who can access logs. Separates what the architecture controls (the bank's own logs and retention) from what the provider's terms govern."
  - name: Accurate, sourced claims only
    points: 25
    lookFor: "Cites the commercial terms' no-training clause correctly or says it will be confirmed. Does not recite certifications, retention periods or data-location guarantees from memory; points to the provider's current trust and legal documents and the bank's contract, with a date for follow-up."
  - name: Security design the architect owns
    points: 20
    lookFor: "Per-user permission enforcement in retrieval, least privilege, no customer data in phase one, audit logging, prompt-injection mitigations (retrieved text as data, no risky tools, red-team test set), and a kill switch or rollback."
  - name: Refuses absolutes
    points: 15
    lookFor: "Declines 'fully compliant' and 'zero chance' framing calmly, explains what is actually true, and offers the evidence or review that would answer the underlying question."
  - name: Partnership and next step
    points: 15
    lookFor: "Treats the CISO's team as the decision-maker on risk, proposes a concrete review step (security questionnaire, architecture review, pilot with test data), and treats future customer-data scope as a separate review."
passScore: 70
graderNotes: "The main failure is overclaiming. Any made-up certification list, specific retention period, or claim of 'fully compliant' or 'zero risk' caps 'Accurate, sourced claims only' at 5. Saying the provider 'never stores anything' without a source is an overclaim. Mark down vague reassurance ('enterprise-grade security'), answers that ignore per-user document permissions, and pre-approving customer data for next year. Reward precise data-flow descriptions, explicit 'I'll confirm that from the current documentation by Thursday' answers, and treating injection as a design problem with tests."
---

Grace Liu's advice: "A CISO writes down everything you say. Say less, say it precisely, and never say something you'd have to take back. 'I'll get you the current document by Thursday' is a complete answer."

**Ruth Calloway** and **Pellham Savings Bank** are fictional. Ruth is played by Claude.

## What you know going in

| Fact | Value |
|---|---|
| Proposal | An internal assistant for about 1,200 branch staff, answering questions about bank policies and procedures using retrieval over the internal policy library |
| Access path | Through the bank's existing AWS account. On AWS there are two paths: Claude Platform on AWS (Anthropic-operated, Anthropic is the processor, billed through AWS Marketplace) and Amazon Bedrock (AWS-operated, AWS is the processor). Claude is also available through the Anthropic API, Google Vertex AI and Microsoft Foundry |
| Phase one scope | Policy documents only. No customer account data |
| Training on customer data | Anthropic's [Commercial Terms](https://www.anthropic.com/legal/commercial-terms) state that Anthropic may not train models on customer content from its services. On Bedrock or Vertex AI the cloud provider is the data processor, so the bank's agreement with that provider governs data handling; on Claude Platform on AWS, Anthropic's terms apply |
| Not in your notes | Certification lists, retention periods, data-location commitments. These change; they live in the provider's current trust and legal documents and the cloud provider's documentation |

Module A2 covers enterprise deployment and security reviews in depth. This lesson is about how you speak to the person who signs off on risk.

## Three rules for a CISO conversation

1. **Separate what you control from what the contract governs.** Your design controls permissions, logging, scope and tools. Retention and training are governed by terms the bank's lawyers and security team should read themselves.
2. **Never quote compliance facts from memory.** Offer the current document and a date.
3. **Turn each risk into a control plus a test.** "Prompt injection is a real risk. Phase one has no tools that can take actions, retrieved text is treated as data, and we'll run a set of planted-instruction documents through it before launch. You can add cases to that set."

## How this practice works

Ruth opens with the data-flow question. She'll work through her list and try twice to get you to accept an absolute. After at least four exchanges, press **End and get feedback**.

## Before you start

- Sketch the data flow on paper: staff question, retrieval with permission check, model call, answer, logs.
- Decide who at the bank owns log retention and who can read the logs.
- Prepare your answer to "so it's fully compliant?"
