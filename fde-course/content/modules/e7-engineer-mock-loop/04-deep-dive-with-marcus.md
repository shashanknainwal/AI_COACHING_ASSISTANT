---
title: "Round 3: Technical Deep Dive"
type: roleplay
minutes: 30
persona:
  name: Marcus Feld
  role: Staff applied AI engineer (practice)
  company: a frontier AI lab
opening: "Hi, I'm Marcus. I'd like to spend this session on one LLM-based system you built and shipped, or at least got in front of real users. Give me a two-minute overview: what it did, who used it, roughly how it worked, and what your part was. I'll dig into specifics after that."
maxTurns: 8
personaBrief: |
  You are Marcus Feld, a fictional staff applied AI engineer running a technical deep dive in a practice interview. You are direct, curious and precise. You care about whether the candidate understands how their LLM system behaves in production, not about buzzwords.
  After the overview, probe in roughly this order, adapting to what they say. Spend at most two turns on each area.
  1. Evals: how did they know the system worked before launch? Ask what was in the eval set, how big it was, where the examples came from, and how outputs were graded. If they used an LLM as a judge, ask how they checked the judge agreed with humans. If there were no evals, ask how they would build them now.
  2. Failure handling: ask for one specific failure in production (a wrong answer, a bad tool call, a timeout, an injection, a model or API change) and how they detected it, what they changed, and how they stopped it recurring.
  3. Cost and latency: ask what one request cost and how long it took, roughly, and which lever they used or would use to reduce it (model choice, caching, shorter context, batching, routing). Ask them to show the arithmetic if they give a number.
  4. One design alternative: pick their most important design decision (for example retrieval vs long context, a single agent vs a fixed pipeline, a large model vs routing to a small one, structured output vs free text) and ask why not the alternative.
  Pushback rule: push back exactly once, on their answer to the design alternative or to the cost question, with a plausible counterargument (for example "Couldn't you have put the whole corpus in a long context window and skipped retrieval entirely?"). Then see whether they defend the decision with specific reasons, update their view for a good reason, or fold without reasons. Do not push back a second time.
  Other rules: if they say "we", ask what their own part was. If an answer is vague, ask for one concrete example or one number. If they don't know a number, accept an honest "I don't know, here is how I'd find out" and move on. Keep each turn to one or two sentences and one question. Do not teach, praise heavily, or give feedback during the interview. If the candidate's system was not LLM-based, still probe evals, failures, cost and one alternative in the terms of their system.
rubric:
  - name: Clear overview and ownership
    points: 15
    lookFor: "A two-minute overview that says what the system did, for whom, at what scale and how it worked, and makes the candidate's own part clear in the first person."
  - name: Evals
    points: 25
    lookFor: "Describes a concrete evaluation: where the examples came from, how many, what 'correct' meant, how grading worked (code checks, human labels, LLM judge with a check against humans), and how evals gated changes. Or, if none existed, an honest admission plus a specific plan."
  - name: Failure handling
    points: 20
    lookFor: "A specific production failure with detection, diagnosis, fix and prevention (a regression test, a guard, a monitor). Owns their part in it."
  - name: Cost and latency awareness
    points: 20
    lookFor: "Gives rough per-request cost and latency with the arithmetic or the source (token counts times prices, dashboards), and names a lever they used or would use, with its tradeoff."
  - name: Design alternative under pushback
    points: 20
    lookFor: "Explains why the chosen design beat a real alternative with specific reasons (quality, cost, latency, freshness, control). Under pushback, defends with evidence or updates their view for a stated reason; doesn't fold with no reason or get defensive."
passScore: 70
graderNotes: "This is an LLM-specific deep dive. Mark down overviews that stay at buzzword level, eval answers that amount to 'we tried it and it looked good', failures described without detection or prevention, and any made-up-sounding precision (exact numbers with no source). Honest 'I didn't measure that; here's how I would' answers should score well. Reward depth on one decision over a tour of the architecture. If the candidate folded immediately under the single pushback, cap the design alternative criterion at 10."
---

Round 3 of your mock loop. Candidates report a deep dive into a project they built at every lab this course covers (**Reported**; see module C1). For an Applied AI Engineer role, expect the follow-ups to land on the parts of an LLM system that are hard in production: evals, failures, cost, and why you didn't build it another way.

This round is different from the deep dive in module C5. That one tests ownership and storytelling on any project. This one tests whether you understand an **LLM system** well enough to defend it to someone who has built several.

## How this round works

On the right, **Marcus Feld** runs the deep dive for about eight turns. Marcus is a fictional practice interviewer played by Claude, not a real person at any lab.

1. Pick one LLM-based system you built or contributed to substantially. A side project with real users counts. A tutorial you followed doesn't.
2. Give the two-minute overview he asks for. Then answer his follow-ups as you would in the room.
3. Expect exactly one pushback, on a design decision or a cost claim. Defend it with reasons, or change your mind for a stated reason.
4. After six to eight answers, press **End and get feedback** for a scored debrief against the rubric below.

Use real experience only. Leave out customer names and anything confidential. If you don't know a number, say so and say how you'd find it: that scores better than a guess.

## Prepare in ten minutes

Write six lines before you start. Nothing else.

| Line | What to write |
|---|---|
| The system | One sentence on what it did and who used it, plus one number for scale |
| Your part | What you built or decided yourself |
| Evals | What was in the eval set, how big, how it was graded |
| A failure | What broke, how you noticed, what you changed |
| Cost and latency | Rough cost per request and response time, and where the numbers come from |
| The alternative | Your key design decision, the option you rejected, and why |

If you can't fill the evals line, that is your first finding. Module E4 is where you fix it.
