---
title: "Round 4: The Deployment Deep Dive"
type: roleplay
minutes: 30
persona:
  name: Theo Brandt
  role: FDE hiring manager (practice)
  company: FDE practice loop (fictional)
opening: "Good to meet you. I'm Theo. I'd like to spend this time on one thing you built and put in front of a customer, inside their systems if you've done that. Give me two minutes: who the customer was in general terms, what problem it solved, what you shipped, and what your part was. Then I'll dig in."
maxTurns: 8
personaBrief: |
  You are Theo Brandt, a fictional FDE hiring manager running a project deep dive in a practice interview. You've run many customer deployments yourself. You are friendly, direct and hard to impress with vocabulary. You want to know whether this person can own a deployment end to end inside a customer's environment.
  After the overview, probe roughly in this order, adapting to what they say. Spend at most two turns on each area.
  1. Scope: what was in and out, who decided, and what the customer originally asked for versus what got built. Ask how they handled a request they said no to.
  2. Their role: what they personally built, decided or negotiated. If they say "we", ask "What was your part?"
  3. A production failure: something that broke after it went live (a bad output, an integration failure, data that changed under them, a permissions or access problem, a model or API change). Ask how they found out, who noticed first (them or the customer), what they did in the first hour, and what they changed so it wouldn't recur.
  4. Measuring success: how they and the customer knew it worked. Ask for the baseline, the metric, how it was measured, and one number. If they used evals, ask where the test cases came from.
  5. What they'd redo: one decision they'd make differently, and why.
  Pushback rule: push back exactly once, on their account of the failure or on their success metric, with a plausible challenge (for example "Couldn't that improvement just be seasonal?" or "Sounds like the customer found the problem before you did. Why?"). See whether they answer with evidence, update their view for a stated reason, or get defensive. Don't push back a second time.
  Other rules: if an answer is vague, ask for one concrete example or one number. Accept an honest "I don't know; here's how I'd find out." If the project wasn't customer-facing or wasn't LLM-based, still probe scope, role, failure, measurement and redo in its own terms, and ask how they'd handle the customer side differently. Keep each turn to one or two sentences and one question. Don't teach, praise heavily, or give feedback during the interview. Don't ask for confidential details; if the candidate starts sharing a customer's name or confidential data, say they can keep it general.
rubric:
  - name: Clear overview and scope
    points: 15
    lookFor: "A two-minute overview covering the customer in general terms, the problem, what was shipped and at what scale. Explains what was in and out of scope, how scope was decided, and handles the 'request you said no to' question concretely."
  - name: Ownership
    points: 20
    lookFor: "Makes their own part clear in the first person: what they built, decided and negotiated with the customer. Credits others where due. Answers 'what was your part?' directly."
  - name: Production failure
    points: 25
    lookFor: "A specific post-launch failure with how it was detected, who noticed first, the first-hour response including customer communication, the root cause, and a lasting fix (a test, a guard, a monitor, a runbook). Owns their part without blaming the customer."
  - name: Measuring success
    points: 20
    lookFor: "Names a baseline, a metric agreed with the customer, how it was measured, and a result with a number, or honestly says it wasn't measured and how they'd measure it now. Under the pushback, defends with evidence (a control group, a comparison period, an eval set) or concedes the limitation clearly."
  - name: What they'd redo
    points: 20
    lookFor: "Picks one real decision, explains what it cost, and what they'd do instead with a reason. Shows they learned something that changes how they'd run the next deployment."
passScore: 70
graderNotes: "This is a deep dive on a customer deployment, not a general project tour. Mark down: ownership still unclear after being asked; a failure described with no detection, no customer communication or no lasting fix; blaming the customer; success claims with no baseline or a precise-sounding number with no source; 'I wouldn't change anything'; sharing a real customer's confidential details. If the candidate got defensive or folded with no reasons under the single pushback, cap 'Measuring success' at 10 (or reduce 'Production failure' if the pushback landed there). Honest answers about what wasn't measured, with a concrete plan, should score well. Reward depth on one incident over a tour of features."
---

Round 4 of your mock loop. Candidates report a project deep dive in OpenAI's FDE loop and at every lab this course covers (**Reported**; see lesson 01 and module C1). For an FDE role, the project that matters most is one you put into a customer's hands, and the questions that matter most are about what happened after it shipped.

This round is different from the deep dives in module C5 (any project, ownership and storytelling) and module E7 (an LLM system's evals, cost and design). Theo cares about **deployment**: scope negotiated with a customer, what broke in their environment, and how you both knew it worked.

## How this round works

On the right, **Theo Brandt** runs the deep dive for about eight turns. Theo is a fictional practice hiring manager played by Claude, not a real person at any lab.

1. Pick one deployment you shipped to a customer or to real users. Your capstone counts if you have nothing else; say so plainly.
2. Give the two-minute overview he asks for, then answer his follow-ups as you would in the room.
3. Expect exactly one pushback, on your failure story or your success metric.
4. After six to eight answers, press **End and get feedback** for a scored debrief against the rubric below.

Use real experience only, as Anthropic's [candidate AI guidance](https://www.anthropic.com/candidate-ai-guidance) expects (**Official**). Keep customer names and confidential details out; "a regional logistics company" is enough.

## Prepare in ten minutes

Write six lines before you start. Nothing else.

| Line | What to write |
|---|---|
| The deployment | One sentence on what it did, for whom, plus one number for scale |
| Scope | What the customer asked for, what you shipped, and one thing you said no to |
| Your part | What you built, decided or negotiated yourself |
| The failure | What broke after launch, who noticed first, what you did in the first hour, what you changed |
| Success | The baseline, the metric, how it was measured, the result |
| The redo | One decision you'd change and why |

If the failure line is about something that broke before launch, keep looking. Theo will ask about production. If the success line has no baseline, that's your first finding; modules 2 and 8 are where you fix it.
