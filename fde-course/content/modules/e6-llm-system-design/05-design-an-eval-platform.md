---
title: "Design It: An Eval Platform for Weekly Changes"
type: written
minutes: 40
sections:
  - key: requirements
    label: 1. Users, workflow and numbers
    prompt: "Who uses the platform, what decision it supports each week, and the numbers you size for (products, cases, runs, turnaround)."
    words: [80, 250]
  - key: architecture
    label: 2. Architecture
    prompt: "Datasets, the run engine, graders, the results store and how a change gets compared and approved. Say how it plugs into the release process."
    words: [150, 450]
  - key: grading
    label: 3. Grading and statistics
    prompt: "How cases are graded, how you trust the graders, and how you tell a real regression from noise."
    words: [100, 350]
  - key: risks
    label: 4. Failure modes, cost and rollout
    prompt: "What goes wrong with eval platforms over time, a rough cost per run, and how you'd roll the platform out to teams."
    words: [80, 300]
rubric:
  - name: Scoping the decision
    points: 15
    lookFor: "Frames the platform around the weekly ship or no-ship decision, names its users (prompt authors, reviewers, a release owner), and states numbers: products, cases per suite, runs per week, turnaround time."
  - name: Architecture and workflow
    points: 25
    lookFor: "Versioned datasets, versioned prompt and model configs, a run engine with concurrency and retries, pluggable graders, a results store keyed by config and case, side-by-side comparison of baseline and candidate, and a CI or release gate. Reasons for choices and at least one rejected alternative."
  - name: Grading quality
    points: 25
    lookFor: "Code-based checks where possible, LLM judges with written rubrics where not, judges validated against human labels with an agreement threshold, judge prompts and models versioned and pinned, and per-slice reporting rather than one average."
  - name: Statistics and noise
    points: 15
    lookFor: "Recognises that scores are noisy, compares baseline and candidate on the same cases, looks at flipped cases, estimates uncertainty from sample size (or uses repeated runs), and sets regression thresholds that account for it."
  - name: Failure modes, cost and adoption
    points: 20
    lookFor: "Names realistic problems (stale golden sets, overfitting to the suite, judge drift when the judge model changes, flaky tool-based cases, leaking eval data into prompts) with responses; gives a cost per run from token counts and prices and uses batch processing for cost; describes how teams adopt it."
passScore: 70
graderNotes: "The decision this platform supports is 'can this week's prompt or model change ship?'. Mark down answers that describe a dashboard without a gate, or that use an LLM judge without ever checking it against humans. Mark down a single overall score with no per-slice view. Reference math the learner may use: a 2,000-case suite with about 3,000 input and 500 output tokens per case on Claude Sonnet 5.5 is about $22 per run (2,000 x (3,000 x $2/M + 500 x $10/M)); an Opus 5.5 judge reading about 3,500 tokens and writing 300 per case adds about $40; the Message Batches API halves both, to about $31 per run. Accept other stated assumptions. For noise: at an 80% pass rate the 95% interval is roughly plus or minus 3.5 points with 500 cases and about 1.8 points with 2,000 cases; full marks on statistics does not require formulas, only a clear recognition that small differences can be noise and a sensible way to handle it (paired comparison, flipped-case review, repeated runs, or confidence intervals)."
---

Leo Martins, your fictional staff-engineer coach, frames this one as a customer engagement. "Pretend you're the applied AI engineer on an account. The customer's team ships a prompt or model change every week, and twice last quarter a change that looked fine broke something in production. They've asked you to design the eval platform. Anthropic's Applied AI Engineer posting lists building eval frameworks as part of the job (Official: the posting says so), so expect evals to come up in your loop." The prompt below is original practice, not a reported question.

## The prompt

> A fictional fintech, Halden Pay, runs four LLM features: a support assistant, a transaction-dispute classifier, a document extractor for onboarding, and an internal analyst copilot. About 25 engineers change prompts, tools or models every week. Releases go out on Thursdays. Design an evaluation platform that tells them, before each release, whether a change is safe to ship.

Answer in the four sections on the right, as you'd talk through it in a 45-minute round.

## How to approach it

1. **Start from the decision.** The platform exists to answer one question every Thursday: ship or don't ship? Who makes that call, and what do they need to see?
2. **Version everything.** Datasets, prompts, tool definitions, model IDs, grader prompts and grader models. A score is meaningless if you can't say exactly what produced it.
3. **Pick graders by case type.** Exact checks for the classifier and extractor (labels, fields, valid JSON). Rubric-based LLM judges for open-ended answers. A human-labelled sample to check the judges.
4. **Treat scores as measurements with error.** A 1-point drop on 300 cases may be noise. Compare on the same cases, look at which ones flipped, and size suites so real regressions show up.
5. **Do the cost math.** Cases times tokens times price times runs per week. Eval runs are work nobody is waiting on in real time, which makes them good candidates for batch processing.

Useful facts: Claude Opus 5.5 costs $4 per million input tokens and $20 per million output tokens; Claude Sonnet 5.5 is $2 and $10; Claude Haiku 5.5 is $0.10 and $0.50 for prompts up to 100K tokens. The Message Batches API processes requests asynchronously at half price. Structured outputs (`output_config.format` with a JSON schema) make judge verdicts easy to parse. For a pass rate p measured on n cases, the standard error is roughly the square root of p(1 − p)/n.

When you submit, Claude grades your design against the interviewer rubric below.
