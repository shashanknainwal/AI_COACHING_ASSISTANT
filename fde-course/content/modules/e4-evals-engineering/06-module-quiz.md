---
title: "Module E4 Quiz"
type: quiz
minutes: 12
questions:
  - q: "Your intent router returns a label from a fixed set of seven through a JSON schema with an enum. How should you grade it?"
    options:
      - "An LLM judge with a rubric, because judges understand intent"
      - "Exact match against the labelled intent, in code"
      - "A human spot-check of 20 cases per release"
      - "A pairwise judge against the previous version"
    answer: 1
    explain: "The output space is closed, so code can grade it exactly, for free, on every run. Save judges for outputs code can't grade."
  - q: "During an eval run, 4 of 200 calls time out. How should the harness treat them?"
    options:
      - "Count them as failures; the user didn't get an answer"
      - "Retry until they pass, then score the passing attempt"
      - "Record them as errors, leave them out of the pass rate and report the error count"
      - "Delete them from the golden set"
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
      - "The normal approximation can give an upper bound above 100% near the extremes and on small n; Wilson stays inside [0, 1]"
      - "Wilson intervals are always narrower"
      - "The normal approximation needs at least 1,000 cases to compute"
      - "Wilson accounts for judge bias"
    answer: 0
    explain: "At p = 0.95 and n = 20 the normal approximation's upper bound is about 104.6%. Wilson behaves well near 0 and 1 and on small samples."
  - q: "Fraud reports are 3% of traffic and your golden set has none. The headline pass rate is 93%. What's the right response?"
    options:
      - "Nothing; 3% is too small to matter"
      - "Report the gap as untested traffic, and add fraud cases from real reports or escalations before claiming coverage"
      - "Generate 500 synthetic fraud messages from the system prompt alone"
      - "Raise the overall threshold to 95% to compensate"
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
      - "A wins, because it was shown first originally"
      - "B wins, because the second call is more recent"
      - "Run it a third time and take the majority"
      - "A tie, and count the pair against the judge's position consistency"
    answer: 3
    explain: "The judge preferred whatever came first, not either summary. A flip between orders is position bias. Score it as a tie and track how often it happens."
  - q: "Which rubric is a judge most likely to apply reliably?"
    options:
      - "\"States the refund window from the policy; makes no claim the policy doesn't support; length and tone don't matter\""
      - "\"Rate helpfulness from 1 to 10\""
      - "\"Is this a good answer?\""
      - "\"Pick the response the baseline model would have written\""
    answer: 0
    explain: "Atomic, checkable criteria plus what doesn't matter give consistent verdicts. Vague scales produce noise, and naming the baseline invites label deference."
  - q: "A candidate prompt has 6 regressions and 0 fixes against the baseline on the same golden set. What does the one-sided sign test give?"
    options:
      - "p = 0.5, no evidence of change"
      - "p = 1/64 ≈ 0.016, strong evidence of a real regression"
      - "p = 6/40 = 0.15"
      - "It can't be computed without the overall pass rates"
    answer: 1
    explain: "If flips were coin tosses, six regressions in six flips has probability (1/2)^6 = 1/64. Only flipped cases matter in a paired comparison."
  - q: "Your Opus 5.5 judge costs $16 per pairwise run over 500 cases. You want to cut judge spend sharply on per-PR runs. What's the best first move?"
    options:
      - "Drop the second order of each pair to halve the calls"
      - "Stop calibrating the judge, since calibration costs money too"
      - "Calibrate Claude Haiku 5.5 on the same human-labelled set and use it for PRs if it meets your agreement bar"
      - "Set temperature to 0 to make each call shorter"
    answer: 2
    explain: "Haiku 5.5 is $0.10 / $0.50 per million tokens against $4 / $20, but it's only a saving if it still agrees with humans. Dropping an order reintroduces position bias, and temperature is rejected on the newest models."
---

Ten questions on golden sets, intervals, judges and regression gates. You need 8 correct to pass.
