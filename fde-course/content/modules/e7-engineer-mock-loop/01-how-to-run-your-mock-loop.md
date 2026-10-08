---
title: How to Run Your Mock Loop
type: reading
minutes: 15
---

> **By the end of this lesson** you'll be able to schedule a full practice loop for an Applied AI Engineer role, run each round under realistic rules and timing, and score yourself the same day so you know which round to fix first.

## Why a full loop, not more drills

By now you've practised each skill on its own: progressive coding in C3, LLM fundamentals in C2, design in E6, stories in C5. A real loop tests something none of those did: **doing all of them back to back, tired, with no second attempt.** People who are strong in every round alone still lose a loop on stamina, on a bad first round that rattles them, or on a deep dive about a project they haven't explained out loud in a year.

This module is one complete practice loop. Run it once, honestly, and you get a scorecard that tells you where your next two weeks should go.

## What the loop is modelled on

Every hiring claim below carries a label: **Official** (the company says it), **Reported** (several independent candidate accounts agree) or **Anecdotal** (one or two accounts). Last checked 2026-10-08. Processes change, and your recruiter's word beats anything here.

| What candidates describe | Label |
|---|---|
| Anthropic: a progressive Python coding assessment, about four levels in about 90 minutes | Reported |
| Anthropic: an onsite in two parts. Part 1 has coding, system design (often LLM infrastructure) and a culture interview. Part 2 covers your experience and goals plus a deep dive into a project you built. Part 2 may be cancelled if part 1 goes badly. | Reported |
| OpenAI forward deployed loops: practical coding, LLM system design and a project deep dive | Reported |
| Perplexity: domain-flavoured coding, AI system design and a hiring-manager deep dive | Reported |
| Anthropic's Applied AI Engineer posting: a customer-facing technical advisor from discovery to deployment who builds eval frameworks and pairs with customer engineers | Official (job posting) |

The pattern across labs is four kinds of round: practical coding, LLM system design, a deep dive on your own work, and motivation and values. This module mirrors that shape. It doesn't reproduce any lab's actual questions. Every prompt here is original.

## The five rounds

| Round | Lesson | Time | What it mirrors |
|---|---|---|---|
| 1. Practical coding | 02: a prompt-template registry | 90 min | The progressive coding screen |
| 2. LLM system design | 03: a pull-request review assistant | 45 min | The design round |
| 3. Technical deep dive | 04: Marcus Feld, an LLM system you built | 30 min | The project deep dive |
| 4. Experiences and goals | 05: Elena Sorokin, hiring manager | 30 min | The experience-and-goals or hiring-manager round |
| 5. Values (optional) | C5: "Live Practice: A Values Interview" | 30 min | The culture or values round |

Round 5 lives in module C5 and is optional here, because you may have run it recently. If you haven't run it in the last two weeks, include it. Several guides describe Anthropic's culture round as the one that fails the most candidates (**Reported**), so skipping it to save time is a poor trade.

Marcus and Elena are fictional practice interviewers played by Claude. They aren't real people at any lab, and nothing they say reflects a real interviewer's script.

## Schedule it

Pick one of two formats and put it in your calendar before you start.

**Option A: one sitting (about 4 hours).**

| Block | Time |
|---|---|
| Round 1: coding | 90 min |
| Break, away from the screen | 15 min |
| Round 2: design | 45 min |
| Break | 10 min |
| Round 3: deep dive | 30 min |
| Round 4: experiences and goals | 30 min |
| Score everything (lesson 06) | 20 min |

**Option B: two sittings, like a two-part onsite.** Day 1: coding, design and the values round (about 3 hours with breaks). Day 2: the deep dive and the experiences-and-goals round (about 1.5 hours), then scoring. This mirrors the reported Anthropic split. Don't skip day 2 if day 1 went badly: in practice, the later rounds are where you learn the most about your stories.

Either way, start Round 1 at the time of day your real interview is likely to be. If you're sharpest at 8am but the onsite starts at 1pm, practise at 1pm.

## The rules

These mirror the official rules, so the practice transfers.

1. **No AI help during any round.** Anthropic's [candidate AI guidance](https://www.anthropic.com/candidate-ai-guidance) says take-homes and live interviews are done without AI unless they tell you otherwise, and that using Claude to prepare and practise is encouraged (**Official**). In this loop Claude plays the interviewers and grades your answers. That's practice. Asking Claude, or any other assistant, to help you answer is not. The tutor is off during the timed drill for the same reason.
2. **Closed book, with one exception.** Our rule, not a reported lab rule: you may open Python's official documentation during Round 1. No searching for solutions, no notes from earlier drills. If your real assessment allows more or less, follow that.
3. **One attempt counts.** Your first submission in each round is your score. Retry as much as you like afterwards, but write the first score down first.
4. **Talk out loud during Rounds 1 and 2.** Interviewers in live rounds hear your reasoning. Narrating to an empty room feels odd, and it's the skill.
5. **Prepare only what a candidate would.** Before Round 3, write the five-line project summary that lesson 04 asks for. Before Round 4, nothing beyond knowing your own stories.
6. **Use real experience only.** The same guidance draws the line at inventing experience. If you haven't built an LLM system yet, don't make one up for Round 3: build one first (the E-track exercises are a start), or run the round on your strongest non-LLM project and accept the lower score on the LLM-specific criteria.

## Timing inside each round

These are our pacing targets, built from the format, not reported lab benchmarks.

| Round | Checkpoint |
|---|---|
| 1. Coding | Read all of Level 1 and sketch the data model by minute 10. Level 1 by minute 20, Level 2 by 40, Level 3 by 65, Level 4 by 90. |
| 2. Design | Requirements and numbers by minute 8. Architecture by minute 25. Evals by 33. Failure modes and cost by 45. |
| 3. Deep dive | The overview in two minutes. Then short, direct answers with a number where you have one. |
| 4. Experiences and goals | Answers under two minutes each. One concrete example per answer. |

If you blow a checkpoint, note the minute and keep going. The note is more useful than the rescue.

## Self-scoring, briefly

Every round produces a number out of 100:

- **Round 1** is scored from the levels you clear and when (the formula is in lesson 06).
- **Rounds 2 to 5** are scored by Claude against the rubric shown in each lesson.

Write each score on paper or in a note as soon as the round ends, with one sentence about what went wrong. Don't read the drill solution or retry anything until all rounds are done; a retry before scoring turns a measurement into a lesson, and you need the measurement first.

Lesson 06 shows how to combine the scores, which weak signal points to which module, and a two-week plan to fix your weakest round.

> **Key takeaways**
>
> - The loop mirrors the four kinds of round candidates report at every lab: practical coding, LLM system design, a project deep dive, and motivation and values.
> - Schedule it in one sitting or two, and run it at the time of day your real interview will be.
> - No AI help during rounds, closed book, first attempt counts, and real experience only.
> - Write each score and one sentence about what went wrong as soon as a round ends.
> - Every hiring claim here is labelled; confirm the details for your own loop with your recruiter.
