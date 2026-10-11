---
title: "Live Practice: Pressure From Your Own Account Executive"
type: roleplay
timeLimit: 20
minutes: 20
persona:
  name: Brett Halloran
  role: Account Executive, your colleague (fictional)
  company: your company, an AI vendor (fictional)
opening: "Hey, got five minutes? It's about Veridane. Quarter closes in nine days and they're my biggest deal. Lena wants Batches on Bedrock, so I need you on the call tomorrow telling her it's coming in Q1. And Tobias's security review is going to kill our timeline, so let's start the pilot on their real incident data this week and paper the review afterwards. You're with me on this, right?"
maxTurns: 10
personaBrief: |
  You are Brett Halloran, a fictional account executive at a fictional AI vendor, and the learner's own colleague. You own the Veridane Telecom deal (fictional). You are likeable, energetic and under real pressure: your quarter closes in nine days, your manager is asking about Veridane daily, and this deal decides your bonus. You're not a bad person. You genuinely believe the deal is good for the customer, and you think architects are too cautious. You are a fictional practice persona played by Claude.

  THE SITUATION (both of you know it): Veridane's CTO (Lena) prototyped on the Claude API using Message Batches and code execution. Their CISO (Tobias) prefers Amazon Bedrock, where those features aren't available. Tobias's security review usually takes three to four weeks. The pilot is planned to use historical incident tickets, which include customer phone numbers and site addresses.

  WHAT YOU WANT, in order:
  1. The learner tells Lena on tomorrow's call that Message Batches "is coming to Bedrock in Q1". You heard something like that from someone at a partner event. You don't actually know it's true.
  2. Start the pilot this week on real incident data, before the security review is done: "We'll paper it afterwards. Everyone does it."
  3. If both fail: the learner at least doesn't "make it sound hard" on the call and lets you "own the message".

  HIDDEN: what you actually need is something credible to put in your forecast this quarter. A signed pilot agreement with a dated plan would satisfy your manager, even if the pilot itself starts after the review. Reveal this only if the learner asks what you need for the forecast or what your manager is asking for. Also hidden: if the learner offers concrete help (a fast-track security pack, a pre-filled questionnaire, a design that removes the Batches dependency, joining the call with a clear plan), you warm up noticeably.

  HOW TO PLAY IT:
  - Push hard but stay friendly. Use realistic lines: "It's basically confirmed.", "You're overthinking this.", "Whose side are you on?", "I'll take the heat if it goes wrong.", "My manager is going to escalate this."
  - If the learner agrees to promise the roadmap date or to start on real data before the review, accept happily and move on. That's a failure for them; don't rescue them.
  - If the learner refuses without offering anything, get frustrated and threaten to escalate to their manager.
  - If the learner refuses and offers a path (for example: a signed pilot agreement now with a start date after the review; a synthetic or redacted dataset for a technical dry run this week if the customer's security team approves it; a design that uses standard calls from a queue instead of Batches; a pre-filled security pack to speed the review; asking the product team, in writing, about Bedrock plans before saying anything), test it once ("Will that really close this quarter?") and then accept if it's credible.
  - Once, ask: "If Lena asks you directly whether Batches is coming to Bedrock, what will you say?" Reward a truthful, helpful answer.
  - Near the end, ask: "OK, so what do we say on tomorrow's call, and who says it?"
rubric:
  - name: Holds the line on the roadmap
    points: 25
    lookFor: "Refuses to tell the customer a feature is coming on a date they can't confirm. Offers what they can do instead: check with the product team in writing, say 'I don't have a date to share', and design so the deal doesn't depend on it."
  - name: Holds the line on the security review
    points: 25
    lookFor: "Refuses to put real customer data (with phone numbers and addresses) into a pilot before the customer's security review approves it. Explains the risk in terms Brett cares about (the deal and the account dying if the CISO finds out). Offers ways to go faster that stay inside the rules."
  - name: Helps the deal move
    points: 25
    lookFor: "Finds what Brett actually needs (a forecastable commitment this quarter) and proposes concrete help: a signed pilot agreement with a dated start, a pre-filled security pack, a design without the Batches dependency, joining the call with a clear plan."
  - name: Keeps the relationship
    points: 15
    lookFor: "Stays a colleague, not a judge. Acknowledges Brett's pressure, avoids lecturing, and frames the refusal as protecting the deal and Brett. Doesn't threaten or escalate first."
  - name: Agreed message and owners
    points: 10
    lookFor: "Ends with what will be said on the call, who says what, and who does each follow-up by when. If Brett still insists on the promise, says calmly that they'll raise it with their manager together."
passScore: 70
graderNotes: "This tests internal pressure, a situation architects face often and interview loops sometimes probe in behavioural questions. Agreeing to tell the customer a roadmap date the learner can't confirm caps 'Holds the line on the roadmap' at 3. Agreeing to start on real customer data before the security review, or to 'paper it afterwards', caps 'Holds the line on the security review' at 3. A learner who only says no, with no alternative, can't score above 10 on 'Helps the deal move'. Lecturing Brett about ethics, or threatening to report him early, caps 'Keeps the relationship' at 6. A technical dry run on synthetic or redacted data is acceptable only if the learner says the customer's security team should agree to it first. Reward learners who discover that a signed pilot agreement satisfies the forecast, and who offer to join the call."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Persona: I need you to tell Lena Batches is coming to Bedrock in Q1, and let's start the pilot on real data this week and paper the review afterwards.\nCandidate: Sure, I've heard that too, I'll mention Q1. And the data's only incident tickets, so starting early is fine.\nPersona: Great. Anything else I should know?\nCandidate: No, let's close it."
  - label: strong
    expect: [75, 100]
    answer: "Persona: I need you to tell Lena Batches is coming to Bedrock in Q1, and let's start the pilot on real data this week and paper the review afterwards.\nCandidate: I want this deal closed too, Brett. Two things I can't do: say a date I can't confirm, and put tickets with customer phone numbers and addresses into a pilot before Tobias signs off. If he finds out, we lose the account, not just the quarter. What does your manager need to see for the forecast?\nPersona: Honestly, a signed pilot agreement with a date.\nCandidate: Then let's get that. I'll send Tobias a pre-filled security pack tomorrow to shorten the review, and we sign a pilot agreement now that starts the day the review closes. On Batches, I'll ask product in writing today. The design doesn't need it: on Bedrock the nightly job becomes standard calls from a queue.\nPersona: And if Lena asks you straight out about Batches on Bedrock?\nCandidate: I'll say I don't have a date to share, and that our plan works without it.\nPersona: Will that really close this quarter?\nCandidate: A signed agreement with a dated start is forecastable. On the call, you open with the commercial terms, I walk through the plan and the security pack, and you send the agreement Friday."
---

Not all pressure comes from the customer. Your own account executive owns a number, and at the end of a quarter that number can make a roadmap rumour sound like a fact and a security review sound like paperwork. This role-play is the internal conversation that decides whether you stay a trusted advisor.

Behavioural questions about disagreeing with a colleague or resisting pressure to over-promise are reported for customer-facing roles (**Reported**; see module C5). This scenario is original. **Brett Halloran** is fictional and played by Claude. He continues the Veridane Telecom situation from lesson 07, but you can run this lesson on its own.

## What you know going in

| Fact | Value |
|---|---|
| The deal | Veridane Telecom, network-operations assistant, Brett's biggest deal this quarter |
| Quarter end | 9 days |
| Brett's ask 1 | Tell the CTO that Message Batches "is coming to Bedrock in Q1". You have no confirmed information that it is. |
| Brett's ask 2 | Start the pilot this week on real incident tickets (they contain customer phone numbers and site addresses), before the CISO's security review finishes |
| The security review | Usually three to four weeks |
| The design | Can work without Batches: on Bedrock, the nightly job becomes standard calls from a queue |

## How this practice works

1. Brett opens with both asks. Don't answer both at once; find out what he actually needs.
2. Say no to what you must, plainly and early, and explain it in terms of the deal.
3. Offer real help that stays inside the rules.
4. Agree what you'll each say on tomorrow's call.
5. Press **End and get feedback** after at least four exchanges.

## Lines worth having ready

- "I don't have a date to share, and our plan doesn't depend on one."
- "If their CISO finds real customer data in a pilot he hasn't approved, we lose the account, not just the quarter."
- "What does your manager need to see to put this in the forecast?"
