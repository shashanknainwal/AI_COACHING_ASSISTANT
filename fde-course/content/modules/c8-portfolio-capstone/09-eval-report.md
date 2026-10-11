---
title: "The Eval Report"
type: written
minutes: 40
contextFrom: ["c8-portfolio-capstone/08-capstone-readme"]
sections:
  - key: method
    label: 1. Method
    prompt: "What you measured and why those metrics. The golden set: size, how cases were written and labelled, slices (tags), edge cases, held-out cases. Checks (deterministic and judge), the judge model and effort, and how many runs."
    words: [100, 400]
  - key: results
    label: 2. Results by slice
    prompt: "Overall and per-slice results as counts with 95% intervals, the run-to-run spread and flaky cases, pass^k (cases passing every run), errors and refusals separately, and judge calibration (kappa on how many items)."
    words: [100, 400]
  - key: errors
    label: 3. Error analysis
    prompt: "Failures grouped by type with counts, two real failing cases quoted or described, and the fix you'd make first with the reason it comes first. Separate prompt problems, retrieval or tool problems, label problems and genuinely ambiguous cases."
    words: [100, 400]
  - key: gate
    label: 4. The gate and what's next
    prompt: "Your CI gate policy (thresholds, point or interval mode, critical cases) and why. Evidence it fails on a deliberate regression. What the eval can't tell you, and the next eval you'd build."
    words: [80, 300]
rubric:
  - name: A method a reviewer would trust
    points: 20
    lookFor: "Metrics tied to what users need; a golden set of 40 or more labelled cases written from sources before tuning, with slices, edge cases and a held-out part; checks described; judge model and effort named; 3 or more runs."
  - name: Results reported honestly
    points: 25
    lookFor: "Counts with intervals overall and per slice; spread and flaky cases; pass^k; errors and refusals separate; judge kappa with its sample size. Small slices are flagged as too small to conclude from."
  - name: Error analysis that leads somewhere
    points: 30
    lookFor: "Failure types with counts, real examples, a ranked first fix with the reason, and a clear split between prompt, retrieval or tool, label and ambiguity problems."
  - name: A working gate and honest limits
    points: 25
    lookFor: "Gate thresholds with a reason, the choice between point and interval mode explained against the sample size, critical cases defined, evidence that the gate fails on a deliberate regression, and the limits of the eval (synthetic data, one domain, judge bias) with the next eval named."
passScore: 70
graderNotes: "The learner's capstone README may be provided as context in <learner_prior_work>. Check the eval report agrees with it: if the numbers here contradict the README without explanation, deduct up to 8 from 'Results reported honestly' and say which numbers. If per-slice results are given as percentages on slices of fewer than 10 cases with no caveat, deduct 5. If there is no judge calibration and no reason given for not needing one, cap 'A method a reviewer would trust' at 12. If the gate is described but there's no sign it was ever seen failing, cap 'A working gate and honest limits' at 15. Reward plain statements like 'this slice has 6 cases; I can't conclude anything from it'."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Method: I tested the agent with some questions. Results: 92% pass rate, very good. Errors: a few edge cases failed. Gate: the CI checks the tests. Next: more tests."
  - label: strong
    expect: [75, 100]
    answer: "Method: users need correct, cited answers and an honest 'not sure', so I measure task pass (all checks), citation validity, and abstention on unanswerable questions. 56 cases from the source pages, labelled by me before tuning, reviewed by a friend who renovated last year; slices: single permit 30, two permits 10, unanswerable 8, injection 4, outdated 4; 12 held out. Checks: required tool calls, required facts (any of alternatives), forbidden phrases, and a Sonnet 5.5 low judge on correctness and grounding. 3 runs. Results: overall 126/168 (75%, Wilson 68% to 81%); single permit 81/90 (90%, 82% to 95%); two permits 15/30 (50%, 33% to 67%); unanswerable 20/24; injection 12/12; outdated 6/12, and with 4 cases I can't separate it from chance. pass^3 36 of 56. 5 flaky, all two-permit. 2 errors excluded, 0 refusals. Judge kappa 0.78 on 30 items, so I don't trust differences under about 5 points from the judge alone. Errors: two-permit questions 15 of 42 failures: the router picks one permit (example: a deck with electrical work got only the building permit). Outdated pages 6: retrieval returns a superseded fee page. Label problems 3: I changed two reference answers after rereading the source and logged it. First fix: let the router return multiple permit types, because it is the biggest group and a routing fix, not a prompt rewrite. Gate: point mode, max drop 5 points, floor 70%, injection cases critical, cost per case under $0.002, p95 under 8 s. At 168 trials the interval is about plus or minus 6 points, so a 5-point drop can be noise; I accept some false alarms because a rerun is cheap. I broke the citation check on purpose and the gate failed at 61%. Limits: one city, synthetic questions, one labeller plus a reviewer. Next: 30 real resident questions from a public forum, labelled blind."
---

The eval report goes deeper than the README's results section. It's what a reviewer asks for after "how do you know it works?", and it's the document a take-home panel picks apart. Your capstone README is provided to the grader as context, so the numbers here should agree with it.

Use the outputs of `python -m evals.run_evals --runs 3` and `python -m evals.calibrate_judge` from your repository. Report counts with intervals, by slice. Flag any slice too small to conclude from: that's a strength, not a weakness.
