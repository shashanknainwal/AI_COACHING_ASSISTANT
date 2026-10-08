---
title: "Running a Fair Bake-Off"
type: reading
minutes: 18
---

> **By the end of this lesson** you'll be able to design a bake-off between models, prompts or vendors that a skeptical customer will accept: one frozen eval set, blind grading, cost per task and p95 latency next to quality, honest uncertainty, and a decision rule written before anyone sees results. You'll also know how to handle the customer's favourite competitor without losing credibility.

## Why bake-offs happen

Enterprise customers rarely evaluate one option. They compare: your platform against their incumbent vendor, two model tiers, a prompt against a fine-tuned model, or "build it ourselves" against a managed product. As the architect, you're often the person who designs that comparison, even when one of the candidates is yours.

That's an awkward position, and the only way through it is a process so fair that the result would stand even if you weren't in the room. If the customer suspects the test was rigged, a win is worth nothing. A fair loss, handled well, often keeps you in the account for the next project.

## The rules of a fair comparison

### 1. One eval set, frozen before anyone tunes

Every candidate runs on **the same cases**, drawn from the customer's real data, and the set is **frozen** before any candidate is tuned against it.

- **Split it.** A development set for iteration (everyone gets the same one) and a held-out test set used once, for the final run. Tuning on the test set is the most common way bake-offs go wrong, and it usually happens innocently.
- **Representative and hard.** Sample from recent real traffic, and deliberately include the hard and expensive cases (for example disputes involving fraud, or the long multi-page claims). A set of easy cases makes every candidate look the same.
- **Every candidate, every case.** If a vendor returns results on 36 of 40 cases, the missing four are the first thing to ask about. Skipped cases are often the hard ones. Count them as errors until they're run.

### 2. The same system boundary

Decide what's being compared. If one candidate gets the customer's retrieval pipeline and another gets a hand-curated context, you're comparing pipelines, not models. Write the boundary down: same inputs, same retrieved context (or retrieval is part of each system and each team builds its own), same output format, same tools.

Give each candidate a **comparable tuning budget**: the same development set and roughly the same number of days. Five weeks of prompt work on one side and an afternoon on the other measures effort, not capability.

### 3. Blind grading with a written rubric

Graders should not know which candidate produced an output.

- Strip names, formatting quirks and signatures. Shuffle the order.
- Use a written rubric agreed before grading, ideally by the customer's own experts (for example two dispute analysts, with a third settling disagreements).
- If you use an LLM judge, calibrate it against those human labels first and, for pairwise comparisons, run each pair in both orders to cancel position bias. The E4 module (*Evals as Engineering*) builds this.
- Grade **every output**, not a sample chosen after reading them.

### 4. Cost and latency next to quality

Quality alone doesn't decide a deployment. Report these for every candidate, measured the same way:

| Measure | How to report it | Common mistake |
|---|---|---|
| Quality | Pass rate with a 95% interval, per category if categories differ in value | One headline number on 40 cases |
| Cost | **Cost per task** in dollars, from measured tokens and list prices | Comparing price per token. Tokenizers differ, so the same text is a different number of tokens on different models. Claude Haiku 5.5's newer tokenizer, for example, counts the same text as about 30% more tokens than Claude Haiku 4.5's |
| Latency | p50 and p95 per task, under the same concurrency and region | Reporting the average, which hides the slow tail users actually feel |
| Errors | Error and timeout rate, plus missing cases | Leaving errors out of every number, so a flaky candidate looks clean |

Record the exact configuration of each run: model id, prompt version, and for current Claude models the `effort` setting, because effort changes both quality and spend. On Claude Opus 5.5, effort defaults to medium. A bake-off that runs one candidate at high effort and another at default isn't comparing like with like unless that's the point.

Two cost notes for the eval runs themselves. Large offline eval runs are a good fit for the Message Batches API, which halves the token price for work nobody is waiting on (results arrive asynchronously, within 24 hours). And a long shared system prompt can be cached across cases; check `usage.cache_read_input_tokens` to confirm hits.

## Statistical noise: when is a difference real?

This is the part customers most often get wrong, and the part interviewers like to probe.

| Cases | Approximate 95% margin on a pass rate near 85% |
|---|---|
| 40 | ±11 points |
| 100 | ±7 points |
| 200 | ±5 points |
| 400 | ±3.5 points |

On 40 cases, 34 passes (85%) has a Wilson interval of about 71% to 93%, and 35 passes (87.5%) about 74% to 95%. A one-case difference is noise. So is a three-case difference.

Ways to get a more honest answer:

- **More cases.** The cheapest fix by far, if the customer can label them.
- **Paired comparison.** Every candidate runs the same cases, so look at the cases where they **disagree**. If A beats B on 9 cases and B beats A on 2, that's real evidence. If it's 5 against 4, it isn't.
- **Repeat runs.** Model outputs vary from run to run, and the newest Claude models reject non-default sampling parameters such as `temperature`, so you can't tune the randomness away. Run borderline cases several times and report the spread.
- **A pre-committed tie rule.** Decide before the run what happens when candidates are within noise. A defensible default: **if quality is statistically tied, choose on cost, latency and operational fit, and say so.** That's the rule you'll implement in the next exercise, using overlapping intervals as a simple and conservative test. It's a heuristic: two intervals can overlap while a paired test still finds a real difference, so for a close, high-stakes call run the paired comparison too.

## Cherry-picking, in all its forms

Nobody sets out to cherry-pick. It creeps in. Watch for these:

| Form | How it sneaks in | The guard |
|---|---|---|
| Picking examples after seeing outputs | "Let's show the five best ones in the readout" | Show a random sample, plus the worst cases, chosen by rule |
| Tuning on the test set | "Just one more prompt tweak" after seeing test failures | Freeze the test set; iterate on the dev set only |
| Best of N runs | Rerunning until the number looks good | Pre-declare the number of runs; report all of them |
| Selective metrics | Reporting accuracy because latency looked bad | Report every agreed metric for every candidate |
| Silent exclusions | "We dropped the cases that timed out" | Errors and missing cases are counted and shown |
| Moving the bar | Raising or lowering the target after results | Targets are in the signed POC plan |

Hold yourself to the same rules you'd demand of a competitor. The customer will notice if you don't.

## The customer's favourite competitor

Sometimes a key stakeholder already prefers another vendor, or the incumbent is in the bake-off with a relationship you can't match. How to handle it:

1. **Include it, on equal terms.** Trying to keep the favourite out of the bake-off signals fear. Insist instead on the same set, the same rubric and the same boundary for everyone.
2. **Let the customer run it.** Results the customer's own team produced are hard to dispute. Offer to run your candidate the same way.
3. **Agree the decision rule first.** Constraints (cost cap, p95, compliance), the quality bar and the tie rule go in writing before the run. Once the rule is agreed, the result decides, not the loudest voice.
4. **Never trash the competitor.** Talk about your measurements, not their weaknesses. If they have a gap, the bake-off will show it.
5. **Ask about missing data, neutrally.** "Their results cover 36 of 40 cases. Can we get the other four, so the comparison is complete?" is a fairness question, not an attack.
6. **If they win fairly, say so.** Then look for where you're genuinely different: cost at scale, deployment options, security posture, a workload in the next phase. Your credibility is the asset that survives the deal. An architect known for honest bake-offs gets invited to design the next one.

## How this shows up in interviews

Expect bake-off questions inside case discussions and customer role-plays rather than as a separate round. Public accounts of architect loops are thin, so treat any specific format as **Anecdotal** and confirm with your recruiter. Interviewers are checking that you know what makes a comparison fair, that you can reason about noise without hand-waving, and that you'll stay honest when the result isn't in your favour.

### Practice prompts (original, in the style of a case round)

- "A customer's evaluation shows your model at 86% and a competitor at 84% on 50 examples. Their procurement lead says that settles it in your favour. What do you say?"
- "Design a bake-off between three models for an insurance claims summarizer. What do you measure, and how do you pick the winner?"
- "The customer's CTO prefers a competitor and wants to run the bake-off on examples he picked himself. How do you handle it?"
- "Your best-quality configuration costs three times the customer's budget per task. The cheapest one is two points lower on 40 cases. Which do you recommend?"

> **Key takeaways**
>
> - A bake-off is only worth winning if it's fair: one frozen, representative eval set, every candidate on every case, the same system boundary and a comparable tuning budget.
> - Grade blind, by a written rubric, ideally with the customer's own experts. Grade every output.
> - Report cost per task (not per token), p50 and p95 latency, and errors next to quality with intervals. Record model, prompt version and effort for every run.
> - On 40 cases the margin is about ±11 points. Use more cases, paired comparisons and repeat runs, and agree a tie rule before the results come in.
> - Cherry-picking creeps in through example selection, test-set tuning, best-of-N runs, selective metrics and silent exclusions. Guard against all of them on your own side too.
> - Include the customer's favourite competitor on equal terms, agree the decision rule first, never trash it, and concede a fair loss. Credibility outlasts the deal.
