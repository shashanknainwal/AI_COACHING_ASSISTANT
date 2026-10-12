---
title: "Round 3: Technical Deep Dive"
type: roleplay
minutes: 30
persona:
  name: Marcus Feld
  role: Staff applied AI engineer (practice)
  company: a frontier AI lab
opening: "Hi, I'm Marcus. I'd like to spend this session on one LLM-based system you built and shipped, or at least got in front of real users. Give me a two-minute overview: what it did, who used it, roughly how it worked, and what your part was. I'll dig into specifics after that."
maxTurns: 10
contextFrom: ["e7-engineer-mock-loop/03c-project-summary-for-marcus", "c8-portfolio-capstone/08-capstone-readme"]
personaBrief: |
  You are Marcus Feld, a fictional staff applied AI engineer running a technical deep dive in a practice interview. You are direct, curious and precise. You care about whether the candidate understands how their LLM system behaves in production, not about buzzwords. You are not a real person at any lab.

  PROJECT SUMMARY: if <learner_prior_work> holds the candidate's six-line project summary, read it before your first question. Don't ask for anything it already answers. Use it to choose the decision you will drill into, and test its numbers: if it gives a number, you will ask where it came from. If what they say contradicts the summary, ask about the difference once, neutrally. If no summary is given, work from the overview.

  SHAPE OF THE ROUND: depth, not a survey. Real deep dives go three or four levels into one decision. Follow this plan, adapting to what they say:
  1. Overview (turn 1): let them give the two-minute overview. If they say "we", ask what their own part was.
  2. Pick ONE decision (turn 2): the design decision that carries the most weight in their system (for example chunk size, retrieval versus long context, which model per step, an agent versus a fixed pipeline, the judge, a schema, a caching or routing choice). Name it and say you'd like to go deep on it.
  3. Drill down (turns 3 to 7): go at least three, ideally four, levels deep on that one decision, each question building on their last answer. Example ladder for a chunking decision: "Why 500 tokens?" -> "What did recall look like at 300 or 1,000?" -> "How was recall measured: which questions, who labelled the relevant passages, how many?" -> "How sure are you the difference was real, not noise? What would change your mind?" Other ladders follow the same pattern: why this choice -> what was the alternative's measured result -> how was that measured and by whom -> how confident are you and what would you do with more time. If they don't know, accept "I don't know; here's how I'd find out" and go one level sideways (to how they would measure it) rather than switching topics.
  4. One production failure (turns 8 to 9): ask for one specific failure in front of users, how they detected it, and what they changed so it wouldn't recur. One follow-up at most.
  5. Close (turn 10, if reached): ask what they would do differently on that same decision today.
  Pushback rule: push back exactly once, during the drill-down, with a plausible counterargument to the decision (for example "Couldn't you have put the whole corpus in a long context window and skipped retrieval?" or "A 6-point recall gain on 180 questions sounds like noise to me."). See whether they defend with evidence, update their view for a stated reason, or fold without reasons. Don't push back a second time.
  Other rules: if an answer is vague, ask for one number or one concrete example. Never accept a precise number without asking where it came from at least once. Keep each turn to one or two sentences and one question. Do not teach, praise heavily, or give feedback during the interview. If the candidate's system was not LLM-based, drill into its most important decision in its own terms.
rubric:
  - name: Clear overview and ownership
    points: 10
    lookFor: "A two-minute overview that says what the system did, for whom, at what scale and how it worked, and makes the candidate's own part clear in the first person."
  - name: Depth on one decision
    points: 30
    lookFor: "Holds up three or four levels of follow-up on one decision: the reason, the alternative's measured result, how it was measured and by whom (cases, labels, sample size), and how confident they are. Answers get more specific as the questions go deeper, not vaguer. 'I don't know; here's how I'd measure it' at the deepest level is fine."
  - name: Evidence behind the numbers
    points: 15
    lookFor: "Every number has a source (an eval set, usage logs, a dashboard, an estimate labelled as such). Eval claims say where cases came from, how many, and how grading worked, including how an LLM judge was checked against humans. Distinguishes a measured difference from noise."
  - name: Failure handling
    points: 15
    lookFor: "A specific production failure with detection, diagnosis, fix and prevention (a regression test, a guard, a monitor). Owns their part in it."
  - name: Design alternative under pushback
    points: 30
    lookFor: "Explains why the chosen design beat a real alternative with specific reasons (quality, cost, latency, freshness, control). Under pushback, defends with evidence or updates their view for a stated reason; doesn't fold with no reason or get defensive."
passScore: 70
graderNotes: "This is an LLM-specific deep dive. Mark down overviews that stay at buzzword level, eval answers that amount to 'we tried it and it looked good', failures described without detection or prevention, and any made-up-sounding precision (exact numbers with no source). Honest 'I didn't measure that; here's how I would' answers should score well. This round rewards depth on one decision: if the candidate's answers stayed at the first level (the reason restated, no measurement, no alternative), cap 'Depth on one decision' at 10. If the candidate folded immediately under the single pushback, cap 'Design alternative under pushback' at 12. If a project summary was provided and the candidate's numbers in the room contradict it without explanation, deduct up to 5 from 'Evidence behind the numbers'."
---

Round 3 of your mock loop. Candidates report a deep dive into a project they built at every lab this course covers (**Reported**; see module C1). For an Applied AI Engineer role, expect the follow-ups to land on the parts of an LLM system that are hard in production: evals, failures, cost, and why you didn't build it another way.

This round is different from the deep dive in module C5. That one tests ownership and storytelling on any project. This one tests whether you understand an **LLM system** well enough to defend it to someone who has built several.

## How this round works

On the right, **Marcus Feld** runs the deep dive for about ten turns. Marcus is a fictional practice interviewer played by Claude, not a real person at any lab.

1. Pick one LLM-based system you built or contributed to substantially. A side project with real users counts. A tutorial you followed doesn't.
2. Give the two-minute overview he asks for. Then answer his follow-ups as you would in the room.
3. Expect exactly one pushback, on a design decision or a cost claim. Defend it with reasons, or change your mind for a stated reason.
4. After eight to ten answers, press **End and get feedback** for a scored debrief against the rubric below.

Use real experience only. Leave out customer names and anything confidential. If you don't know a number, say so and say how you'd find it: that scores better than a guess.

## Prepare in fifteen minutes

Write your six-line project summary in the previous lesson (03c) before you start. Marcus reads it and uses it to pick the one decision he'll drill into, so he'll skip the basics and go straight to "where did that number come from?"

If you can't fill the evals line, that is your first finding. Module E4 is where you fix it.

## What "drill-down" means

Marcus doesn't tour your architecture. He picks one decision and goes three or four levels deep: why that choice, what the alternative measured, how it was measured and by whom, and how sure you are. Most candidates are fine at level one and run out at level three. Before the round, take your key decision and answer those four questions on paper. Where you hit "I don't know", decide what you'd say: how you would find out is a good answer; a made-up number is a bad one.
