---
title: "Graders: Code, Humans and LLM-as-Judge"
type: reading
minutes: 18
---

> **By the end of this lesson you will be able to:**
> - Pick the cheapest grader that measures what matters for each output type
> - Write an LLM-as-judge rubric and prompt that produce consistent verdicts
> - Calibrate a judge against human labels with accuracy, false-pass rate and Cohen's kappa
> - Recognize and counter the common biases of LLM judges

## Three kinds of graders

A grader turns one output into a score. Prefer them in this order: cheapest, fastest and most reliable first.

| Grader | Use it for | Example |
|---|---|---|
| **Code** | Anything with a checkable right answer | Category equals label; JSON matches schema; number within 1%; extracted date equals reference; generated SQL returns the expected rows |
| **LLM-as-judge** | Open-ended text where "correct" needs judgment | Is this answer correct and grounded? Does this email follow the style guide? |
| **Human** | Building labels, calibrating judges, high-stakes spot checks | A support lead reviews 50 answers a week |

Code graders are deterministic, free and instant: **design outputs so code can grade them.** Structured outputs help: if the system returns `{"category": ..., "urgency": ...}`, grading is a comparison. Even for free text, you can often check pieces with code: does the answer contain the right dollar amount? Does every citation exist? Is it under 100 words?

Useful code-grader patterns:

- **Exact match** after normalizing (lowercase, strip, sort lists).
- **Set metrics** for lists (extracted line items, tags): precision, recall, F1.
- **Numeric tolerance:** `abs(actual - expected) <= 0.01 * abs(expected)`.
- **Schema and constraint checks:** required fields, allowed values, length limits.
- **Execution:** run generated code or SQL and compare results, not text.

## LLM-as-judge

When outputs are open-ended, a second model call can grade them. Done well, LLM judges agree with humans about as often as humans agree with each other. Done badly, they produce confident, meaningless numbers.

### Writing the judge

- **A specific rubric.** "Is this a good answer?" yields noise. List the criteria: states the facts the customer needs; no claims that contradict the reference; addresses the question. Also say what *doesn't* matter ("length and tone don't affect this grade").
- **A reference answer** when you have one. Grading against a reference is far more reliable than asking the judge to know the right answer.
- **Binary or few-point scales.** Pass/fail per criterion is more consistent than a 1-10 score. If you need a scale, define every point.
- **Reasoning before the verdict.** Ask for the explanation first, then the verdict, in a structured output. The verdict then follows from the reasoning, and the reasoning shows you why a case failed.
- **One judgment per call.** Grading five criteria at once blurs them; split them when precision matters.
- **A capable model.** The judge needs to be at least as good at the task as the system it grades. Use a strong model, and keep the judge's prompt separate from the system's prompt.

### Known biases

| Bias | What happens | Countermeasure |
|---|---|---|
| **Verbosity** | Longer, confident answers get passed more often | Rubric says length doesn't matter; calibration set includes long wrong answers |
| **Position** | In A-vs-B comparisons, the first (or second) option wins more often | Run both orders; count a win only if it's consistent |
| **Self-preference** | A model may favor text that sounds like its own | Calibrate against humans; consider a different judge model |
| **Leniency** | Judges pass borderline answers | Strict rubric with explicit fail conditions; track false-pass rate |
| **Format sensitivity** | Paraphrases ("twenty-five dollars" vs "$25") get failed | Rubric says equivalent wording is fine; include paraphrases in calibration |

## Calibration: grading the grader

Never ship a judge you haven't compared with humans. Take 50-200 outputs, have a domain expert label them, run the judge on the same outputs, and measure:

- **Accuracy:** how often judge and human agree.
- **False passes:** the judge passed something the human failed. For most customer systems this is the dangerous direction, because a lenient judge hides real failures.
- **False fails:** the judge failed something good. Annoying and wasteful, but less dangerous.
- **Cohen's kappa:** agreement corrected for chance.

Why kappa? Suppose 90% of answers are good, and a lazy judge says "pass" to everything. Its accuracy is 90%, which looks great, but it has no skill. Kappa compares the observed agreement with the agreement you'd expect by chance, given how often each side says "pass":

```
po    = share of cases where judge and human agree
jp    = judge's pass rate,   hp = human's pass rate
pe    = jp × hp + (1 − jp) × (1 − hp)     # chance agreement
kappa = (po − pe) / (1 − pe)
```

Kappa is 1 for perfect agreement and 0 for chance-level agreement (the always-pass judge scores 0). As a rough guide, above 0.8 is strong, 0.6-0.8 is substantial, and below 0.4 means the judge isn't ready.

Read every disagreement. Each one tells you something: a rubric gap, a judge bias, or sometimes a mislabeled case. Fix the rubric, re-run, and re-calibrate whenever you change the judge's prompt or model.

## Pairwise comparison

Sometimes the question isn't "is this good?" but "is the new version better?" A **pairwise** judge sees two answers to the same question and picks the better one, or a tie. It's more sensitive than absolute scores for small improvements. Always run each pair in both orders to cancel position bias, and treat inconsistent results as ties.

## Judges cost money

A judge call per case per run adds up: 500 cases × 10 runs a day is 5,000 judge calls. Keep judges for what code can't grade, use a smaller judge model only if it calibrates well, and cache the judge's rubric and instructions with prompt caching.

> **Key takeaways**
> - Prefer code graders; design outputs (structured outputs, citations) so code can grade them.
> - LLM judges need a specific rubric, a reference answer, simple scales, and reasoning before the verdict.
> - Calibrate every judge against human labels: accuracy, false passes, false fails and Cohen's kappa.
> - Counter verbosity, position, self-preference and leniency biases with rubric wording, calibration cases and order swaps.
