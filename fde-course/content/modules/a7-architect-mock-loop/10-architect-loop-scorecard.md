---
title: Your Architect Loop Scorecard and Fix Plan
type: reading
minutes: 20
---

> **By the end of this lesson** you'll be able to turn all six round scores into one honest verdict, read the depth round against a reference answer key, trace each weak signal to the module that fixes it, and follow a two-week plan that ends with a second loop on fresh material.

## Step 1: collect your scores

Every round is graded by Claude against the rubric in its lesson. Your attempts are saved, and [/learn/progress](/learn/progress) shows each lesson's first attempt, latest attempt and rubric lines over time. In loop mode, the first graded attempt in each round is marked as the loop score. Use that one, not your best retry.

## Step 2: revise the depth round with the answer key

Round 4 (lesson 07) is graded on the conversation. Anika picks the topics, so she may not have asked all ten classic questions below. Read your transcript, then use this key to check what she did ask and to revise what she didn't. A confident wrong answer costs more than "I don't know, here's how I'd find out".

What a strong answer includes:

1. **Why not put all 52,000 pages in the window?** About 500 tokens a page makes 26 million tokens, 26 times a 1-million-token window. Even a subset that fits is expensive: 1 million input tokens on Sonnet 5.5 is $2 per question, against a few cents with retrieval. Retrieval also gives citations to a document and revision, and handles weekly bulletin changes without reprocessing everything.
2. **Prompt caching for a CTO.** When many requests start with the same text (instructions, tool definitions, a reference document), the provider can reuse the work on that prefix. Cached reads on Sonnet 5.5 cost $0.10 per million tokens instead of $2, and cache reads don't count toward input-tokens-per-minute limits on most models. It saves nothing when the start of the prompt changes every time (a timestamp or user name at the top), when requests are further apart than the cache lifetime (five minutes by default, one hour as an option), or when the shared part is tiny.
3. **The arithmetic.** Sonnet 5.5: 10,000 × $2 / 1M = $0.02, plus 500 × $10 / 1M = $0.005, so $0.025 a request and $25 per 1,000. Haiku 5.5: $0.001 + $0.00025 = $0.00125 a request, $1.25 per 1,000. Twenty times cheaper; whether it's good enough is an eval question. The 500 output tokens assume `effort` is set explicitly: all three models think by default and thinking is billed as output (Sonnet 5.5 defaults to `high`, Haiku 5.5 to `medium`). If output triples to 1,500 tokens, Sonnet 5.5 is $0.035 a request.
4. **The tool-use flow.** You send tool definitions (name, description, input schema) with the request. If Claude decides to use one, the response ends with `stop_reason: "tool_use"` and a tool-use block with the tool name and input. The customer's code runs the tool, ideally after validating the input and checking permissions, and sends back a `tool_result` with the matching id. The loop continues until Claude answers. Claude never executes anything itself.
5. **91% on evals, useless to users.** The eval set doesn't look like real questions; the metric measures something users don't care about; latency or the interface gets in the way; the answers are right but not actionable in the workflow; a data source users depend on is missing. First move: read 20 real pilot transcripts.
6. **When fine-tuning wins.** A narrow, stable task where you need consistent format or style at high volume, or need a smaller, faster model to match a larger one, and you've already measured prompting and retrieval on a real eval and they've plateaued. It isn't a way to keep facts current. Confirm which models and platforms support fine-tuning before you promise it.
7. **Measuring faithfulness.** Break the answer into claims and check each against the cited passage. Check in code that every citation points to a real retrieved passage. Use an LLM judge for support, calibrated against human labels on a sample. Track unsupported claims as a rate.
8. **Injection through a document.** Treat retrieved text as data, never as instructions. The real protection is architectural: least-privilege tools, no outbound email or file-sharing tool without human approval, allowlists for destinations, and logging. Add injection cases to the eval set. A prompt saying "ignore injected instructions" helps but isn't a control.
9. **p95 under 3 seconds with 15,000-token prompts.** Cache the stable prefix (cheaper, and less work per request; the dynamic part still costs). Use a smaller model for the step (faster, maybe less accurate). Trim retrieved context (faster and cheaper, risk of missing the answer). Stream the response (feels faster, doesn't change the total). Lower `effort` (less reasoning).
10. **`effort` on Opus 5.5.** Levels from low to max control how much the model thinks before answering; the default on Opus 5.5 is medium (Haiku 5.5 also defaults to medium, Sonnet 5.5 to high). Higher effort tends to help hard reasoning and costs more tokens and more time: thinking is billed as output and happens before the first token. Thinking can't be switched off on Opus 5.5, so effort is the lever.

## Step 3: score every round out of 100

Three rounds combine two lessons. Our formulas, written for this course and not taken from any lab:

- **Round 1 = 0.4 × written case (lesson 02) + 0.6 × presentation (lesson 03)**
- **Round 2 = 0.4 × written design (lesson 04) + 0.6 × live whiteboard (lesson 06)**
- **Round 5 = 0.3 × deal stories (lesson 08) + 0.7 × deep dive (lesson 09)**

The live parts count more because a real panel hears you, not your document. A written case of 80 and a presentation of 60 gives 68.

Copy this into a note:

```text
ARCHITECT LOOP SCORECARD                            date: ________

Round                                 Score  Pass?  One sentence: what went wrong
1  Case (0.4 prep + 0.6 Sofia)        ___    ___    ______________________________
2  Design (0.4 written + 0.6 Daniel)  ___    ___    ______________________________
3  Customer (Victor Hale)             ___    ___    ______________________________
4  Technical depth (Anika Rao)        ___    ___    ______________________________
5  Pre-sales (0.3 stories + 0.7 Teo)  ___    ___    ______________________________
6  Values (C5)                        ___    ___    ______________________________

Weakest round: ____   Lowest rubric line in it: ________________
Depth topics where I hit the edge: ______________
```

A round passes at 70, the same pass mark the graded lessons use.

## Step 4: read the weakest round, not the average

An average hides the thing that sinks a loop. Candidates describe loops judged round by round, and at Anthropic a weak first part of the onsite is reported to cancel the second (**Reported**). One round at 45 isn't rescued by three at 90.

| What your card shows | Verdict | What to do next |
|---|---|---|
| Every round 70 or more | Ready to schedule | One more loop on fresh material a week before the real one |
| One round 50 to 69 | Close | The two-week plan below, aimed at that round |
| Two or more rounds 50 to 69 | Not yet | The two-week plan on the lower one, then a second cycle on the other |
| Any round under 50 | A gap, not a polish job | Go back to that round's modules first; plan on three to four weeks |

Look at the rubric line, not just the round. A design score of 64 made of 18/20 on the pipeline and 6/20 on residency is a deployment problem, not a design problem. The rubric-line trends on [/learn/progress](/learn/progress) make this easier to see across attempts.

## Step 5: map the weak signal to the fix

| Weak signal | Likely cause | Where to fix it |
|---|---|---|
| Round 1: no clear recommendation, or it came late | Thinking in options instead of decisions | A5 Executive Communication (one-pagers), A1 The Architect's Job (solution design docs) |
| Round 1: cost and value section thin, or numbers fell apart when Sofia asked | Cost and value modelling isn't automatic | A3 Choosing the Approach (total-cost models), C2 "Tokens, Context Windows and What They Cost" and "Exercise: Build a Cost Calculator" |
| Round 1: success criteria vague, or no "stop" result | Proof-of-concept design | A4 Proofs of Concept That Close |
| Round 1: rambled under interruption | Answers not rehearsed out loud | A5 role-plays, then rerun lesson 03 with a two-minute timer per answer |
| Round 1: lost the fine-tuning argument | Approach selection | A3 Choosing the Approach |
| Round 2: low residency or topology score, or fell into the Foundry-for-the-EU trap | Platform and data-handling knowledge | A2 Enterprise Deployment of Claude (lesson 01's residency table) |
| Round 2b: didn't adapt to the constraint updates, or the diagram didn't match the narration | Designing out loud under change | Rerun lesson 06 with a different first question; practise redrawing before explaining |
| Round 2: low pipeline or decision-boundary score | Pattern knowledge | A6 Reference Architectures (document processing in particular) |
| Round 2: low evals | No habit of proving quality | A4 Proofs of Concept That Close; E4 Evals as Engineering as deeper background |
| Round 3: pitched too early, missed hidden concerns | Discovery skills | A1 The Architect's Job (technical discovery) |
| Round 3: improvised compliance answers | Unsure what you can say about data handling | A2 Enterprise Deployment of Claude, then practise "I'll confirm that in writing" out loud |
| Round 3: no next step | Not closing | A5 Executive Communication |
| Round 4: low 'Technically correct' or several confident wrong answers | Fundamentals | C2 LLM Fundamentals Interviewers Probe, all of it |
| Round 4: low 'Depth under follow-up' on evals or injection | Retrieval quality and security | A6 Reference Architectures; E3 Retrieval at Scale and E2 Tool Use & Agents as deeper background |
| Round 4: low 'Numbers and cost' | Arithmetic isn't automatic | A3 lesson 04 (unit economics), C2 cost lessons |
| Round 5: stories didn't hold up, or numbers changed under questioning | Thin or unrehearsed deal stories | Rewrite lesson 08 with a specific moment and number per story, then rerun lesson 09 |
| Round 5: low 'Ownership of failure' or 'Technical and commercial judgement' | Defensiveness about losses; going along with sales pressure | A5 "Live Practice: Saying No Without Losing the Deal" and "Live Practice: Pressure From Your Own Account Executive" |
| Round 6: values | Unclear view on the lab's mission and tradeoffs | C4 Reading the Labs, C5 "Answering Mission Questions Honestly" |
| Rounds 1, 3, 5 or 6: stories feel thin | Story bank | C5 "Building Your Story Bank" and "Write It: Two Stories" |
| Any round: generic motivation came up | No specific reason written down | C1 "Write It: Why This Lab?" |

## Step 6: the two-week fix plan

About 60 to 90 minutes a day on weekdays, aimed at your weakest round. Swap in the modules from the table above.

| Day | Work | Time |
|---|---|---|
| 1 | Reread the weakest round's feedback. Write the three rubric lines you lost most points on. Pick the modules. | 45 min |
| 2–3 | Work through the first module's readings and exercises. Notes in your own words. | 90 min each |
| 4 | Redo that module's written or role-play lesson without looking at your earlier answer. | 60 min |
| 5 | A timed rep of the weak round on different material (see Step 7). Score it. | 60 min |
| 6–7 | The second module, or a deeper pass on the first if day 5 didn't move. | 90 min each |
| 8 | Fix your raw material: a one-page cost cheat sheet with current prices, a list of "things I'd confirm with the vendor", or your story bank. | 60 min |
| 9 | A second timed rep on different material. Compare it with day 5. | 60 min |
| 10 | Rest, or light review. Don't cram. | 0–30 min |

Then run a second full loop within the following week.

## Step 7: rerun on fresh material

Repeating the same case measures memory, not skill.

| Round | First loop | Second loop |
|---|---|---|
| 1. Case | Corvane field service | Write a case narrative for the Aldermoor claims platform instead: situation, recommendation, POC plan, costs, risks, ask. Present it to Sofia; she adapts to what you say. |
| 2. Design | Aldermoor claims, written then live | An A6 Reference Architectures design you haven't done, or E6 "Design It: A Support Agent at 10,000 Tickets a Day"; rerun lesson 06 opening with different questions, since the constraints land by turn, not by topic |
| 3. Customer | Victor Hale | The A5 role-plays with the skeptical CTO, the cautious CISO and the Veridane steering committee, or Victor again with a different opening move |
| 4. Depth | Anika Rao | Rerun lesson 07 and steer early toward the topics where you hit the edge; Anika follows where your answers go |
| 5. Pre-sales | Your three deal stories | Three different stories (another win, another loss, another stalled pilot), then lesson 09 again |
| 6. Values | C5 values interview | C5 again, with different stories |

You may also use Claude outside the course to run extra mock rounds, which Anthropic's [candidate AI guidance](https://www.anthropic.com/candidate-ai-guidance) encourages (**Official**). Ask for original cases and questions in the style of a round, never for "the real questions".

## When to stop practising

Stop adding loops when two in a row pass every round on fresh material. After that, more practice tends to make answers sound rehearsed, and a rehearsed case presentation is easy to spot. Spend the remaining days resting, reading what the lab publishes about its enterprise customers and deployment options, and writing the questions you want to ask your panel.

> **Key takeaways**
>
> - Every round is graded against its rubric; your attempts and rubric-line trends live on /learn/progress. Use the first attempt as the loop score.
> - Rounds 1, 2 and 5 combine a written part and a live part, weighted toward the live part, because the panel hears you, not your document.
> - In the depth round, a confident wrong answer costs more than "I don't know, here's how I'd find out".
> - Judge readiness by your weakest round and its lowest rubric line, not the average.
> - Each weak signal maps to an A-module or a shared-core lesson; fix the cause, not the round.
> - Two weeks, 60 to 90 minutes a day, then a second loop on material you haven't seen.
