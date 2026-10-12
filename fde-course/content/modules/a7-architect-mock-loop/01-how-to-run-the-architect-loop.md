---
title: How to Run the Architect Mock Loop
type: reading
minutes: 15
---

> **By the end of this lesson** you'll be able to schedule a full practice loop for an Applied AI Architect or Solutions Architect role, run each round under realistic rules and timing, and record your scores the same day so you know which round to fix first.

## Why a full loop

Modules A1 to A6 trained the parts one at a time: discovery, deployment options, choosing the approach, proofs of concept, executive communication and reference architectures. An architect loop tests them together, in a different order than you learned them, with someone interrupting you. You present a recommendation before you've finished thinking. You design on a whiteboard while the clock runs and the requirements change. You talk to an anxious executive who doesn't care about your architecture diagram. A hiring manager asks about the deal you lost.

Grace Liu, your coach for this track (a fictional principal architect), puts it this way: "Nobody fails an architect loop for not knowing what RAG is. They fail because they can't commit to a recommendation, can't do the arithmetic out loud, or start pitching before they've listened."

This module is one complete practice loop. Run it once, honestly, and you get a scorecard that tells you where your next two weeks should go.

## What the loop is modelled on

Every hiring claim below carries a label: **Official** (the company says it), **Reported** (several independent candidate accounts agree) or **Anecdotal** (one or two accounts). Last checked 2026-10-08. Public information on architect loops is thinner than on engineering loops, so treat this table as a sketch and your recruiter's word as the truth.

| What we know | Label |
|---|---|
| Anthropic's "Solutions Architect, Applied AI" posting describes pre-sales architecture for large enterprises: a trusted technical advisor who fits Claude into the customer's stack, builds evals, designs scalable architectures, and works with Sales, Product and Engineering from discovery to deployment | Official (job posting) |
| Anthropic's onsite, across roles, is described in two parts, with a culture or values interview in the first part, and the second part may be cancelled if the first goes badly | Reported |
| A few guides call Anthropic's culture round the one that fails the most candidates; this rests on guides rather than independent candidate accounts | Anecdotal |
| Solutions-type roles at OpenAI include a case study presentation; one candidate describes a week-long take-home case followed by a panel discussing it from several angles | Anecdotal |
| A detailed, round-by-round account of Anthropic's Solutions Architect loop | We found none in public sources |

So this loop is built from two things: what the posting says the job is, and the round types that show up across applied loops (a case, a design, a customer conversation, technical depth, past customer experience, values). It doesn't reproduce any lab's actual questions. Every case, prompt and persona here is original and fictional.

## The six rounds

| Round | Lesson | Time | What it tests |
|---|---|---|---|
| 1a. Case preparation | 02: the Corvane field-service case | 60 min | Turning a messy brief into a recommendation, with numbers |
| 1b. Case presentation | 03: present to Sofia Lindqvist | 20–30 min | Leading with the answer, defending it under questioning |
| 2a. Design, written prep | 04: claims processing across three regions | 50 min | Designing for scale, residency and human decision rights |
| 2b. Design, live whiteboard | 06: Daniel Okonjo, Aldermoor design | 45 min | Asking for requirements, drawing while talking, adapting when constraints change |
| 3. Customer role-play | 05: Victor Hale, COO of a hospital network | 20–30 min | Discovery before pitching, risk, people, an honest next step |
| 4. Technical depth | 07: Anika Rao, depth interviewer | 25 min | Whether the fundamentals hold up three levels deep |
| 5a. Deal stories, written | 08: three deal stories | 45 min | Real pre-sales experience, told with numbers and ownership |
| 5b. Pre-sales deep dive | 09: Teodor Brandvold, hiring manager | 30 min | Whether your stories hold up when someone who has read them keeps asking |
| 6. Values and motivation | C5: "Live Practice: A Values Interview" | 30 min | Motivation and judgement |

Rounds 1a and 1b count as one round on the scorecard, and so do 2a and 2b, and 5a and 5b. Round 6 lives in module C5. If you haven't run it in the last two weeks, include it here: some guides describe the values round as a common place to fail (**Anecdotal**), and it costs half an hour.

Sofia Lindqvist, Daniel Okonjo, Victor Hale, Anika Rao and Teodor Brandvold are fictional practice personas played by Claude. They aren't real people at any lab or company, and nothing they say reflects a real interviewer's script. Every graded round, including the depth round, is scored by Claude against the rubric shown in its lesson.

## Schedule it

Put one of these in your calendar before you start. If your account has loop mode, start it from the course map before Round 1a: it locks hints and the tutor and records your first attempt in each round as the loop score.

**Option A: two sittings (about 3.5 hours each).**

| Day 1 | Time | Day 2 | Time |
|---|---|---|---|
| Round 1a: case preparation | 60 min | Round 5a: write deal stories (or the evening before) | 45 min |
| Break, away from the screen | 10 min | Round 3: customer role-play | 20–30 min |
| Round 1b: case presentation | 20–30 min | Round 4: technical depth | 25 min |
| Round 2a: design, written prep | 50 min | Break | 10 min |
| Break | 15 min | Round 5b: pre-sales deep dive | 30 min |
| Round 2b: design, live whiteboard | 45 min | Round 6: values (C5) | 30 min |
| | | Record scores (lesson 10) | 20 min |

**Option B: three shorter sittings.** Day 1: the case (1a and 1b). Day 2: the design (2a and 2b) and the depth round. Day 3: the deal stories, the deep dive, the customer role-play, values and scoring. Don't skip a later day because an earlier one went badly; real onsites are reported to run in two parts, and you need the whole picture (**Reported**).

Run the case at the time of day your real panel is likely to be. Presenting at 4pm after three other rounds is a different skill from presenting fresh at 9am.

## The rules

These mirror the official rules, so the practice transfers.

1. **No AI help during any round.** Anthropic's [candidate AI guidance](https://www.anthropic.com/candidate-ai-guidance) says take-homes and live interviews are done without AI unless you're told otherwise, and that using Claude to prepare and practise is encouraged (**Official**). In this loop Claude plays the panel and grades your work. That's practice. Asking any assistant to draft your case or your design is not.
2. **Write your own first draft.** The same guidance says first drafts of what you submit should be your own. If a real loop gives you a case in advance and allows AI for polishing, you'll still be asked to defend every number live. Practise as if no one will help you.
3. **Closed book, with one exception.** Our rule, not a reported lab rule: you may use a calculator or a spreadsheet for arithmetic. No searching, no notes from A1 to A6. Each lesson gives you the facts you're allowed to use.
4. **One attempt counts.** Your first submission in each round is your score. Retry as much as you like afterwards, but write the first score down first.
5. **Talk out loud.** In Rounds 2b and 4 especially; voice mode works in every role-play. Architect interviews are spoken. Narrating to an empty room feels odd, and it's the skill.
6. **Use real experience only.** In the deal stories, the deep dive, the values round and anywhere you cite your own past work, the guidance draws the line at invented experience. If you haven't run a proof of concept, say what you'd do, not what you "did". Adjacent experience is fine when you label it.

## Timing inside each round

These are our pacing targets, built from the format, not reported lab benchmarks.

| Round | Checkpoint |
|---|---|
| 1a. Case preparation | Read the case and write the one-sentence recommendation by minute 15. Numbers done by minute 35. All sections drafted by 55. |
| 1b. Presentation | Recommendation and the number that matters in the first 60 seconds. No answer to an interruption longer than 90 seconds. |
| 2a. Design, written | Requirements and numbers by minute 10. Regional topology by minute 25. Decision boundaries and evals by 40. Cost and rollout by 50. |
| 2b. Design, live | At least four clarifying questions before your first diagram. A first diagram by minute 12. Redraw within one turn of each constraint update. Final walkthrough in the last two minutes. |
| 3. Customer | At least three questions before you propose anything. A concrete next step before the end. |
| 4. Depth | 30 to 90 seconds per answer, out loud. Say "I don't know, here's how I'd find out" instead of guessing. |
| 5b. Deep dive | Two-minute stories, then specifics on demand. Name the moment, the people by role and the number. |

If you blow a checkpoint, note the minute and keep going. The note is more useful than the rescue.

## Recording scores

Every round produces a number out of 100, graded by Claude against the rubric in its lesson:

- **Round 1** combines your written case (lesson 02) and your presentation (lesson 03).
- **Round 2** combines the written design (lesson 04) and the live whiteboard (lesson 06).
- **Round 3** is the customer role-play (lesson 05).
- **Round 4** is the depth round (lesson 07).
- **Round 5** combines the deal stories (lesson 08) and the deep dive (lesson 09).
- **Round 6** is the values round in C5.

Your attempts are saved, and your progress page at [/learn/progress](/learn/progress) shows each round's first and latest scores. Still write each score down as soon as the round ends, with one sentence on what went wrong. Don't retry anything until all rounds are done: a retry before scoring turns a measurement into a lesson, and you need the measurement first.

> **Key takeaways**
>
> - Public detail on architect loops is thin. The loop here is built from the official posting plus round types reported across applied loops, and every claim is labelled.
> - Six rounds: a case (prepared and presented), an architecture design (written, then live on a whiteboard), a customer role-play, a technical depth round, a pre-sales experience deep dive and values.
> - No AI help during rounds, your own first draft, closed book except a calculator, first attempt counts.
> - Lead with the recommendation, do the arithmetic out loud, and listen before you pitch.
> - Every round is graded against a rubric. Write each score and one sentence about what went wrong as soon as a round ends.
