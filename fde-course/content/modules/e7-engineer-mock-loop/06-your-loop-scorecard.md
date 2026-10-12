---
title: Your Loop Scorecard and Next Steps
type: reading
minutes: 15
---

> **By the end of this lesson** you'll be able to turn your round scores into one honest verdict, trace each weak signal to the module that fixes it, and follow a two-week plan that ends with a second loop on fresh material.

## Step 1: score every round out of 100

Rounds 2 to 6 and the values round already have a score from Claude's rubric. If you're signed in, the progress dashboard at `/learn/progress` fills these in automatically as you finish each graded round, and shows your weakest round and its lowest rubric line, so you can skip the copying below and check its numbers instead. Round 1 needs a formula. Use this one, written for this course (it is not how any lab scores its assessment):

| Round 1 result | Points |
|---|---|
| Each level cleared inside the 90 minutes | 25 |
| Each level cleared after the clock ran out | 10 |
| A level started but not cleared | 0 |

So Levels 1 to 3 inside the clock and Level 4 at minute 104 scores 85. Levels 1 and 2 inside the clock and nothing else scores 50.

Then fill in the card. Copy this into a note:

```text
MOCK LOOP SCORECARD                         date: ________

Round                           Score   Pass?  One sentence: what went wrong
1  Coding (registry, 02)        ___     ___    ______________________________
2  Design, live (Nadia, 03b)    ___     ___    ______________________________
3  Deep dive (Marcus, 04)       ___     ___    ______________________________
4  Exp. and goals (Elena, 05)   ___     ___    ______________________________
5  Customer session (05b)       ___     ___    ______________________________
6  Take-home panel (05d)        ___     ___    ______________________________
   Take-home README (05c)       ___     ___    (preparation; not a round)
V  Values (C5, optional)        ___     ___    ______________________________

Weakest round: ____   Lowest rubric line in it: ________________
Round 1 minute marks:  L1 ___  L2 ___  L3 ___  L4 ___
```

A round passes at 70, the same pass mark the graded lessons use.

## Step 2: read the weakest round, not the average

An average hides the thing that sinks a loop. Candidates describe loops judged round by round, and at Anthropic a weak first onsite part is reported to cancel the second (**Reported**). One round at 45 isn't rescued by three at 90.

| What your card shows | Verdict | What to do next |
|---|---|---|
| Every round 70 or more | Ready to schedule | Run one more loop on fresh material a week before the real one, to keep your timing sharp |
| One round 50 to 69 | Close | Two-week plan below, aimed at that round |
| Two or more rounds 50 to 69 | Not yet | Two-week plan on the lower one, then a second cycle on the other |
| Any round under 50 | A gap, not a polish job | Go back to that round's modules first; plan on three to four weeks before the loop |

Look at the rubric line, not just the round. A design score of 62 made of 19/25 on architecture and 4/20 on cost is a cost problem, not a design problem.

## Step 3: map the weak signal to the fix

| Weak signal | Likely cause | Where to fix it |
|---|---|---|
| Round 1: stuck on Level 3 or 4, rewriting earlier code | A Level 1 data model that couldn't grow | C3 "Data Models That Survive Level 4", then redo the C3 drills on the clock |
| Round 1: levels fail on edge cases you missed | Reading the spec too fast | C3 "How Progressive Coding Screens Work" (the first-ten-minutes routine) |
| Round 1: slow everywhere, right in the end | Python fluency: sorting, formatting, dict handling | C3 "Exercise: Ranking and Formatting Warm-Up", repeated until it's under 15 minutes |
| Round 2: low scoping, or 'Asked for the numbers' | Jumping to boxes before numbers | E6, the live design interviews (gateway, coding agent) where requirements only appear when you ask |
| Round 2: low 'Adapted to the new constraint' | Defending the first design instead of revising it | Rerun an E6 live design interview and say out loud what changes and what doesn't after each constraint |
| Round 2: low evals, or Round 3 evals | No habit of proving quality | E4 Evals as Engineering |
| Round 2: low context or architecture | Retrieval and context selection | E3 Retrieval at Scale, E2 Tool Use & Agents |
| Round 2 or 3: low cost and latency | Token math not automatic | C2 "Tokens, Context Windows and What They Cost" and "Prompt Caching and Latency", then E5 Production Concerns |
| Round 2 or 3: thin failure modes | Haven't run an LLM system in production | E2 (tool failures, traces) and E5 (rate limits, fallbacks, observability) |
| Round 3: folded under pushback | Decisions you made but never wrote down the reasons for | Write a one-page decision record for your project; rerun Round 3 |
| Round 3: low 'Depth on one decision' | You know the choice but not the measurement behind it | Answer the four drill-down questions (why, the alternative's result, how it was measured, how sure) for your key decision; E4 for the measurement habits |
| Round 5: missed root causes | Migration details not automatic | E1 and E2 (forced tool_choice, prefill, append-only history), E5 (max_tokens and thinking) |
| Round 5: low 'Explains to the non-expert' | Answering a decision-maker with detail instead of a decision | A5 Executive Communication (Architect track), and practise a one-sentence answer plus a date |
| Round 6: low evaluation rigour | Take-home eval too small, tuned on its own test cases, or no run-to-run check | E4 lessons 1 and 4, then rebuild the take-home eval with a held-out set |
| Round 3: "we" answers, unclear part | Ownership | C5 "Building Your Story Bank" and the C5 deep-dive practice |
| Round 4: generic motivation | No specific reason written down | C1 "Write It: Why This Lab?" |
| Round 4: weak conflict or customer story | Thin story bank | C5 "Building Your Story Bank" and "Write It: Two Stories" |
| Round 5: values | Unclear view on the lab's mission and tradeoffs | C4 Reading the Labs, C5 "Answering Mission Questions Honestly" |

## Step 4: the two-week fix plan

About 60 to 90 minutes a day on weekdays, aimed at your weakest round. Swap in your own modules from the table above.

| Day | Work | Time |
|---|---|---|
| 1 | Reread your weakest round's feedback. Write the three rubric lines you lost most points on. Pick the modules from the table. | 45 min |
| 2–3 | Work through the first module's readings and exercises. Take notes in your own words. | 90 min each |
| 4 | Redo one exercise from that module without looking at your earlier answer. | 60 min |
| 5 | A short timed rep of the weak round on different material (see below). Score it. | 60 min |
| 6–7 | The second module, or a deeper pass on the first if the day-5 score didn't move. | 90 min each |
| 8 | Fix your raw material: update your story bank, write the decision record for your project, or rebuild your cost cheat sheet. | 60 min |
| 9 | A second timed rep on different material. Compare it with day 5. | 60 min |
| 10 | Rest, or a light review. Don't cram. | 0–30 min |

Then run a second full loop within the following week.

## Step 5: rerun on fresh material

Repeating the same prompt measures memory, not skill. For the second loop, use material you haven't seen in a scored setting:

| Round | First loop | Second loop |
|---|---|---|
| 1. Coding | Prompt-template registry | C3 "Drill: An LLM Gateway Ledger", or the C3 feature-flag drill if it's been a month |
| 2. Design | PR review assistant (live, 03b) | E6 "Design Interview: A Multi-Tenant LLM Gateway" or "Design Interview: An Autonomous Coding Agent" |
| 3. Deep dive | Marcus, on project A | Marcus again, on a different project, or the C5 deep dive |
| 4. Experiences and goals | Elena | Elena again, with different stories from your bank |
| 5. Customer session | Ostrander Payroll | FDE track module 11's customer call, or Rafael again with a different diagnosis order |
| 6. Take-home panel | Sablewood take-home | A different take-home of your own choosing, built against the real API, with the same README sections |

The role-plays adapt to what you say, so repeating them with different stories is fair practice. You may also use Claude outside the course to run extra mock rounds, which Anthropic's [candidate AI guidance](https://www.anthropic.com/candidate-ai-guidance) encourages (**Official**). Ask it for original questions in the style of a round, never for "the real questions".

## When to stop practising

Stop adding loops when two in a row pass every round on fresh material. After that, more practice tends to make answers sound rehearsed. Spend the remaining days on rest, on the specific lab's published writing, and on the questions you want to ask your interviewers.

> **Key takeaways**
>
> - Score every round out of 100. For Round 1: 25 per level inside the clock, 10 per level after it. The progress dashboard at `/learn/progress` collects the rubric scores for you.
> - Judge readiness by your weakest round and its lowest rubric line, not the average.
> - Every weak signal maps to a specific module; fix the cause, not the round.
> - Two weeks, 60 to 90 minutes a day, then a second loop on material you haven't seen.
> - Stop when two loops in a row pass every round; then rest.
