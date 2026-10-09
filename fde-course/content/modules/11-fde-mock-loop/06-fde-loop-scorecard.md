---
title: "Your FDE Loop Scorecard and Fix Plan"
type: reading
minutes: 15
---

> **By the end of this lesson** you'll be able to turn your round scores into one honest verdict, trace each weak signal to the FDE or shared-core module that fixes it, and follow a two-week plan that ends with a second loop on fresh material.

## Step 1: score every round out of 100

Rounds 1, 3 and 4 already have a score from Claude's rubric. Round 2 needs a formula. Use this one, written for this course (it is not how any company scores its assessments):

| Round 2 result | Points |
|---|---|
| Each level cleared inside the 75 minutes | 25 |
| Each level cleared after the clock ran out | 10 |
| A level started but not cleared | 0 |

So Levels 1 to 3 inside the clock and Level 4 at minute 88 scores 85. Levels 1 and 2 inside the clock and nothing else scores 50.

Copy this card into a note and fill it in:

```text
FDE MOCK LOOP SCORECARD                        date: ________

Round                        Score  Pass?  One sentence: what went wrong
1  Take-home (Marlow & Pike) ___    ___    ______________________________
2  Coding (ticket router)    ___    ___    ______________________________
3  Customer call (Ines)      ___    ___    ______________________________
4  Deep dive (Theo)          ___    ___    ______________________________
5  Design (E6, optional)     ___    ___    ______________________________
6  Values (C5, optional)     ___    ___    ______________________________

Weakest round: ____   Lowest rubric line in it: ________________
Round 2 minute marks:  L1 ___  L2 ___  L3 ___  L4 ___
Round 1: minutes used ___ of 120, sections left thin: ________
```

A round passes at 70, the same pass mark the graded lessons use.

## Step 2: read the weakest round, not the average

Candidates describe loops judged round by round (**Reported**). One round at 45 isn't rescued by three at 90, so look at your lowest score first.

| What your card shows | Verdict | What to do next |
|---|---|---|
| Every round 70 or more | Ready to schedule | One more loop on fresh material a week before the real one |
| One round 50 to 69 | Close | The two-week plan below, aimed at that round |
| Two or more rounds 50 to 69 | Not yet | Two weeks on the lower one, then a second cycle on the other |
| Any round under 50 | A gap, not a polish job | Go back to that round's modules first; plan three to four weeks before the loop |

Then look at the rubric line inside the round. A take-home at 61 made of 18/20 on approach and 6/20 on evals is an evals problem, not a take-home problem.

## Step 3: map the weak signal to the fix

The FDE track (modules 1 to 10) is where the job skills live. The shared core (C1 to C5) is where the interview skills live. Most weak signals point to one of each.

| Weak signal | Likely cause | Where to fix it |
|---|---|---|
| Round 1: low framing, or building before asking | Discovery habit not automatic | Module 2, "Running a Discovery Call" and "Success Metrics, Baselines, and Acceptance Criteria" |
| Round 1: two-week scope tried to do everything | Saying no | Module 2, "Scope, Change Requests, and the Art of Saying No"; module 1, "Exercise: Prioritize a Customer Backlog" |
| Round 1: thin data plan | Haven't profiled messy customer data on the clock | Module 3, "Your First Hour with Customer Data", "Entity Resolution" and "Using Claude on Messy Data (and When Not To)" |
| Round 1: no integration story, or writes straight to the ERP | Integration patterns | Module 4, "Incremental Sync Jobs and Schema Mapping"; module 5, "Safe Access to Production Data" |
| Round 1 or 3: eval plan with no ground truth or thresholds | No habit of proving quality | Module 8, "Why Evals Are the FDE's Superpower" and "Release Gates, Noise and Nondeterminism"; module 10, "Exercise: Evaluate the Agent and Decide" |
| Round 1: approach vague about where Claude fits | Building with Claude | Module 6, "Choosing Models, Effort, and Latency Budgets"; module 7, "Workflows vs Agents, Guardrails and MCP" |
| Round 2: stuck at Level 3 or 4, rewriting earlier code | A Level 1 data model that couldn't grow | C3 "Data Models That Survive Level 4", then the C3 drills on the clock |
| Round 2: missed edge cases in the spec | Reading too fast | C3 "How Progressive Coding Screens Work" |
| Round 2: right in the end but slow | Python fluency | C3 "Exercise: Ranking and Formatting Warm-Up"; module 3 exercises, timed |
| Round 3: defended the plan without asking | Listening under pressure | Module 2, "Exercise: Analyze a Discovery Call Transcript"; module 2, "Stakeholder Mapping" |
| Round 3: froze or ignored the new constraint | Re-scoping live | Module 2, "Exercise: Change-Request Impact Calculator"; module 10, "Exercise: Scope the Engagement", redone with a constraint you add yourself |
| Round 3: weak close | No habit of ending with a next step | Module 1, "Your First Week on an Engagement"; module 10, "The Executive Readout" |
| Round 4: failure story with no detection or lasting fix | Haven't owned production | Module 9, "Incident Response and Graceful Degradation" and "Post-Mortems, Runbooks and Handoff" |
| Round 4: success claim with no baseline | Measurement | Module 2, "Exercise: Measure a Baseline from Raw Data"; module 8 |
| Round 4: "we" answers, unclear part | Ownership | C5 "Building Your Story Bank" and "Live Practice: The Project Deep Dive" |
| Round 4: no customer deployment to talk about | Experience gap | Finish module 10 end to end and use it honestly as your deep-dive project, then look for a real deployment to own |
| Round 5 or 6 weak | Design or values | E6 "How the LLM Design Round Works"; C4 Reading the Labs and C5 "Answering Mission Questions Honestly" |
| Any round: unsure what the real loop looks like | Process | C1 "The Loop, Round by Round" and "Your Prep Plan" |

## Step 4: the two-week fix plan

About 60 to 90 minutes a day on weekdays, aimed at your weakest round. Swap in the modules from the table above.

| Day | Work | Time |
|---|---|---|
| 1 | Reread your weakest round's feedback. Write down the three rubric lines that lost the most points. Pick one FDE module and one shared-core module from the table. | 45 min |
| 2–3 | The FDE module's readings and exercises. Notes in your own words. | 90 min each |
| 4 | Redo one exercise from that module without looking at your earlier answer. | 60 min |
| 5 | A short timed rep of the weak round on different material (see Step 5). Score it. | 60 min |
| 6–7 | The shared-core module, or a deeper pass on the first if the day-5 score didn't move. | 90 min each |
| 8 | Fix your raw material: write the decision record for your deployment, the failure story with its first hour, a one-page discovery checklist, or your data-profiling routine. | 60 min |
| 9 | A second timed rep on different material. Compare with day 5. | 60 min |
| 10 | Rest, or a light review. Don't cram. | 0–30 min |

Then run a second full loop within the following week.

## Step 5: rerun on fresh material

Repeating the same prompt measures memory, not skill. For the second loop, use material you haven't seen in a scored setting:

| Round | First loop | Second loop |
|---|---|---|
| 1. Take-home | Marlow & Pike | Module 10's NorthStar brief, answered in the same six sections under the same two-hour cap; or A7's Corvane case, written as an FDE's two-week plan rather than an executive narrative |
| 2. Coding | Ticket router | C3 "Drill: An LLM Gateway Ledger" or the E7 prompt-template registry, both at 75 minutes |
| 3. Customer call | Ines | A7's customer round with Victor Hale, or Ines again with a different take-home answer |
| 4. Deep dive | Theo, on deployment A | Theo again on a different deployment, or the C5 deep dive |

The role-plays adapt to what you say, so repeating them with different material is fair practice. You may also use Claude outside the course to run extra mock rounds, which Anthropic's [candidate AI guidance](https://www.anthropic.com/candidate-ai-guidance) encourages (**Official**). Ask it for original cases and questions in the style of a round, never for "the real questions".

## When to stop practising

Stop adding loops when two in a row pass every round on fresh material. After that, more practice tends to make answers sound rehearsed. Spend the remaining days resting, reading the company's own writing about how it deploys with customers, and writing the questions you want to ask your interviewers, for example how FDEs split time between customer sites and the core team, and how a deployment is judged a success.

> **Key takeaways**
>
> - Score every round out of 100. For Round 2: 25 per level inside the 75 minutes, 10 per level after.
> - Judge readiness by your weakest round and its lowest rubric line, not the average.
> - Job skills live in FDE modules 1 to 10; interview skills live in the shared core. Most weak signals need one of each.
> - Two weeks, 60 to 90 minutes a day, then a second loop on material you haven't seen.
> - Stop when two loops in a row pass every round; then rest.
