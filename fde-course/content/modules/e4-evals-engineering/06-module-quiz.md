---
title: "Module E4 Quiz"
type: quiz
minutes: 14
questions:
  - q: "Your intent router returns a label from a fixed set of seven through a JSON schema with an enum. How should you grade it?"
    options:
      - "An LLM judge with a rubric, because judges understand intent"
      - "Exact match against the labelled intent, in code"
      - "A human spot-check of twenty cases on every release"
      - "A pairwise judge comparing it with the previous version"
    answer: 1
    explain: "The output space is closed, so code can grade it exactly, for free, on every run. Save judges for outputs code can't grade."
  - q: "During an eval run, 4 of 200 calls time out. How should the harness treat them?"
    options:
      - "Count them as failures, since the user got no answer"
      - "Retry until they pass, then score the passing attempt"
      - "Record them as errors, unscored, and report the count"
      - "Delete those cases from the golden set permanently"
    answer: 2
    explain: "A timeout is plumbing, not the model answering wrong. Mixing the two hides both problems. A high error rate should make you distrust the run itself."
  - q: "About how wide is the 95% margin of error on a pass rate near 50% measured on 100 cases?"
    options:
      - "About ±1 point"
      - "About ±3 points"
      - "About ±5 points"
      - "About ±10 points"
    answer: 3
    explain: "1.96 × sqrt(0.25 / 100) ≈ 0.098. You need about 400 cases for ±5 points and about 1,000 for ±3."
  - q: "Why report a Wilson interval instead of the simple normal approximation for 19 passes out of 20?"
    options:
      - "Wilson stays in [0, 1]; the normal one can pass 100%"
      - "Wilson intervals are always narrower than normal ones"
      - "The normal approximation needs 1,000 cases to compute"
      - "Wilson also corrects for the bias of an LLM judge"
    answer: 0
    explain: "At p = 0.95 and n = 20 the normal approximation's upper bound is about 104.6%. Wilson behaves well near 0 and 1 and on small samples."
  - q: "Fraud reports are 3% of traffic and your golden set has none. The headline pass rate is 93%. What's the right response?"
    options:
      - "Nothing, because 3% of traffic is too small to matter"
      - "Report it as untested and add real fraud cases"
      - "Generate 500 synthetic fraud messages from the prompt alone"
      - "Raise the overall threshold to 95% to compensate for it"
    answer: 1
    explain: "A headline can't speak for categories it never tested, and fraud mistakes are expensive. Real cases come first. Synthetic cases should be variations of real ones."
  - q: "A lazy judge says \"pass\" to every answer. Human experts pass 90% of answers. What are its raw agreement and Cohen's kappa?"
    options:
      - "Agreement 90%, kappa 0.9"
      - "Agreement 10%, kappa 0"
      - "Agreement 90%, kappa 0"
      - "Agreement 100%, kappa 1"
    answer: 2
    explain: "It agrees on the 90% the humans passed, but chance agreement is also 0.9, so kappa = (0.9 − 0.9) / (1 − 0.9) = 0. High agreement, no skill."
  - q: "A pairwise judge says \"first\" when shown (A, B) and \"first\" again when shown (B, A). What should you record?"
    options:
      - "A wins, because A was the one shown first originally"
      - "B wins, because the second call is the more recent one"
      - "Run it a third time and take the majority of the votes"
      - "A tie, and a hit to the judge's position consistency"
    answer: 3
    explain: "The judge preferred whatever came first, not either summary. A flip between orders is position bias. Score it as a tie and track how often it happens."
  - q: "Which rubric is a judge most likely to apply reliably?"
    options:
      - "\"States the refund window; no unsupported claims\""
      - "\"Rate the overall helpfulness from 1 to 10\""
      - "\"Is this a good answer for the customer?\""
      - "\"Pick what the baseline model would have written\""
    answer: 0
    explain: "Atomic, checkable criteria give consistent verdicts. Vague scales produce noise, and naming the baseline invites label deference."
  - q: "A candidate prompt has 6 regressions and 0 fixes against the baseline on the same golden set. What does the one-sided sign test give?"
    options:
      - "p = 0.5, no evidence of any change"
      - "p = 1/64 ≈ 0.016, a real regression"
      - "p = 6/40 = 0.15, weak evidence at most"
      - "It needs the overall pass rates as well"
    answer: 1
    explain: "If flips were coin tosses, six regressions in six flips has probability (1/2)^6 = 1/64. Only flipped cases matter in a paired comparison."
  - q: "Your Opus 5.5 judge costs $16 per pairwise run over 500 cases. You want to cut judge spend sharply on per-PR runs. What's the best first move?"
    options:
      - "Drop the second order of each pair to halve the calls"
      - "Stop calibrating, since calibration runs cost money too"
      - "Calibrate Haiku 5.5; use it on PRs if it clears the bar"
      - "Set temperature to 0 so that every judge call is shorter"
    answer: 2
    explain: "Haiku 5.5 is $0.10 / $0.50 per million tokens against $4 / $20, but it's only a saving if it still agrees with humans. Dropping an order reintroduces position bias, and temperature is rejected on the newest models."
  - q: "A teammate says 50 cases run twice each gives the same precision as 100 cases run once. What's wrong with that?"
    options:
      - "Nothing; both designs produce 100 graded outputs"
      - "Runs of one case are correlated; it acts like n = 50"
      - "Repeats add noise, so 50 × 2 is less precise than 50 × 1"
      - "Repeats only matter when temperature is above zero"
    answer: 1
    explain: "Variation between cases usually dominates, and runs of the same case move together. More cases narrow the interval on the population rate; repetitions measure per-case flakiness. Average runs per case, or use clustered standard errors."
  - q: "Your gate checks twenty categories on every PR and blocks when any one drops more than 10 points. Teams complain it blocks clean PRs. What's the most likely cause?"
    options:
      - "The overall sign test is miscalculated when there are many flips"
      - "The golden set is too large for the category checks to be stable"
      - "Errors are being scored as failures in the smaller categories"
      - "Twenty checks: one crosses by chance, and one flip can trip it"
    answer: 3
    explain: "This is the multiple-comparisons problem: many independent checks make a false alarm likely on most runs, and in a small category a single flipped case is a big percentage drop. Require a minimum number of regressions, send small drops to review, or use per-category tests at a corrected threshold."
---

Twelve questions on golden sets, intervals, judges and regression gates. You need 10 correct to pass.
