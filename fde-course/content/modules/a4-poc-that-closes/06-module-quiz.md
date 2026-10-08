---
title: "Module A4 Quiz"
type: quiz
minutes: 12
questions:
  - q: "Six weeks into a POC, the team says the results 'look promising' but nobody can say whether to proceed. What was most likely missing from the start?"
    options:
      - "A more capable model"
      - "Written success criteria with baselines, a decision owner and exit rules, agreed before work began"
      - "A longer timeline"
      - "A more polished demo for the executive sponsor"
    answer: 1
    explain: "Most stalls are process failures. Without agreed criteria and a named decision owner, there's nothing to decide against, so the POC drifts."
  - q: "Your POC measures field accuracy at 94.8%. Why does the customer need a baseline next to that number?"
    options:
      - "Without today's number, measured the same way, nobody can tell whether 94.8% is an improvement or a regression"
      - "Baselines are required by most security reviews"
      - "A baseline lets you lower the target if the result is disappointing"
      - "It isn't needed; 94.8% is good for any task"
    answer: 0
    explain: "A result is only meaningful as a comparison. If the manual process is 93%, 94.8% is an improvement. If it's 99%, the same number is a regression."
  - q: "Which success criterion is written well?"
    options:
      - "The assistant should be accurate and fast"
      - "Users should love the drafts"
      - "Accuracy should be as high as possible"
      - "At least 95% of 14 key fields correct on the frozen 400-claim test set, graded against adjudicated labels; must-have; baseline 93%"
    answer: 3
    explain: "A usable criterion names the metric, how it's measured, on what data, the target and direction, whether it's a must-have, and the baseline."
  - q: "A customer wants a 98% accuracy target and offers 40 labelled cases to measure it. What's the main problem?"
    options:
      - "40 cases is too many to label well"
      - "Accuracy targets should never be above 95%"
      - "On 40 cases the 95% interval is roughly ±10 points, so the measurement can't tell 98% from 90%"
      - "The target should be set after seeing the results"
    answer: 2
    explain: "Size the eval set along with the target. On 40 cases, even 39 of 40 has an interval of about 87% to 100%. You need hundreds of cases to resolve a few points."
  - q: "Your POC hits two must-haves cleanly. The third is 0.2 points under its target, inside the borderline band you agreed. What do you recommend?"
    options:
      - "Go: round it up, it's basically there"
      - "No-go: any miss is a failure"
      - "A conditional go, with a written fix plan and a date to re-measure, as the agreed rules say"
      - "Change the target to match the result"
    answer: 2
    explain: "The borderline rule exists for exactly this case. Applying the rule you agreed up front is what keeps the readout credible."
  - q: "A competitor's bake-off results cover 36 of the 40 frozen cases, at 94% accuracy. How should you treat the missing four?"
    options:
      - "Count them as errors until they're run, and ask neutrally for the complete results"
      - "Drop them from every candidate so the comparison is on the same 36"
      - "Ignore them; 36 cases is enough"
      - "Point out in the readout that the competitor is hiding failures"
    answer: 0
    explain: "Every candidate runs every case. Skipped cases are often the hard ones, so they count as errors until run. Ask as a fairness question, not an accusation."
  - q: "Why compare candidates on cost per task rather than price per token?"
    options:
      - "Price per token is confidential"
      - "Tokenizers differ, so the same text is a different number of tokens on different models; only cost per task is comparable"
      - "Cost per task is always lower"
      - "Price per token ignores latency"
    answer: 1
    explain: "Token counts depend on the tokenizer and on how much each configuration generates. Measure tokens on the real cases and convert to dollars per task."
  - q: "Candidate A passes 35 of 40 cases and B passes 34 of 40. B costs a fifth as much and both meet every constraint. Your plan says that when quality is statistically tied, cost decides. What do you recommend?"
    options:
      - "A, because it's more accurate"
      - "Run both again until one is clearly ahead"
      - "Neither; 40 cases proves nothing"
      - "B, stating that the quality difference is within noise and recommending more cases to confirm before scaling"
    answer: 3
    explain: "One case out of 40 is noise (both intervals span roughly 71% to 95%). Apply the agreed tie rule, say why, and recommend more cases to tighten the estimate."
  - q: "The customer's CTO prefers a competitor and wants the bake-off run only on examples he picks. What's the best response?"
    options:
      - "Agree, to keep him happy"
      - "Refuse to take part in the bake-off"
      - "Welcome the competitor, and propose that his examples join a frozen set sampled from real traffic, graded blind by a rubric agreed in advance"
      - "Ask the account executive to escalate to the CEO"
    answer: 2
    explain: "Include the favourite on equal terms and make the process fair enough that any result will stand. His examples can be part of the set; they shouldn't be the whole set."
  - q: "In the readout, a survey shows agents rate the assistant 8.4 out of 10. It wasn't one of the agreed criteria. How should you use it?"
    options:
      - "Mention it as supporting context, clearly labelled as outside the agreed criteria, and never in place of a missed criterion"
      - "Lead the readout with it; executives like simple numbers"
      - "Use it to offset the missed handling-time target"
      - "Hide it so nobody accuses you of cherry-picking"
    answer: 0
    explain: "Extra signals can add context, but scoring the POC on a metric nobody agreed to is moving the goalposts. Report it, label it, and don't let it replace a miss."
---

Ten questions on POC plans, success criteria, fair bake-offs and honest readouts. You need 8 correct to pass.
