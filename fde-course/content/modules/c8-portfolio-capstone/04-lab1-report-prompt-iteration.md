---
title: "Lab 1 Report: Prompt Iteration on a Real Model"
type: written
minutes: 25
sections:
  - key: setup
    label: 1. Setup
    prompt: "Model, effort, date, number of runs per prompt, and what prompt v1 and v2 contained (summarise; don't paste long prompts)."
    words: [40, 150]
  - key: results
    label: 2. Results
    prompt: "Paste your filled-in results table: correct out of 30 for each run of each prompt, the spread, intervals, flipped tickets, top confusions, cost and mean output and thinking tokens."
    words: [60, 300]
  - key: analysis
    label: 3. Signal or noise?
    prompt: "Which differences between v1 and v2 are bigger than the run-to-run spread, and which aren't? Which tickets flipped, and were they the ambiguous ones? What does that say about your labels versus your prompt?"
    words: [100, 350]
  - key: next
    label: 4. What you'd do next
    prompt: "The one change you'd make next and how you'd know it worked (how many items, how many runs)."
    words: [40, 150]
rubric:
  - name: Measured, complete numbers
    points: 25
    lookFor: "Model, effort and date stated. Correct counts out of 30 for every run of both prompts, with intervals or an explicit note on what 30 items can show. Cost and output tokens (including thinking) from the results file."
  - name: Variance taken seriously
    points: 30
    lookFor: "Compares the v1-to-v2 difference with the spread across runs and says plainly whether it's bigger than noise. Treats one ticket as about 3 points. Doesn't claim an improvement from a single run."
  - name: Error analysis on real tickets
    points: 25
    lookFor: "Names specific tickets that flipped or were always wrong, checks whether they're the ambiguous ones, and separates prompt problems from label problems from genuine ambiguity."
  - name: Honest and actionable next step
    points: 20
    lookFor: "One concrete next change with a measurement plan (more items, more runs, a held-out set). Doesn't overfit to the 30 tickets; mentions not putting test tickets in the prompt."
passScore: 70
graderNotes: "Grade honesty over results. A report with modest numbers that reads its variance correctly should score higher than a report with high numbers and no runs breakdown. If only one run per prompt is reported, cap 'Variance taken seriously' at 10. If the learner pasted the test tickets or their answers into the prompt, cap 'Error analysis on real tickets' at 10 and say why in feedback. If numbers have no counts (percentages only), cap 'Measured, complete numbers' at 12. If the learner says plainly they couldn't run the lab and gives a reasoned prediction instead, cap the total at about 50 and say what would lift it. Numbers that look invented (for example 30/30 on every run with zero cost) should be questioned in feedback."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Setup: Claude. Results: v1 got 83%, v2 got 93%. Analysis: v2 is much better because I added more detail to the prompt, a 10 point improvement. Next: add even more detail and examples."
  - label: strong
    expect: [75, 100]
    answer: "Setup: claude-haiku-5-5, effort low, 2026-10-12, 3 runs each. v1 is the kit's two-line prompt; v2 adds a one-line definition per category and three boundary rules (wrong item counts as damaged_item, a refund not yet received after a return is returns, account takeover is account). Results: v1 24/30, 25/30, 23/30 (spread 23 to 25; run 2 Wilson 65% to 93%); v2 27/30, 27/30, 28/30. Flips: v1 5 tickets (t14, t15, t20, t22, t28), 4 of them marked ambiguous; v2 2 tickets (t22, t28), both ambiguous. Top v1 confusion: damaged_item labelled returns (t15, t20). Cost $0.012 for v1, $0.015 for v2; mean output 41 tokens, about 20 of them thinking. Analysis: the v1 to v2 gap (mean 24 vs 27.3) is larger than either prompt's spread (2 tickets for v1, 1 for v2), so I believe v2 helps, but by about 3 tickets, which is one interval width at n=30. The remaining flips are t22 (invalid gift card: billing or account?) and t28 (bank transfer for wholesale): those are label questions, so I'd write a labelling rule rather than lengthen the prompt. Next: write 40 fresh tickets as a held-out set, label them before running, and compare v1 and v2 over 3 runs each; I'd only call a change real if the held-out gap exceeds the run spread."
---

Paste your lab 1 results here. The lab lives in `capstone-kit/labs/lab1_prompt_iteration/` and runs on your own API key (see the previous lesson). The in-browser simulator can't do this lab: the point is the variance a real model shows.

Fill in `RESULTS_TEMPLATE.md` from the lab folder first, then use it to answer the four sections. The grader rewards a correct reading of your numbers, including "this difference is noise", over impressive numbers.

The tickets describe Quillfeather Stationery, a fictional shop.
