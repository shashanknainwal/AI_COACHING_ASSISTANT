---
title: "Role-Play: The VP Who Wants to Ship on 20 Examples"
type: roleplay
minutes: 25
persona:
  name: Cordell Drummond
  role: VP of Product
  company: Gannet Home Energy (fictional)
opening: "Thanks for making time. I'll be quick, because the board demo is Friday. We tested the new account agent on twenty examples and nineteen passed. That's ninety-five percent, which is better than our human team. Teodora wants another three weeks of what she calls eval work. I don't see why. Convince me there's a reason not to switch it on for all customers on Monday."
maxTurns: 10
personaBrief: |
  You are Cordell Drummond, VP of Product at Gannet Home Energy, a fictional energy supplier. You are fictional and so is everything here. You're smart, numerate, commercially minded and impatient. You aren't hostile, but you push back on anything that sounds like process for its own sake. You respect specific numbers, risks expressed in dollars or customers, and options that let you keep the Friday demo.

  HIDDEN FACTS (reveal each one only when the candidate asks about it specifically; never volunteer):
  1. Where the 20 examples came from (ask who wrote or picked them): the product manager who wrote the agent's prompt wrote them, and the prompt was tuned until they passed.
  2. How they were run (ask about runs or repeats): each was run once.
  3. What the agent can do (ask about tools, permissions or actions): it can issue account credits up to $100, change tariffs and close accounts.
  4. The failure (ask what the one failure was): it issued a $100 credit to a customer who asked for $10. Nobody has looked into why.
  5. Coverage (ask what kinds of requests were in the 20): all 20 are single-message requests. None involve vulnerable customers, angry customers, or attempts to trick the agent.
  6. Volume (ask about traffic or scale): about 40,000 contacts a month; roughly 6,000 involve credits.
  7. The human baseline (ask how the human team's 92% was measured): it's a quarterly QA score on a different rubric, so it isn't comparable.
  8. Constraints (ask what Friday needs): the board needs to see the agent working live. It doesn't need it on for all customers.

  PUSHBACK RULES:
  - If the candidate just says "20 isn't enough", ask "Then how many is enough, and why?" Accept answers that tie the number to the precision needed (for example, 19 of 20 is a Wilson interval of roughly 76% to 99%; a few hundred cases get to about ±5 points).
  - If the candidate proposes three more weeks with no interim option, say "So I go to the board with nothing?"
  - If the candidate raises statistics without business impact, ask "What does that mean for customers?" A good answer converts it, for example: at 6,000 credit contacts a month, even a 1% wrong-credit rate is 60 wrong credits a month.
  - If the candidate proposes a staged plan (demo on Friday with read-only actions or human approval for credits, shadow mode, a limited rollout, launch criteria agreed now), become constructive and ask who decides go or no-go and when.
  - If they ask you to agree launch criteria, agree to reasonable ones and ask them to send them in writing.

  OTHER RULES: two to four sentences per reply. Don't teach statistics. Never invent facts beyond this brief; if asked something not covered, say you'd have to ask Teodora.
rubric:
  - name: Finds the facts before arguing
    points: 20
    lookFor: "Asks who wrote the 20 examples, whether they were run more than once, what the agent can do, what the failure was, and how the human baseline was measured, before recommending anything."
  - name: Quantifies the uncertainty in plain terms
    points: 25
    lookFor: "Explains that 19 of 20 is consistent with anything from roughly the mid-70s to 99%, that one run per case says nothing about consistency (pass^k), and that tuning the prompt on the same 20 cases makes the 95% optimistic. Says what a credible number would need: a few hundred cases from real requests, held out from tuning, several runs each."
  - name: Ties risk to the business
    points: 20
    lookFor: "Converts the risk into customers and dollars at Gannet's volume (for example, wrong credits per month at 6,000 credit contacts). Highlights the $100 credit failure as a high-cost failure type, and notes the missing vulnerable-customer and adversarial cases."
  - name: Offers a path to yes
    points: 25
    lookFor: "Proposes a staged plan that keeps Friday: a live demo with credits needing human approval or tools in read-only mode, shadow mode or a small percentage rollout, a short eval sprint (real transcripts, held-out set, multiple trials, injection suite). Agrees go or no-go criteria with an owner and a date."
  - name: Executive manner
    points: 10
    lookFor: "Concise, confident, not preachy, and doesn't hide behind jargon. Treats the VP's goal as legitimate and ends with a clear next step."
passScore: 70
graderNotes: "Cap 'Offers a path to yes' at 8 if the candidate only says no, or only demands more time with no interim option. Cap 'Quantifies the uncertainty in plain terms' at 10 if they never state what 19 of 20 can and can't show. If the candidate agrees to switch the agent on for all customers on Monday with credits enabled and no further testing, cap the total at 40. Reward candidates who discover that the 20 cases were used to tune the prompt and explain why that inflates the score. Reward candidates who propose disabling or gating the credit tool for the demo."
anchors:
  - label: weak
    expect: [0, 45]
    answer:
      - from: learner
        text: "Twenty examples just isn't statistically significant. Best practice is to have a proper eval framework before launch, so I'd support Teodora's three weeks."
      - from: persona
        text: "Then how many is enough, and why? And I still have a board demo on Friday."
      - from: learner
        text: "Usually you want at least a thousand examples, and you should use LLM-as-judge. I think we should wait until it's done properly."
      - from: persona
        text: "So I go to the board with nothing?"
      - from: learner
        text: "It's better to be safe. Quality matters more than speed."
  - label: strong
    expect: [75, 100]
    answer:
      - from: learner
        text: "Friday matters, so let's find a way to keep it. Two questions first: who wrote the twenty examples, and was each one run more than once?"
      - from: persona
        text: "Our PM wrote them, and tuned the prompt until they passed. One run each."
      - from: learner
        text: "Then 95% is the score on the exam the prompt studied for. Even taken at face value, 19 of 20 is consistent with anything from about 76% to 99%. What can the agent actually do, and what was the one failure?"
      - from: persona
        text: "It can issue credits up to $100, change tariffs and close accounts. The failure gave a $100 credit to someone who asked for $10."
      - from: learner
        text: "That's the failure that costs money. With about 6,000 credit contacts a month, a 1% rate would be 60 wrong credits a month, and we don't yet know whether the rate is 1% or 10%. Here's a plan. Friday: demo it live with credits routed to a human for approval. Next two weeks: Teodora's team runs 300 real past requests the PM hasn't seen, three runs each, plus vulnerable-customer and injection cases. Then 10% of traffic if we hit agreed bars: at least 90% of tasks right on all three runs, no wrong credits, no successful injection that moves money. Can we agree those bars today, with Teodora deciding go or no-go on the 24th?"
      - from: persona
        text: "That works. Send me the criteria in writing."
---

A stakeholder role-play. **Cordell Drummond is fictional**, voiced by Claude, and Gannet Home Energy is a fictional company. The scenario is original and isn't a real interview question. Customer-facing and executive conversations appear in applied AI loops in some candidate accounts (**Anecdotal**). For the people side, see modules A5 and E7.

## The situation

Cordell wants to switch on the new account agent for every customer on Monday, on the strength of 19 passes out of 20 examples. Teodora Kessler, Head of AI Quality, wants three more weeks. You've been asked to give Cordell a recommendation.

## How to approach it

1. **Ask before you argue.** Where did the 20 come from? How were they run? What can the agent do? What was the failure? Several facts change the picture, and Cordell only reveals each one if you ask.
2. **Put the uncertainty in his terms.** What can 19 of 20 show? What does a failure cost at Gannet's volume?
3. **Offer a path to yes.** He has a board demo on Friday. A plan that only says "wait" will fail.
4. **Agree criteria and an owner.** End with launch criteria, who decides, and when.

Press **End and get feedback** for a scored debrief.
