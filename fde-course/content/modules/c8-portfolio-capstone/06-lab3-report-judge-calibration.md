---
title: "Lab 3 Report: Calibrating an LLM Judge"
type: written
minutes: 25
sections:
  - key: labels
    label: 1. Your labels
    prompt: "How you labelled the 20 items, which ones were hard, and your agreement and kappa with the author's labels."
    words: [60, 250]
  - key: judge
    label: 2. The judge against your labels
    prompt: "Paste your table: judge model and effort, agreement and kappa for each run and for the majority vote, the confusion counts, self-agreement across runs, and cost."
    words: [60, 300]
  - key: disagreements
    label: 3. Every disagreement
    prompt: "For each item where the judge's majority disagreed with you: what the judge's rationale said, and who was wrong (the judge, your label, or the rubric). Then the rubric change you made and its effect."
    words: [100, 400]
  - key: trust
    label: 4. Would you gate on it?
    prompt: "Would you trust this judge as a CI gate? At what threshold, with what spot-checking, and what would make you re-calibrate?"
    words: [60, 200]
rubric:
  - name: Labelled first, honestly
    points: 20
    lookFor: "Labelled before running the judge, names the hard items, reports human-vs-author agreement and kappa, and treats that as a rough ceiling for the judge."
  - name: Correct calibration numbers
    points: 25
    lookFor: "Agreement and kappa per run and for the majority, confusion counts, judge self-agreement, model, effort and cost. Understands that kappa corrects for chance (an always-pass judge has kappa 0)."
  - name: Disagreements analysed, not explained away
    points: 30
    lookFor: "Goes through each disagreement with the rationale, decides who was wrong, and admits when their own label was the mistake. Any label changed after seeing the judge is disclosed. One rubric change, re-run, effect reported."
  - name: A sensible trust decision
    points: 25
    lookFor: "A clear yes or no on gating with a threshold, ongoing spot-checks of a sample, and triggers for re-calibration (a judge model change, a rubric change, a new data slice). Mentions the small sample (20 items)."
passScore: 70
graderNotes: "If kappa is missing or the learner reports only raw agreement, cap 'Correct calibration numbers' at 10. If the learner silently changed labels to match the judge, or says they labelled after seeing the judge's verdicts, cap 'Labelled first, honestly' at 5. If every disagreement is blamed on the judge without reading its rationale, cap 'Disagreements analysed' at 12. Kappa near 1.0 on 20 items is possible but should come with a note on sample size. Reward reports that notice the borderline items drive both human and judge disagreement."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Labels: I agreed with most. Judge: it got 90% so it's accurate. Disagreements: the judge was wrong on two because it is an AI. Trust: yes, the judge is good enough to use."
  - label: strong
    expect: [75, 100]
    answer: "Labels: I labelled all 20 before running anything, using the five rubric lines. Hard: a11 (vague duplicate-charge answer), a18 ('a couple of weeks' vs 14 days) and a20. Me vs author: 18/20, kappa 0.80; we split on a18 and a20. Judge (claude-sonnet-5-5, low, 3 runs): run 1 17/20 kappa 0.70, run 2 18/20 kappa 0.80, run 3 17/20 kappa 0.70; majority 18/20 kappa 0.80; confusion human/judge pass/pass 9, fail/fail 9, pass/fail 1, fail/pass 1; self-agreement 85% (unstable: a11, a18, a20); cost $0.21. Disagreements: a18, I said pass, the judge failed it on 'grounded' because 'a couple of weeks' isn't the stated 14 days; I now think the judge is right and changed my label, noted here. a11, I said fail, the judge passed it saying it matches the pending-charge fact; the rubric doesn't say an answer must include the settle-and-refund step, so that's a rubric gap. Rubric v2 adds 'complete: includes every fact the customer needs to act'. Re-run majority 19/20, kappa 0.90, self-agreement 95%. Trust: yes for a gate on pass rate, with a 10-point margin, a weekly spot-check of 20 random verdicts, and a fresh calibration whenever the judge model, effort or rubric changes. Twenty items is small; I'd grow the set to 60 before relying on kappa to one decimal place."
---

Paste your lab 3 results here. The lab lives in `capstone-kit/labs/lab3_judge_calibration/`. Label all 20 items yourself before you run the judge, or you'll anchor on its verdicts.

An LLM judge is a measuring instrument. This report shows you checked the instrument before trusting its readings.
