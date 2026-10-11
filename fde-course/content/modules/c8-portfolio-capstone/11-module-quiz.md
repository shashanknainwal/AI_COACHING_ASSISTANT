---
title: "Module C8 Quiz"
type: quiz
minutes: 12
questions:
  - q: "What makes the Foundations portfolio capstone different from the module 10 capstone?"
    options:
      - "It is graded by hidden tests running in the browser"
      - "It runs on the real API with your own key, in a domain you choose"
      - "It uses a fixed customer and dataset chosen by the course"
      - "It is optional reading with no graded deliverables at all"
    answer: 1
    explain: "Module 10 runs on the in-browser simulator with a given customer. The portfolio capstone runs against the real API on your own key, in your own domain, and is graded through written reports and the review role-play."
  - q: "Your prompt v2 scores 27/30 on one run; v1 scored 25/30 on one run. Across three runs, v1 ranged from 23 to 26. What's the honest conclusion?"
    options:
      - "v2 is clearly better: it gained more than six points"
      - "v2 is worse, because single runs always overstate gains"
      - "Nothing can be learned from 30 tickets, so stop measuring"
      - "The gap is within v1's own run-to-run spread; run v2 more times"
    answer: 3
    explain: "A 2-ticket gap is smaller than v1's 3-ticket spread across runs. Run v2 several times and compare spreads before claiming a gain."
  - q: "An LLM judge agrees with your labels on 11 of 20 items. It said 'pass' to all 20, and 11 of your labels are 'pass'. What is its Cohen's kappa?"
    options:
      - "0, because its agreement is exactly what chance predicts"
      - "0.55, because it agreed on 55% of the items"
      - "1.0, because it never contradicted itself across items"
      - "It can't be computed without a third labeller"
    answer: 0
    explain: "Kappa corrects for chance. A judge that always says pass agrees with you exactly as often as chance would, so kappa is 0 despite 55% raw agreement."
  - q: "Lab 4 shows 0 refusals in 40 calls. How should you report the refusal rate?"
    options:
      - "As 0%, since no call was refused during the test"
      - "As unknown, since refusals are random and cannot be measured"
      - "As 0 of 40, with a 95% upper bound of about 9%"
      - "As 2.5%, adding one imaginary refusal to the count to stay conservative"
    answer: 2
    explain: "Zero observed events still leaves real uncertainty with a small sample. The Wilson interval for 0 of 40 runs from 0% to about 9%. Claiming a rate under 1% needs hundreds of clean calls."
  - q: "Why does the capstone kit put the cache breakpoint on the system prompt instead of using top-level automatic caching for one-shot classification calls?"
    options:
      - "Automatic caching is unavailable on Claude Haiku 5.5"
      - "The last block changes every call, so each call would write a cache entry that is never read"
      - "Block-level breakpoints make cache writes free of charge"
      - "Top-level caching invalidates the structured output schema"
    answer: 1
    explain: "Caching is a prefix match. Put the breakpoint at the end of the shared part. If the cached block includes the per-ticket text, every call pays for a write and nothing is reused."
  - q: "Which statement about thinking and cost on current models is correct?"
    options:
      - "Thinking tokens are billed as output and count against max_tokens"
      - "Thinking tokens are free of charge, because their raw text is never returned to you"
      - "Thinking only happens when you pass a thinking parameter"
      - "Thinking tokens are billed as input at the cache-read price"
    answer: 0
    explain: "All three current models think by default. Thinking is billed as output, sits inside max_tokens and adds latency, which is why the kit sets effort explicitly and every cost table includes it."
  - q: "Your agent's response has stop_reason 'refusal' and contains a partial tool_use block. What should the loop do?"
    options:
      - "Run the tool, since the input usually parses fine"
      - "Retry the identical request in a loop until the model stops refusing it"
      - "Delete the refused turn from history and continue the loop"
      - "Stop and run no tools from that turn"
    answer: 3
    explain: "A refusal can cut a tool_use block off mid-input. Never execute that turn's tools; stop, and handle the refusal as its own outcome."
  - q: "Overnight your judge model is upgraded and your pass rate rises 8 points with no code change. What should you do first?"
    options:
      - "Reset the baseline, since the judge is now more accurate"
      - "Lower the gate's thresholds so that the next nightly run is stable again"
      - "Pin the judge version and re-calibrate it against human labels"
      - "Switch the system under test to the new model version too"
    answer: 2
    explain: "A changed judge is a changed instrument. Pin its version, re-run calibration, and score the same outputs with both judges before you trust or reset anything."
  - q: "Which README sentence would a deep-dive interviewer trust most?"
    options:
      - "Our agent achieved excellent accuracy and is production ready"
      - "Pass rate 126/168 over 3 runs (Wilson 68% to 81%); 2 errors excluded"
      - "We used the best model available to minimise hallucinations"
      - "Accuracy was around 95% in our internal testing last month"
    answer: 1
    explain: "Counts, runs, an interval and errors reported separately give the reviewer something to check. Adjectives and unsourced percentages invite the next question."
  - q: "In point mode with 36 trials, your gate fails on a 6-point drop. A teammate says it's noise. What's the best response?"
    options:
      - "Delete the failing cases so the gate goes green again"
      - "Switch permanently to interval mode on this one pull request"
      - "Re-run with more trials, and change the policy only in a reviewed PR"
      - "Raise max_drop to 10 points right away so that this pull request passes"
    answer: 2
    explain: "With 36 trials a 6-point move can be noise. Get more evidence by re-running with more trials. Gate thresholds change only through review, never to turn one red build green."
---

Ten questions on the ideas in this module. You need 8 to pass.
