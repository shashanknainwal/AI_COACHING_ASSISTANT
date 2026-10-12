---
title: "Module A4 Quiz"
type: quiz
minutes: 12
questions:
  - q: "Six weeks into a POC, the team says the results 'look promising' but nobody can say whether to proceed. What was most likely missing from the start?"
    options:
      - "A more capable model, since the current one isn't clearly good enough to decide on"
      - "Agreed success criteria with baselines, a decision owner and exit rules"
      - "A longer timeline, because six weeks is rarely enough for an enterprise POC"
      - "A more polished demo that the executive sponsor could show to the board"
    answer: 1
    explain: "Most stalls are process failures. Without agreed criteria and a named decision owner, there's nothing to decide against, so the POC drifts."
  - q: "Your POC measures field accuracy at 94.8%. Why does the customer need a baseline next to that number?"
    options:
      - "Without today's number, measured the same way, 94.8% can't be judged"
      - "Because most security reviews require a baseline before they approve a pilot"
      - "So that you can lower the target later if the final result is disappointing"
      - "It isn't needed, because 94.8% accuracy is good enough for almost any task"
    answer: 0
    explain: "A result is only meaningful as a comparison. If the manual process is 93%, 94.8% is an improvement. If it's 99%, the same number is a regression."
  - q: "Which success criterion is written well?"
    options:
      - "The assistant should be accurate, fast and easy for adjusters to use every day"
      - "Users should love the drafts and recommend the tool to their colleagues"
      - "Accuracy should be as high as possible on every document type we receive"
      - "95%+ of 14 key fields correct on the frozen 400-claim set; must-have; baseline 93%"
    answer: 3
    explain: "A usable criterion names the metric, how it's measured, on what data, the target and direction, whether it's a must-have, and the baseline."
  - q: "A customer wants a 98% accuracy target and offers 40 labelled cases to measure it. What's the main problem?"
    options:
      - "40 cases is too many for the customer's experts to label carefully in time"
      - "Accuracy targets should never be set above 95% for any production workload"
      - "On 40 cases even 39 right spans about 87% to 99%: it can't confirm 98%"
      - "The target should be set after seeing the first results, not before them"
    answer: 2
    explain: "Size the eval set along with the target. Near a high pass rate the interval is lopsided and wide on small sets. You need hundreds of cases to resolve a few points."
  - q: "Your POC hits two must-haves cleanly. The third is 0.2 points under its target, inside the borderline band you agreed. What do you recommend?"
    options:
      - "Go: round the result up, because 0.2 points is basically there"
      - "No-go: any miss on a must-have is a failure, whatever was agreed"
      - "A conditional go with a fix plan and a re-measure date, per the rules"
      - "Change the target to match the result so the readout is a clean pass"
    answer: 2
    explain: "The borderline rule exists for exactly this case. Applying the rule you agreed up front is what keeps the readout credible."
  - q: "A competitor's bake-off results cover 36 of the 40 frozen cases, at 94% accuracy. How should you treat the missing four?"
    options:
      - "Count them as errors until run, and ask neutrally for full results"
      - "Drop them from every candidate so the comparison uses the same 36 cases"
      - "Ignore them, since 36 cases is plenty to compare the candidates fairly"
      - "Point out in the readout that the competitor appears to be hiding failures"
    answer: 0
    explain: "Every candidate runs every case. Skipped cases are often the hard ones, so they count as errors until run. Ask as a fairness question, not an accusation."
  - q: "Why compare candidates on cost per task rather than price per token?"
    options:
      - "Because list prices per token are confidential and can't be shared in a readout"
      - "Tokenizers and output lengths differ, so only cost per task compares"
      - "Because cost per task always comes out lower, which helps the business case"
      - "Because price per token ignores latency, which matters more than cost"
    answer: 1
    explain: "Token counts depend on the tokenizer and on how much each configuration generates, including thinking. Measure tokens on the real cases and convert to dollars per task."
  - q: "Candidate A passes 35 of 40 cases and B passes 34 of 40. B costs a fifth as much and both meet every constraint. Your plan says that when quality is statistically tied, cost decides. What do you recommend?"
    options:
      - "A, because it passed one more case and accuracy matters more than cost"
      - "Run both again and again until one of them is clearly ahead of the other"
      - "Neither, because 40 cases can't prove anything about either candidate"
      - "B: the gap is noise; recommend more cases before scaling"
    answer: 3
    explain: "One case out of 40 is noise (both intervals span roughly 71% to 95%). Apply the agreed tie rule, say why, and recommend more cases to tighten the estimate."
  - q: "The customer's CTO prefers a competitor and wants the bake-off run only on examples he picks. What's the best response?"
    options:
      - "Agree to his examples, because keeping the CTO happy matters more than method"
      - "Refuse to take part in a bake-off that the customer's CTO is clearly biasing"
      - "Add his examples to a frozen, sampled set graded blind by an agreed rubric"
      - "Ask the account executive to escalate the disagreement to the customer's CEO"
    answer: 2
    explain: "Include the favourite on equal terms and make the process fair enough that any result will stand. His examples can be part of the set; they shouldn't be the whole set."
  - q: "In the readout, a survey shows agents rate the assistant 8.4 out of 10. It wasn't one of the agreed criteria. How should you use it?"
    options:
      - "As labelled context only, never in place of a missed criterion"
      - "Lead the readout with it, because executives respond to simple numbers"
      - "Use it to offset the missed handling-time target in the overall decision"
      - "Leave it out entirely so nobody can accuse the team of cherry-picking"
    answer: 0
    explain: "Extra signals can add context, but scoring the POC on a metric nobody agreed to is moving the goalposts. Report it, label it, and don't let it replace a miss."
---

Ten questions on POC plans, success criteria, fair bake-offs and honest readouts. You need 8 correct to pass.
