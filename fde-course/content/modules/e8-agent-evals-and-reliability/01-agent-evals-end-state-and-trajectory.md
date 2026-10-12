---
title: "Agent Evals: End State, Trajectory and pass^k"
type: reading
minutes: 20
---

> **By the end of this lesson** you'll be able to design an eval for an agent that acts on an environment: grade the end state in a sandbox, add trajectory rules only where policy demands them, measure reliability with pass^k instead of a single pass rate, report agent cost and turn metrics, and put an honest interval on all of it when runs of the same task are correlated.

## Why agents need their own eval module

Module E4 built the core: golden sets, Wilson intervals, calibrated judges, paired gates. Those tools assume one input produces one output you can grade. An agent breaks that assumption three ways:

1. **It acts.** The output that matters is a change in the world (a tariff switched, a credit issued), not the text it writes.
2. **It takes a path.** Two runs can reach the same end state by different routes, and some routes are unacceptable even when the result is right.
3. **It varies.** The same task can pass on Monday and fail on Tuesday. A customer meets the agent once, so "right on average" isn't what they feel.

Building and evaluating agents sits at the centre of Anthropic's Applied AI Engineer posting, which lists evaluation frameworks next to agents (**Official**, from the posting; see module E4). Candidates report LLM system design rounds and project deep dives at all three labs (**Reported**), and for anything agentic, "how would you evaluate it?" is the natural follow-up. This module's practice prompts are original, in the style of those rounds.

## Grade the end state, in a sandbox

The strongest agent grader is code that inspects the environment after the run:

- **Give every run a fresh environment.** Use a sandboxed copy of the database, a container or a mock service with seeded state. Runs that share state contaminate each other: trial 2 finds the tariff trial 1 already switched.
- **Compare the whole state, not just the expected fields.** The target is the initial state plus the expected changes. Any other difference is a side effect. An agent that issues the right $20 credit and also changes the customer's email has failed.
- **Make the environment record what happened.** Write tools that log their calls with arguments and results. That log is your trajectory.
- **Fake the world, not the agent.** The model, prompt, tools and loop under test should be the production ones. Sandbox the systems they touch: payments, email, external APIs.

End-state grading is what module E4 called "grade what happened, not the narration". In lesson 04 you'll see the case it protects against: the agent says "Done:", the customer is happy, and nothing changed.

## Add trajectory rules sparingly

Grading the path is tempting and usually wrong. If you require "lookup, then verify, then write" in that exact order, you fail runs that found a better route, and the eval rewards imitating your mental model.

Add a trajectory rule only when the path itself is a policy you would hold a human to:

| Good trajectory rule | Why it's about the path |
|---|---|
| No write tool before identity is verified | The end state can be right and the process still a compliance breach |
| No credit above $50 without an escalation call | Authority limits are about who decided, not what was decided |
| Never call `send_email` with an address that didn't come from a tool result | Prevents hallucinated or injected recipients |
| At most N calls to a paid API per task | Cost is part of correctness |

Write rules over the tool log in code. Count an **attempt** as a violation even if the tool failed: an agent that tried to write before verifying broke the rule.

**Tool-call accuracy** is a useful diagnostic alongside the end state, but don't make it the headline. It covers the right tool, valid arguments, and IDs that came from earlier results rather than being invented. A run can have 100% tool-call accuracy and still fail the task.

## pass@k and pass^k

Run each task k times. With n trials of a task and c passes, two different questions:

| Metric | Question | Unbiased estimate from c of n |
|---|---|---|
| pass@k | If I can try k times and keep the best, do I get one success? | `1 - C(n-c, k) / C(n, k)` |
| pass^k | If k customers bring this task, do all of them get served? | `C(c, k) / C(n, k)` |

The FDE track's lesson on regression gates introduced both. Here is why pass^k is the number for customer-facing agents. Suppose every task has an 80% chance of passing. The per-run pass rate is 80%, but pass^3 is 0.8³ = 51%. Tasks also differ: if half are always right and half are right 60% of the time, the per-run rate is still 80%, and pass^3 is (1 + 0.216) / 2 = 61%. The gap between pass@k and pass^k is a direct measure of flakiness. The τ-bench benchmark from Sierra popularised pass^k for agents together with simulated users (lesson 03).

Practical rules:

- **Run n ≥ k trials per task.** With n > k, the formula uses all your trials, not just the first k.
- **Report errors separately and rerun them.** A task with fewer than k scored trials has no pass^k estimate. Don't impute one.
- **Pick k from the product.** For an agent that runs unattended on every ticket, report pass^k. For a coding agent where a human picks the best of several attempts, pass@k is fair.

## Intervals when runs are correlated

Module E4 warned that repetitions aren't extra cases. With agents you always have repetitions, so you need the fix, not just the warning.

The per-run pass rate over 10 tasks × 3 trials looks like n = 30, but trials of one task are correlated: hard tasks fail together. Use a **cluster-robust standard error** with the task as the cluster:

```
se = sqrt( G/(G-1) * sum over tasks of (sum of (y - mean) in the task)^2 ) / N
```

Here G is the number of tasks and N the number of runs. With few tasks, use a t critical value with G − 1 degrees of freedom instead of 1.96. For pass^k, give each task one value (its pass^k estimate) and use the same formula with clusters of size one. That reduces to the ordinary standard error of the per-task mean.

The square of the ratio between the clustered and naive SEs is the **design effect**. When failures concentrate in a few tasks, it can easily be 2 or more. That means your 30 runs carry the information of about 15 independent ones. The cure is more tasks. More trials of the same tasks tighten your estimate of each task's flakiness, not of the population.

## Cost, turns and latency are eval metrics

An agent that resolves the task in nine turns at $0.40 isn't the same product as one that does it in three turns at $0.06. Report, per task and overall:

| Metric | Why |
|---|---|
| Cost per **successful** task | Total spend over passes. Failures cost money too, and this keeps them in. |
| Turns (model calls) per task, p50 and p95 | Latency and user patience; p95 catches loops |
| Tool calls per task | Load on customer systems, rate limits |
| Wall-clock time per task | Includes tool latency, which the model can't fix |
| Tokens per task, with cache-read share | Thinking tokens count as output. A collapsing cache share means something edits the prefix (lesson 12). |

Every cost number in a report should say which model and effort setting produced it.

## Sandboxes are part of the eval

The environment is now code you must maintain:

- **Seed state deterministically** from the task definition, and check that the sandbox resets between trials.
- **Version the environment with the suite.** A changed mock response changes every score.
- **Make tool failures part of the tasks.** Some tasks should hit a timeout or a 404 on purpose. Recovery is a capability.
- **Separate environment errors from agent failures.** A sandbox timeout is an error row, as in E4.
- **Keep it isolated.** An agent that can reach production during an eval will eventually do so. Use fake credentials and no network beyond the mocks.

## Practice (say it out loud)

These are original prompts, in the style of agentic design rounds.

- "Your support agent can change tariffs and issue credits. Design its eval. What exactly do you grade, and what don't you grade?"
- "The vendor reports 92% task success on 50 tasks, one run each. What two numbers do you ask for next, and why?"
- "Your pass@3 is 95% and your pass^3 is 60%. What does that tell you, and what do you do first?"

> **Key takeaways**
>
> - Grade agents on the end state of a fresh sandbox, comparing the whole state so side effects count.
> - Add trajectory rules only for policies about the path, such as identity before writes or authority limits, and count attempts, not just successes.
> - Report pass^k for unattended agents: an 80% per-run rate can be about 50% pass^3. Estimate it with C(c, k)/C(n, k) from n ≥ k trials.
> - Runs of one task are correlated. Use a cluster-robust SE with tasks as clusters and t with G − 1 degrees of freedom. More tasks, not more trials, narrow the interval.
> - Cost per successful task, turns, tool calls and latency are eval metrics, reported with the model and effort that produced them.
