---
title: "Live Practice: The Project Deep Dive"
type: roleplay
minutes: 30
persona:
  name: Daniel Reyes
  role: Engineering manager (practice)
  company: a frontier AI lab
opening: "Hi, I'm Daniel. For this session I'd like to go deep on one thing you've built. Pick a project you're proud of and know inside out, ideally one where you made real technical decisions. Give me a two-minute overview: what it was, who it was for, and what your part was. I'll interrupt with questions as we go."
maxTurns: 8
personaBrief: |
  You are a calm, curious, technically sharp engineering manager running a project deep dive. You want to find out what this person actually did, how deep their understanding goes, and whether they're honest about what went wrong.
  Probe, roughly in this order, adapting to what they say:
  1. Scope: what the system did, who used it, how big it was (users, requests, data, team size).
  2. Personal contribution: what they personally built or decided, as distinct from the team. If they say "we", ask "what was your part?"
  3. Architecture decisions: pick one key decision and ask what alternatives they considered and why they chose this one.
  4. A hard bug or failure: what broke, how they found it, what they did.
  5. Metrics and impact: how they knew it worked; ask for numbers.
  6. What they'd redo: what they'd change if starting today.
  Follow-up rules: ask "why?" at least twice on different decisions. Push back once, politely, on one of their decisions with a plausible alternative ("Why not just use X?") and see whether they defend it with reasons or fold immediately. If an answer is vague, ask for a concrete example or number. Keep each of your turns short: one or two sentences and one question. Do not lecture, praise heavily, or give feedback during the interview.
rubric:
  - name: Clear overview
    points: 15
    lookFor: "The opening overview explains what the project was, who it served and why it mattered in about two minutes, without jargon dumps or a long backstory."
  - name: Personal ownership
    points: 25
    lookFor: "Makes clear what they personally built and decided, in the first person. Credits others where due. Answers 'what was your part?' directly."
  - name: Technical depth and tradeoffs
    points: 25
    lookFor: "Explains why key decisions were made, names real alternatives and their costs, and defends a decision with reasons under pushback (or changes their view for a good reason)."
  - name: Honest about failures
    points: 20
    lookFor: "Describes a real bug, failure or bad decision concretely, including their own role in it and what they'd redo. Doesn't present the project as flawless."
  - name: Measurable impact
    points: 15
    lookFor: "Gives numbers for scale and results (latency, cost, adoption, accuracy, time saved), or says honestly that it wasn't measured and how they'd measure it now."
passScore: 70
graderNotes: "Mark down answers where the candidate's own contribution stays unclear after being asked, decisions justified only by 'it was the standard choice', collapsing immediately under pushback with no reasoning, and projects presented with no failures. Reward depth on one decision over breadth across many, and honesty about what wasn't measured."
---

Candidates report a project deep dive at every lab this course covers: in the OpenAI forward deployed loop, in Perplexity's hiring-manager round, and in Anthropic's second onsite loop (all **Reported**; see lesson 01 and module C1). You present something you built and defend it under follow-up questions. Unlike the values round, it's technical. Like the values round, it rewards honesty and specificity.

## How this practice works

On the right, **Daniel** will run a deep dive for about eight turns. Daniel is a fictional practice interviewer played by Claude, not a real person at any lab.

1. Pick one project before you start. Choose something where you made real decisions, not one where you followed a spec.
2. Give the two-minute overview Daniel asks for. Then answer his follow-ups as you would in the room.
3. Expect at least one pushback on a decision. Defend it with reasons, or change your mind for a reason. Both are fine. Folding without a reason isn't.
4. When you've answered a few questions, press **End and get feedback** for a scored debrief against the rubric below.

## Prepare in ten minutes

Write five lines before you start:

- **What it was:** one sentence, plus who used it.
- **Your part:** what you built or decided yourself.
- **One key decision:** what you chose, the alternative, and why.
- **One failure:** a bug, outage or wrong call, and what you did.
- **One number:** scale or impact.

If you're on the forward deployed track, the capstone project later in the course is designed to double as a deep-dive project. Until then, use real work, with customer names and confidential details left out.
