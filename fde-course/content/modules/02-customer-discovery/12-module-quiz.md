---
title: "Module 2 Quiz"
type: quiz
minutes: 10
questions:
  - q: "A customer says: \"We need a dashboard of all our shipments.\" What's the best next question?"
    options:
      - "Which charting library do you prefer?"
      - "What would the dashboard let you do that you can't do today?"
      - "Do you want it in dark mode?"
      - "Should it refresh every minute or every hour?"
    answer: 1
    explain: "Customers describe solutions. Asking what it would enable uncovers the need, which may be early warning of late shipments rather than a dashboard."
  - q: "Which discovery question is most likely to get you real workflow detail?"
    options:
      - "How does intake usually work?"
      - "Is intake slow?"
      - "Walk me through the last referral you processed this morning."
      - "Wouldn't it be great if AI handled intake?"
    answer: 2
    explain: "Asking about a specific recent instance gets real detail instead of the idealized process. The others are generic, closed, or leading."
  - q: "In a 45-minute discovery call, what share of the words should the FDE speak, roughly?"
    options:
      - "Under about 30%"
      - "About 50%"
      - "About 70%"
      - "It doesn't matter as long as you cover the agenda"
    answer: 0
    explain: "If you're talking more than about 30%, you're pitching rather than discovering."
  - q: "A user says intake \"takes forever.\" What should you do?"
    options:
      - "Write down \"intake is slow\" and move on"
      - "Ask how long, how often, and how many people it affects"
      - "Promise to make it 10x faster"
      - "Ask whether they've tried working faster"
    answer: 1
    explain: "Quantifying turns a complaint into a baseline and a business case: for example, 6 people × 2 hours a day."
  - q: "The IT director has high influence, low interest in the project, and is skeptical. What's the right strategy?"
    options:
      - "Monitor with a monthly note"
      - "Keep informed with weekly demos"
      - "Keep satisfied, and meet them early one-on-one to understand their concerns"
      - "Avoid them until launch"
    answer: 2
    explain: "High influence + low interest = keep satisfied. A high-influence skeptic is a top risk, so meet them early."
  - q: "Which test best tells you whether someone is really your champion?"
    options:
      - "They reply to emails quickly"
      - "They attend every meeting"
      - "They will spend political capital for the project, like pushing for data access in meetings you're not in"
      - "They have the most senior title"
    answer: 2
    explain: "Friendly and responsive makes someone a contact. A champion actively advocates and takes risks for the project."
  - q: "Intake times for 9 items in hours: 2, 3, 3, 4, 4, 5, 6, 8, 120. Which number best describes the typical item?"
    options:
      - "The average, 17.2 hours"
      - "The median, 4 hours"
      - "The maximum, 120 hours"
      - "The minimum, 2 hours"
    answer: 1
    explain: "Process times are skewed; one stuck item drags the average up. Use the median for typical and p90 for the tail."
  - q: "Your baseline only includes claims that were completed. 15 claims from the window are still open. What's the issue?"
    options:
      - "None, open items don't matter"
      - "The baseline probably looks better than reality, because open items tend to be the slowest"
      - "The baseline probably looks worse than reality"
      - "You must wait until every claim closes before reporting anything"
    answer: 1
    explain: "Excluding unfinished items biases durations downward. Report the open count alongside the median."
  - q: "Which metric definition is complete?"
    options:
      - "Make intake faster"
      - "Median intake hours: target 4h"
      - "Median intake hours, baseline 26h, target 4h, decrease, by 2026-06-30, owner Marcus Lee"
      - "Users love the new intake tool"
    answer: 2
    explain: "A complete metric has a definition, baseline, target, direction, deadline, and owner (plus guardrails)."
  - q: "With structured outputs in the Anthropic API, what must every object in your JSON Schema include?"
    options:
      - "\"additionalProperties\": false"
      - "A \"description\" on every field"
      - "\"strict\": true"
      - "A default value for every field"
    answer: 0
    explain: "Structured outputs require additionalProperties: false on every object, with required fields listed in \"required\"."
  - q: "An extraction call returns stop_reason == \"max_tokens\". What should your code do?"
    options:
      - "Parse the JSON anyway; structured outputs guarantee it's valid"
      - "Raise a clear error, then retry with higher max_tokens or split the input"
      - "Return an empty dict silently"
      - "Switch to asking for JSON in the prompt"
    answer: 1
    explain: "A truncated response is cut off mid-JSON and won't parse. Fail loudly and fix the cause."
  - q: "The plan is full (25 of 25 days). The sponsor asks for a 6-day must-have. What's the best response?"
    options:
      - "\"No, the plan is full.\""
      - "\"Sure!\" and work weekends"
      - "\"Yes, and to keep the date we'd defer W5, W6 and W3, or we keep everything and move the date by 6 days. Which do you prefer?\""
      - "Quietly reduce testing to make room"
    answer: 2
    explain: "Make the trade-off visible and let the sponsor decide, then record the decision in writing."
---

Twelve questions covering discovery calls, stakeholder mapping, metrics and baselines, structured outputs with Claude, and scope management. You need **10 out of 12** to pass. You can retry as many times as you like.
