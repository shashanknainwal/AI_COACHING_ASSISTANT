---
title: "Graders: Code, Humans and LLM-as-Judge"
type: reading
minutes: 3
---

> **By the end of this lesson you will be able to:**
> - Pick the cheapest grader that measures what matters
> - Write an LLM-as-judge rubric that produces consistent verdicts
> - Calibrate a judge with accuracy, false-pass rate and Cohen's kappa

Brightway's routing labels can be checked with `==`. Jordan also wants to know whether the agent's written replies are correct, and nobody can read 400 of them every week.

## Three kinds of graders

Prefer them in this order:

| Grader | Use it for | Example |
|---|---|---|
| **Code** | Anything with a checkable answer | Category equals label; JSON matches schema; number within 1%; generated SQL returns the expected rows |
| **LLM-as-judge** | Open-ended text that needs judgment | Is this answer correct and grounded? |
| **Human** | Building labels, calibrating judges, spot checks | A support lead reviews 50 answers a week |

**Design outputs so code can grade them.** With structured outputs (`{"category": ..., "urgency": ...}`) grading is a comparison, and free text still has checkable parts (the dollar amount, citations that exist). Patterns: exact match after normalizing; precision, recall and F1 for lists; numeric tolerance `abs(actual - expected) <= 0.01 * abs(expected)`; schema checks.

## Writing an LLM judge

- **Specific rubric:** list the criteria, and what *doesn't* matter ("length and tone don't affect this grade").
- **Reference answer** whenever you have one.
- **Binary or few-point scales:** pass/fail per criterion beats 1-10.
- **Reasoning before the verdict** in a structured output, so the verdict follows from the reasoning and you can see why a case failed.
- **One judgment per call** when precision matters.
- **A capable model,** with a prompt separate from the system's.

| Bias | What happens | Countermeasure |
|---|---|---|
| **Verbosity** | Long, confident answers pass more | Rubric says length doesn't matter; long wrong answers in calibration |
| **Position** | In A-vs-B, one slot wins more | Run both orders; count only consistent wins |
| **Self-preference** | Favors text like its own | Calibrate against humans; try another judge model |
| **Leniency** | Borderline answers pass | Explicit fail conditions; track false passes |
| **Format sensitivity** | "twenty-five dollars" vs "$25" fails | Rubric allows equivalent wording |

## Calibration: grading the grader

Have a domain expert label 50-200 outputs, run the judge on the same ones, and measure **accuracy**, **false passes** (judge passed what the human failed: the dangerous direction, because it hides real failures), **false fails**, and **Cohen's kappa**.

Kappa corrects for chance. If 90% of answers are good, a judge that always says "pass" has 90% accuracy and no skill:

```
po    = share of cases where judge and human agree
jp    = judge's pass rate,   hp = human's pass rate
pe    = jp × hp + (1 − jp) × (1 − hp)     # chance agreement
kappa = (po − pe) / (1 − pe)
```

Kappa is 1 for perfect agreement and 0 at chance (the always-pass judge scores 0). Rough guide: above 0.8 strong, 0.6-0.8 substantial, below 0.4 not ready. Read every disagreement; re-calibrate when the judge's prompt or model changes.

**Pairwise judges** pick the better of two answers and catch small improvements; run both orders and treat inconsistent results as ties. Judges cost money (500 cases × 10 runs a day is 5,000 calls), so use them only where code can't grade.

> **Key takeaways**
> - Prefer code graders; design outputs so code can grade them.
> - Judges need a specific rubric, a reference, simple scales, reasoning before verdict.
> - Calibrate against humans: accuracy, false passes, false fails, kappa.
> - Counter verbosity, position, self-preference and leniency biases.
