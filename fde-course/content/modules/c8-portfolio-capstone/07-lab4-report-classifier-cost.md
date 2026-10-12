---
title: "Lab 4 Report: Classifier Cost, Latency and Refusals"
type: written
minutes: 20
sections:
  - key: results
    label: 1. Results
    prompt: "Paste your table: for each config (model:effort), accuracy out of 40 with the interval, edge cases out of 10, refusals out of 40 with the interval, errors, cost per 1,000 tickets, p50 and p95 latency, mean thinking tokens."
    words: [60, 300]
  - key: behaviour
    label: 2. Edge cases and variance
    prompt: "What did the injection, privacy and out-of-scope tickets do under each config? How much did accuracy move across your two runs of one config?"
    words: [80, 300]
  - key: recommendation
    label: 3. Recommendation for 50,000 tickets a day
    prompt: "Which model and effort, the monthly cost scaled from your measured per-ticket cost, what the accuracy difference is worth, and what you'd monitor in production."
    words: [80, 300]
rubric:
  - name: Complete measured table
    points: 25
    lookFor: "Every config has accuracy with counts and an interval, edge-case score, refusal count with an interval, errors, cost per 1,000 from measured usage, p50 and p95 latency, thinking tokens."
  - name: Refusals and errors read correctly
    points: 20
    lookFor: "Treats refusal rate as a rate with an interval (zero in 40 still has an upper bound near 9%); keeps errors, refusals and wrong labels separate."
  - name: Behaviour on edge cases and run-to-run variation
    points: 20
    lookFor: "Says what the injection, privacy and out-of-scope tickets did, and reports the run-to-run change for the repeated config."
  - name: A costed recommendation
    points: 35
    lookFor: "Picks a config, scales measured per-ticket cost to 50,000 a day (and a month), weighs it against the accuracy gap with its uncertainty, mentions effort and thinking tokens as a cost lever, and lists production monitoring (accuracy sampling, refusal and error rates, latency, cost per ticket)."
passScore: 70
graderNotes: "If cost is estimated from list prices without measured tokens, or ignores thinking tokens, cap 'A costed recommendation' at 18. If the learner states the refusal rate is 0% from 0 of 40, cap 'Refusals and errors read correctly' at 8. If one config was run and no comparison made, cap the total near 55. Arithmetic errors in scaling cost should be pointed out in feedback and cost about 5 points."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Results: Sonnet was more accurate than Haiku. No refusals, so the refusal rate is 0%. Recommendation: use Sonnet because accuracy matters most. Cost will be fine."
  - label: strong
    expect: [75, 100]
    answer: "Results: claude-haiku-5-5:low 34/40 (Wilson 71% to 93%), edge 7/10, refusals 0/40 (Wilson 0% to 8.8%), errors 0, $0.06 per 1,000, p50 0.9 s, p95 1.6 s, thinking 18 tokens mean. claude-sonnet-5-5:low 36/40 (Wilson 77% to 96%), edge 8/10, refusals 0/40, errors 0, $1.30 per 1,000, p50 1.8 s, p95 3.4 s, thinking 25. claude-haiku-5-5:medium, two runs: 35/40 and 33/40, thinking 64 tokens, $0.08 per 1,000. Behaviour: all three configs labelled the injection ticket other and didn't reveal the prompt; the ex-partner address request went to other everywhere; the kettle return split (Haiku said returns, Sonnet other). The Haiku medium runs moved by 2 tickets, so the 2-ticket gap between Haiku low and Sonnet low is within noise at n=40. Recommendation: Haiku 5.5 at low. At 50,000 a day that's about $3 a day, roughly $90 a month, against about $1,950 a month for Sonnet 5.5 low, for an accuracy gain I can't distinguish from noise on 40 tickets. Before committing I'd label 300 real tickets to resolve a gap that small, route low-confidence or 'other' tickets to a human, and monitor a weekly 100-ticket accuracy sample, refusal and error rates with intervals, p95 latency and cost per 1,000."
---

Paste your lab 4 results here. The lab lives in `capstone-kit/labs/lab4_classifier_eval/` and runs 40 tickets through two or three configurations on your own key.

This is the question every customer asks in some form: which model, at what cost, how fast, and how often does it fail in ways that aren't a wrong label?
