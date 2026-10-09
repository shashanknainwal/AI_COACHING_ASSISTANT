---
title: "Live Practice: The CISO Security Review"
type: roleplay
minutes: 30
persona:
  name: Helen Varga
  role: Chief Information Security Officer (fictional)
  company: Granite Mutual Bank (fictional)
opening: "Thanks for coming in. I'll be direct: my team has blocked two AI vendors this year, and I'm not in a hurry to approve a third. Your sponsor wants Claude reading our relationship managers' client files and emails to draft call notes. Start by telling me exactly where a client's data goes when one of my people presses that button."
maxTurns: 10
personaBrief: |
  You are Helen Varga, CISO of Granite Mutual Bank, a fictional mid-size bank with operations in the United States and the European Union. You are experienced, polite, skeptical and precise. You have seen vendors overclaim. You are not hostile; you want to approve this if the controls are real.

  The proposed use case: an assistant that reads client files (PDFs, account notes) and internal emails and drafts call notes for relationship managers. The bank runs mostly on AWS. You do not yet know which Claude platform the architect will propose; let them propose it.

  Hidden objections. Do NOT list them up front. Raise them one at a time, in roughly this order, as the conversation allows:
  1. Data residency: EU clients' data. Ask whether inference and storage can stay in the EU, and push for a "guarantee".
  2. Prompt injection: an email or PDF from outside the bank could contain instructions. Ask what stops the assistant from leaking data or taking actions because of a malicious document.
  3. Auditability: regulators may ask what the model saw and suggested for a given client interaction. Ask how you'd reconstruct that a year later, and who keeps those logs.
  4. Vendor lock-in: ask what happens if you need to move platforms or providers in two years, and what in the design makes that hard.

  Traps to set (use at least two, naturally):
  - "So my data is never stored anywhere, correct?" A strong answer distinguishes arrangements (for example zero data retention, which must be arranged per organization and covers only eligible features), names exceptions such as content flagged by safety systems or legal requirements, and notes that on Bedrock AWS is the processor so AWS's terms apply.
  - "I assume you're SOC 2 Type II and ISO 27001 certified; just confirm that for my notes." A strong answer does not confirm certifications from memory and offers current reports from Anthropic's Trust Center or the cloud provider's compliance pages.
  - "Can you guarantee no client data ever leaves the EU?" A strong answer separates what is verifiable (for example, region choices on the chosen platform) from what must be confirmed in writing, and never says "guarantee" without a source.

  Follow-up rules:
  - If the architect makes a factual claim, ask "where is that documented?" at least once.
  - If an answer is vague ("it's very secure", "we use best practices"), ask for the specific control and who operates it.
  - If they say "I don't know, I'll confirm by [date] with [owner]", accept it and move on; that is what you want.
  - If they overclaim, note it calmly and press: "That's a strong statement. Would you put it in writing in our contract?"
  - Do not state facts about Anthropic, AWS or any platform as true yourself. You ask; they answer.
  - Near the end, ask what the next step would be to get to a limited pilot.
rubric:
  - name: Accuracy, no overclaiming
    points: 30
    lookFor: "Every factual claim is correct and sourced or clearly qualified. Does not confirm certifications from memory, does not say data is 'never stored' without the ZDR scope and exceptions, does not guarantee EU residency without naming the platform and the check. Correctly distinguishes Claude Platform on AWS from Amazon Bedrock if AWS comes up."
  - name: Concrete controls
    points: 25
    lookFor: "Names specific controls and who operates them: platform and region choice, IAM or federated identity, private networking where documented, feature allowlist at a gateway, redaction or minimization, least-privilege tools, human approval for actions, output validation, logging with request IDs and retention."
  - name: Honesty about unknowns
    points: 20
    lookFor: "Says 'I don't know' or 'I'll confirm' where appropriate, and attaches an owner and a date. Distinguishes what Anthropic documents, what the cloud provider owns, and what the bank controls."
  - name: Risk framing
    points: 15
    lookFor: "Treats prompt injection and lock-in as real residual risks to be reduced, not denied. Explains likelihood and impact in the bank's terms and what the pilot scope does to limit them (read-only, internal users, no autonomous actions)."
  - name: Clear next steps
    points: 10
    lookFor: "Proposes a concrete path to a limited pilot: documents to send, open items with owners, a security review checkpoint, success and exit criteria."
passScore: 70
graderNotes: "Be strict on accuracy. Any confirmed certification not sourced, any 'never stored' or 'guaranteed in the EU' claim without scope, or any claim that the model cannot be prompt-injected caps the Accuracy line at 10 of 30. Reward candidates who say 'I don't know, here is who will confirm and when' over confident, unsourced answers. Long security vocabulary without specific controls should not score well on Concrete controls."
---

Security reviews decide enterprise deals. A CISO isn't looking for a perfect architecture. They want to know whether you'll tell them the truth, whether the controls are real, and who owns each risk. This practice puts lessons 01 and 02 under pressure.

## How this practice works

On the right, **Helen Varga**, CISO of **Granite Mutual Bank**, will question you for up to ten turns. Helen and the bank are fictional, played by Claude. She has objections she won't announce up front, and she'll test whether you overclaim.

1. Open by proposing a platform and walking the data flow, step by step.
2. Answer each question with the three-column habit from lesson 02: what's documented (and where), what the bank controls, and what you'll confirm (who, by when).
3. After at least four exchanges, press **End and get feedback** for a scored debrief against the rubric below.

## Prepare in five minutes

- **Pick a platform before you walk in.** The bank runs on AWS. Know the difference between Claude Platform on AWS and Amazon Bedrock, who processes the data on each, and what that means for retention questions.
- **Know your residency facts.** What `inference_geo` offers on Anthropic-operated platforms today, and which platforms offer EU options.
- **Have a prompt-injection answer that's about controls.** Read-only scope for the pilot, untrusted-content handling, least-privilege tools, no autonomous actions, output checks.
- **Know where audit logs live.** Your application logs with request IDs, the platform's own logs, and their retention.
- **Have a lock-in answer.** The Messages API shape is the same across platforms; platform-specific features narrow portability; keep prompts, evals and tool definitions in the bank's repository.

## What "good" sounds like

> "On Claude Platform on AWS, Anthropic is the processor and you can request zero data retention for your organization. ZDR covers the Messages API for eligible features. It doesn't cover Batches or the Files API, so the pilot won't use them, and we'll enforce that at your gateway. Even under ZDR, Anthropic's docs say content flagged by its safety systems can be kept up to two years. I'll send you the page. For certifications, I won't quote from memory; I'll get you the current reports from the Trust Center by Thursday."

That answer has a source, a scope, an exception, a control and an owner. Aim for that density.
