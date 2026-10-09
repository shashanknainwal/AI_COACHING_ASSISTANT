---
title: How to Run the FDE Mock Loop
type: reading
minutes: 15
---

> **By the end of this lesson** you'll be able to schedule a full practice loop for a forward deployed engineer role, run each round under rules that match the real ones, and score yourself the same day so you know which round to fix first.

## Why a loop, not more practice

You've practised the parts of this job one at a time: discovery in module 2, messy data in module 3, integrations in module 4, building on Claude in modules 6 and 7, evals in module 8, shipping in module 9, and a whole engagement in the capstone. An interview loop asks for all of it in a few days, under time pressure, with people watching. Strong candidates still lose loops on stamina, on a take-home that ran long and left them tired for the coding round, or on a deep dive about a deployment they haven't explained out loud since it shipped.

This module is one complete practice loop. Your coach is **Theo Brandt**, a fictional FDE hiring manager played by Claude. Run the loop once, honestly, and you get a scorecard that tells you where your next two weeks should go.

## What the loop is modelled on

Every hiring claim below carries a label: **Official** (the company says it), **Reported** (several independent candidate accounts agree) or **Anecdotal** (one or two accounts). Last checked 2026-10-08. Processes change, and your recruiter's word beats anything here.

| What we know | Label |
|---|---|
| Anthropic's Forward Deployed Engineer posting: builds production applications on Claude inside customer systems, including MCP servers, sub-agents and agent skills, with significant customer travel (the posting we read said 25 to 50 percent) and Python plus one other language | Official (job posting) |
| OpenAI FDE: a recruiter screen, then either technical screens or a take-home with a review call, then a virtual onsite of several interviews | Reported |
| OpenAI FDE onsite: practical, production-style coding, LLM system design, and a deep dive on a project you built | Reported |
| OpenAI FDE: interviewers assess scoping ambiguous problems, building systems around models, proving them with evals, and talking with non-technical stakeholders | Reported |
| One candidate describes a week-long take-home case study, followed by a panel that walked through it from several angles | Anecdotal |
| One candidate describes a coding screen where AI tools were allowed | Anecdotal |
| Anthropic, across technical roles: a progressive Python coding assessment of about four levels | Reported |

Public detail on Anthropic's FDE loop specifically is thin. So this module is built from two things: the reported shape of FDE loops elsewhere, and what Anthropic's posting says the job is. None of the prompts here are real interview questions. Every case, problem and persona is original.

## The rounds

| Round | Lesson | Time | What it mirrors |
|---|---|---|---|
| 1. Take-home case | 02: Marlow & Pike Distribution | 2 hours | The take-home or case study |
| 2. Practical coding | 03: a ticket-routing service | 75 min | The practical coding screen |
| 3. Customer call | 04: Ines Carvalho disputes your case | 30 min | The take-home review and the stakeholder skills interviewers assess |
| 4. Project deep dive | 05: Theo Brandt, a deployment you shipped | 30 min | The project deep dive |
| 5. LLM system design (optional) | E6 "Design It: A Support Agent at 10,000 Tickets a Day" | 45 min | The design round |
| 6. Values (optional) | C5 "Live Practice: A Values Interview" | 30 min | The culture or values round |

Rounds 5 and 6 live in other modules. Include them if you haven't run them in the last two weeks. The design round is reported in FDE loops (**Reported**), and several guides describe Anthropic's culture round as the one that fails the most candidates (**Reported**). Skipping them to save an hour is a poor trade if your real loop has them.

Round 3 depends on Round 1. Ines Carvalho is the customer from your take-home, and she has read your write-up. Do Round 1 first and keep your answer open during Round 3.

Theo, Ines and Marlow & Pike are fictional. They aren't real people or companies, and nothing they say reflects a real interviewer's script.

## Schedule it

Pick one format and put it in your calendar before you start.

**Option A: two sittings (recommended).**

| Day | Block | Time |
|---|---|---|
| 1 | Round 1: take-home case | 2 hours |
| 2 | Round 2: coding | 75 min |
| 2 | Break, away from the screen | 15 min |
| 2 | Round 3: customer call | 30 min |
| 2 | Break | 10 min |
| 2 | Round 4: deep dive | 30 min |
| 2 | Score everything (lesson 06) | 20 min |

Day 1 mirrors a take-home you do on your own time. Day 2 mirrors an onsite where the review of your take-home sits next to coding and a deep dive.

**Option B: one long day (about 5.5 hours).** Same order, with a 30-minute lunch break after Round 1. This is harder than most real loops, which is the point of choosing it.

Either way, run day 2 at the time of day your real onsite is likely to be.

## The rules

These mirror the official rules, so the practice transfers.

1. **No AI help during any round.** Anthropic's [candidate AI guidance](https://www.anthropic.com/candidate-ai-guidance) asks candidates to write first drafts themselves, says take-homes and live interviews are done without AI unless the company says otherwise, and encourages using Claude to prepare and practise (**Official**). In this loop, Claude plays Theo and Ines and grades your work. That's practice. Asking any assistant to help you answer is not. The tutor is off during the timed drill.
2. **If a real round allows AI, follow that round's rules.** One account describes an AI-enabled coding screen (**Anecdotal**). If your recruiter says tools are allowed, practise that way too, using the C3 drills. Never assume it.
3. **Timebox the take-home.** Two hours, then stop. Real take-homes are often longer (one account describes a week, **Anecdotal**), but the skill being tested is the same: scoping, judgement and clear writing. A cap stops you from polishing instead of deciding.
4. **Closed book for coding, with one exception.** Our rule, not a reported lab rule: you may open Python's official documentation during Round 2. No searching for solutions.
5. **One attempt counts.** Your first submission in each round is your score. Retry afterwards as much as you like, but write the first score down first.
6. **Real experience only.** The same guidance draws the line at inventing experience. For Round 4, use a deployment you actually worked on. If you haven't shipped one to a customer yet, use your capstone or your strongest internal project, say so plainly, and accept a lower score on the customer criteria.

## Timing inside each round

These are our pacing targets, built from the format, not reported lab benchmarks.

| Round | Checkpoint |
|---|---|
| 1. Take-home | Read the case and list your discovery questions by minute 20. Approach and scope by minute 60. Data and eval plans by minute 95. Risks and the demo by minute 120. |
| 2. Coding | Read Level 1 and sketch the data model by minute 8. Level 1 by minute 15, Level 2 by 33, Level 3 by 55, Level 4 by 75. |
| 3. Customer call | Ask before you defend: two questions before you restate your plan. Adjust the plan out loud when the new constraint lands. |
| 4. Deep dive | The overview in two minutes. Then short answers, each with one concrete example or one number. |

If you miss a checkpoint, write down the minute and keep going. The note is more useful than the rescue.

## Self-scoring, briefly

Every round produces a number out of 100.

- **Round 2** is scored from the levels you clear and when. The formula is in lesson 06.
- **Rounds 1, 3 and 4** are scored by Claude against the rubric shown in each lesson.

Write each score down as soon as the round ends, with one sentence on what went wrong. Don't look at the drill solution or retry anything until every round is done. A retry before scoring turns a measurement into a lesson, and you need the measurement first.

> **Key takeaways**
>
> - The loop mirrors the reported FDE shape: a take-home or case, practical coding, a customer-facing review, and a project deep dive, with optional design and values rounds.
> - Anthropic's FDE posting (Official) describes building production apps on Claude inside customer systems; public detail on its interview loop is thin, so every prompt here is original.
> - Run the take-home first; the customer call in Round 3 is about your take-home.
> - No AI help during rounds, a hard timebox, first attempt counts, real experience only.
> - Write each score and one sentence about what went wrong the moment a round ends.
