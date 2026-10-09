---
title: "Module 1 Quiz"
type: quiz
minutes: 8
questions:
  - q: "What most clearly separates a forward deployed engineer from a consultant?"
    options:
      - "FDEs only work remotely"
      - "FDEs represent a product company and feed deployment lessons back into the product"
      - "Consultants write more code than FDEs"
      - "FDEs never talk to executives"
    answer: 1
    explain: "Consultants deliver a statement of work. FDEs make the product succeed at the customer and turn repeated custom work into product improvements."
  - q: "Which problem statement is the best output of discovery?"
    options:
      - "Use AI to improve customer support"
      - "Build a chatbot by Q3"
      - "Cut tier-1 article lookup time from ~6 minutes to under 2 for the top 20 ticket categories, without lowering CSAT"
      - "Make support agents happier"
    answer: 2
    explain: "A good problem statement names who, what, a baseline, a target and a guardrail metric."
  - q: "Your riskiest assumption is that the customer's ticket data can be exported and is usable. What should you build first?"
    options:
      - "A polished UI for agents"
      - "A script that pulls and profiles a week of real ticket data"
      - "A multi-agent system"
      - "A slide deck explaining the architecture"
    answer: 1
    explain: "Build the smallest thing that tests the riskiest assumption. Here that's data access and quality."
  - q: "A pilot has an enthusiastic champion but no executive sponsor. What is the most likely outcome if nothing changes?"
    options:
      - "Rapid expansion across the company"
      - "The pilot succeeds but never expands"
      - "The security team blocks it"
      - "The champion becomes the sponsor automatically"
    answer: 1
    explain: "Without someone who owns budget and the business outcome, pilots stall in 'pilot purgatory'."
  - q: "With scores impact × urgency ÷ effort, which request ranks highest? A: impact 5, urgency 4, effort 4. B: impact 3, urgency 4, effort 1. C: impact 5, urgency 5, effort 10."
    options:
      - "A (5.0)"
      - "B (12.0)"
      - "C (2.5)"
      - "They're tied"
    answer: 1
    explain: "B scores 12, A scores 5, C scores 2.5. Cheap, valuable work wins."
  - q: "Why is `response.content[0].text` a fragile way to read a Claude response?"
    options:
      - "content is a string, not a list"
      - "The first block may be a thinking or tool_use block, not text"
      - "text is only available on streaming responses"
      - "It's deprecated in favor of response.text"
    answer: 1
    explain: "content is a list of typed blocks. Filter for blocks whose type is 'text'."
  - q: "A response comes back with stop_reason == 'max_tokens'. What does that mean?"
    options:
      - "The request was refused"
      - "Claude wants to call a tool"
      - "The output hit your max_tokens cap and is truncated"
      - "The input was too long"
    answer: 2
    explain: "Raise max_tokens or ask for a shorter answer; don't ship a cut-off response."
  - q: "At $4 per million input tokens and $20 per million output tokens, what does a call with 10,000 input and 1,000 output tokens cost?"
    options:
      - "$0.06"
      - "$0.24"
      - "$0.04"
      - "$0.60"
    answer: 0
    explain: "10,000 × $4/1M = $0.04, plus 1,000 × $20/1M = $0.02, total $0.06."
  - q: "Which is the best weekly update format for a customer sponsor?"
    options:
      - "A 30-minute status meeting with slides"
      - "A short written update on the same day each week: Shipped, Metric, Next, Need from you"
      - "Updates only when something goes wrong"
      - "A detailed engineering changelog"
    answer: 1
    explain: "Consistent, short, written updates build trust and reduce meetings."
  - q: "The customer's IT director keeps delaying your data access. What is the best first move?"
    options:
      - "Escalate to their CEO immediately"
      - "Work around IT using exported spreadsheets from a friendly user"
      - "Meet them early, bring a clear data-flow document, and ask what they need to approve"
      - "Pause the engagement"
    answer: 2
    explain: "Gatekeepers usually have legitimate concerns. Respect their process and make approval easy."
---

Ten questions on the FDE role, the operating loop, your first week, and the Messages API. You need **8 out of 10** to pass. You can retry as many times as you like.
