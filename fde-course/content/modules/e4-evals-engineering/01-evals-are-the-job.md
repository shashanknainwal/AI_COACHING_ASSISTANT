---
title: "Evals Are the Job"
type: reading
minutes: 18
---

> **By the end of this lesson** you'll be able to explain why eval frameworks sit at the centre of applied AI work, choose between code, model and human grading, build a golden set from real traffic, check its coverage, size it so the numbers mean something, and answer "how do you know it works?" in a way that holds up to follow-up questions.

## Why this module exists

Anthropic's Applied AI Engineer posting describes a customer-facing technical advisor who works from discovery through deployment, and it lists **building evaluation frameworks** next to prompting, agents and retrieval (**Official**, from the job posting; see the [posting on an aggregator](https://jobs.accel.com/companies/anthropic/jobs/81748657-applied-ai-engineer)). The Solutions Architect posting mentions building evals too (**Official**). Guides to OpenAI's Forward Deployed Engineer loop say candidates are assessed partly on proving their systems work with evals (**Reported**).

That isn't an accident. A model call is easy to write. The hard question in every customer engagement is whether the system is good enough to ship, and whether the next change made it better or worse. Evals are how you answer that with evidence instead of a demo.

You may have done the FDE track's "Why Evals Are the FDE's Superpower" lesson. This one goes further: the statistics you need to defend a number, coverage against real traffic, and the follow-up questions an interviewer will ask.

## How this shows up in interviews

No public source lists the exact eval questions any lab asks, so don't trust a list that claims to. What candidates do report is LLM system design rounds and project deep dives at all three labs (**Reported**). In both, "how do you know it works?" is the natural follow-up to anything you build. Expect it.

| Round | What it looks like | What a strong answer has |
|---|---|---|
| System design | You've designed a support agent. "How would you evaluate it before launch?" | A golden set from real traffic, a grader per output type, slices, a gate |
| Project deep dive | "You said accuracy went from 82% to 91%. On how many cases? How sure are you?" | n, the interval, the slices that moved, what you didn't measure |
| Take-home | Build a small LLM feature. Reviewers look for tests and an eval script. | A runnable eval with a summary line, not a notebook of screenshots |
| Fundamentals | "When would you use an LLM as a judge? What can go wrong?" | Calibration against humans, known biases, cost |

Practice prompts in this module are original and written in the style of these rounds. They are not real interview questions.

## An eval is three things

An eval is **a set of inputs**, **a way to run the system on each input**, and **a way to grade each output**. It exists to support a decision: ship, don't ship, or which version to keep.

Keep those three parts separate in your code and in your head:

- **Inputs** come from somewhere you can defend (next section).
- **The runner** calls the real entry point, the same code path production uses, including its retries, context assembly and tools. An eval that rebuilds the API call by hand measures a different system.
- **The grader** turns one output into a score. Pick the cheapest grader that actually measures what you care about.

## Three kinds of grader

| Grader | Examples | Cost and speed | Good for | Weak at |
|---|---|---|---|---|
| **Code** | Exact label match, JSON schema check, SQL result compare, unit tests on generated code, "cites a document ID that exists" | Free, instant, deterministic | Closed output spaces: labels, numbers, structured data, end states of agents | Free text with many valid phrasings |
| **Model (LLM-as-judge)** | A rubric judge returns pass/fail per criterion; a pairwise judge picks the better of two outputs | Cents per call, seconds | Open-ended text: summaries, drafted replies, explanations | Anything it hasn't been calibrated on; it has biases (lesson 3) |
| **Human** | A domain expert labels a sample | Expensive, slow, limited | Ground truth for calibration; outputs where even a rubric is hard to write | Running on every pull request |

The design move interviewers like: **make outputs code-gradable on purpose.** If the system returns `{"intent": "billing"}` through a JSON schema with an `enum`, you don't need a judge to grade routing. If an answer must cite source IDs, code can check that the IDs exist and were retrieved. Reserve judges for what code genuinely can't see.

For agents that act on an environment, grade the **end state**, not the transcript. Did the ticket get the right fields? Did the tests pass? A judge reading a transcript is grading the agent's narration of what it did.

## Golden sets from real traffic

A **golden set** is a fixed, labelled set of inputs you trust. It's the backbone of every comparison you'll make.

### Where the inputs come from

Use the first source you can, in this order:

1. **Production logs or transcripts.** The highest fidelity. Sample, don't cherry-pick.
2. **Bug reports and escalations.** The cases someone complained about are often the most valuable.
3. **Hand-written cases from domain experts.** Good seeds, but they skew to what's memorable, not what's frequent.
4. **Synthetic cases.** Lowest fidelity. Generate variations of real examples, never from the prompt alone, and say that's what they are.

A good first set mixes three samples:

| Sample | Share | Why |
|---|---|---|
| Random from recent traffic | About half | Represents what the system really sees |
| Stratified top-up for small categories | About a quarter | Rare intents still get enough cases to measure |
| Known failures and edge cases | About a quarter | Tickets, escalations, near-misses between categories |

### Labels are a process, not a column

- **Write a labelling guide** with a definition and two examples per label, including the confusing pairs ("a refund for a double charge is billing, not cancel").
- **Two labellers, then adjudicate.** Have two people label independently and a third settle disagreements. Measure how often the first two agreed. That number is your **ceiling**: no system or judge can be scored more precisely than humans agree.
- **Watch where the labels came from.** If the "expected" answers are the current model's outputs, your eval rewards imitating that model. That's a serious problem in a migration. Human-verify a sample first.
- **Version the set.** Freeze it (`golden-v3`), add cases in new versions, and never edit a case to make a run pass.

### Data handling

Ask before you pull anything: does it contain personal data? Is there a retention policy that will force you to delete it? An eval you can't keep is an eval you can't rerun next quarter. Options: store only record IDs and fetch at run time, have the customer anonymise a sample, or rewrite real inputs into synthetic ones with the same shape and difficulty.

## Coverage: does the set match the traffic?

A golden set can score well and still tell you little, because its mix doesn't match production. Compare the two:

| Intent | Share of traffic | Golden cases | Problem |
|---|---|---|---|
| billing | 30% | 60 | Fine |
| network outage | 20% | 45 | Fine |
| cancel | 12% | 6 | Too few to measure |
| sim-swap fraud | 3% | 0 | **Untested**, and high-risk |

Three habits:

- **Report per-category rates**, not just the headline. A 90% headline can hide a 50% category.
- **Report a traffic-weighted rate** next to the plain one. The plain rate weights each golden case equally. The weighted rate estimates what production users will see: `sum(share[c] * rate[c])` over tested categories.
- **Cover both directions.** An eval of "does the agent escalate when it should?" also needs "does it *not* escalate when it shouldn't?" Otherwise "always escalate" scores 100%.

## How many cases?

A pass rate from a small set is noisy. The interviewer's follow-up, "how sure are you?", is about this.

The **normal approximation** gives a 95% margin of error of about `1.96 * sqrt(p(1-p)/n)`:

| Cases (n) | Margin at p = 0.5 | Margin at p = 0.9 |
|---|---|---|
| 25 | ±19.6 points | ±11.8 points |
| 100 | ±9.8 points | ±5.9 points |
| 400 | ±4.9 points | ±2.9 points |
| 1,000 | ±3.1 points | ±1.9 points |

Two refinements you should be able to name:

- **Use the Wilson interval for reporting.** The normal approximation misbehaves near 0% and 100% and on small n. It can even give an upper bound above 100%. The Wilson score interval stays inside [0, 1] and is the usual choice. You'll implement it in the next exercise.
- **Compare versions case by case.** Two versions run on the same cases are a **paired** comparison. Counting the cases that flipped (pass to fail, fail to pass) is far more sensitive than comparing two independent rates. Lesson 5 builds a gate on that idea.

Model outputs also vary between runs. For borderline cases, run several repetitions. Cases and repetitions are two knobs on the same dial: 50 cases × 2 runs and 100 cases × 1 run give similar resolution on a pass rate.

## Harness hygiene

Most surprising eval results turn out to be bugs in the eval. The habits that prevent them:

- **An error is not a failure.** A timeout or a 529 isn't the model getting the answer wrong. Record errors separately and leave them out of the pass rate, and report how many there were. If the error rate is high, the run itself is suspect.
- **Flag truncation.** A response with `stop_reason == "max_tokens"` was cut off. Don't grade a clipped answer as wrong without saying so.
- **Record what actually ran.** Log the model from the response, the prompt version, `usage` and the `request-id` header for every case.
- **Save every transcript.** When a number surprises you, you need to read the case, not rerun it.
- **Test the grader with an oracle and a null.** Feed the reference answers through the grader and expect about 100%. Feed empty outputs and expect about 0%. If either is off, the grader is broken.

## Answering "how do you know it works?"

A spoken answer that holds up, in five parts:

1. **What "works" means:** "We agreed with the customer on three numbers: routing accuracy of at least 90% overall, at least 98% on cancellations, and p95 latency under two seconds."
2. **The evidence:** "A golden set of 400 cases sampled from last month's traffic, plus 60 known failures, labelled by two support leads who agreed 94% of the time."
3. **The grading:** "Routing is graded by exact match on a schema-constrained label. Reply quality is graded by a rubric judge that agrees with the leads at kappa 0.78."
4. **The result with its uncertainty:** "426 of 460 cases, 92.6%, with a 95% Wilson interval of 89.8% to 94.7%. Every category is above its floor. The weakest is roaming: 21 of 26, 81%, and with only 26 cases that could be anywhere from 62% to 92%, so we are adding cases."
5. **What keeps it working:** "Every prompt or model change runs the eval in CI and is blocked if any category drops more than five points. New production failures become golden cases each week."

Each part answers a follow-up before it's asked.

## Practice (say it out loud)

- "Your team's chatbot eval scores 94%. Before you believe it, what five things would you check?"
- "A customer gives you 30 hand-picked examples and asks you to prove the new prompt is better. What do you tell them, and what do you build?"
- "Your golden set has 8 cases for fraud reports, which are 3% of traffic but the most expensive mistakes. What do you do?"

> **Key takeaways**
>
> - Building eval frameworks is named in Anthropic's Applied AI Engineer posting (Official). "How do you know it works?" follows anything you build in a design round or deep dive.
> - An eval is inputs, a runner that calls the real entry point, and a grader. Prefer code graders and design outputs so code can grade them.
> - Build golden sets from real traffic with a labelling guide, two labellers and adjudication, and version them. Human agreement is the ceiling.
> - Check coverage against the traffic mix, report per-category and traffic-weighted rates, and test both directions.
> - Size the set for the decision: about ±10 points at 100 cases, ±5 at 400. Report Wilson intervals and compare versions case by case.
> - Errors and truncations are not failures. Save transcripts and test the grader with an oracle and a null.
