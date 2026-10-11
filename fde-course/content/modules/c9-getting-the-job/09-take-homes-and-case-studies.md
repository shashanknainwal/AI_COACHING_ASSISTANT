---
title: "Take-Homes and Case Studies (Review a README)"
type: written
minutes: 40
sections:
  - key: verdict
    label: 1. Verdict
    prompt: "Would this submission get the candidate to the review call? One or two sentences, with the main reason."
    words: [20, 80]
  - key: problems
    label: 2. The problems, ranked
    prompt: "The most serious problems with the submission, most serious first. For each, say why a reviewer would care."
    words: [100, 350]
  - key: strengths
    label: 3. What to keep
    prompt: "Two or three things the candidate did well that should survive a rewrite."
    words: [30, 150]
  - key: panel
    label: 4. Three panel questions
    prompt: "Three questions a review panel would ask about this README, and what a strong answer would contain."
    words: [60, 250]
rubric:
  - name: Finds the disqualifying issues
    points: 30
    lookFor: "Flags the two issues that could end the process on their own: the README says an AI coding assistant wrote most of the code although the brief said no AI tools, and an .env file with an API key is committed. Explains why each matters (breaking the assessment's stated rules; leaking a secret)."
  - name: Judges the evaluation honestly
    points: 25
    lookFor: "Spots that '100% accuracy' on 12 hand-picked notes, written by the candidate and also used to tune the prompt, shows almost nothing: too few cases, no edge cases, no held-out set, no interval or counts per field. Notes the cost figure ignores thinking tokens and isn't from measured usage."
  - name: Spots scope and time problems
    points: 15
    lookFor: "Notices the time box was blown (about 11 hours against a 4-hour brief) and the time went to a web UI the brief didn't ask for, while the eval and error analysis were thin. Notes 'production ready' is unsupported and that there's no decision log or rejected alternatives."
  - name: Fair about strengths
    points: 10
    lookFor: "Credits real strengths: a clear problem statement, structured outputs with a schema, a sensible model and effort choice with a reason, an honest limitations line about clinical review."
  - name: Panel questions that probe
    points: 20
    lookFor: "Three questions a reviewer would really ask (how the eval set was built and kept separate from tuning, how the AI-use statement squares with the rules, what was cut to fit the time box, how cost was measured, what fails), each with what a strong answer would contain."
passScore: 70
graderNotes: "The README is fictional and deliberately flawed. Cap 'Finds the disqualifying issues' at 12 if the learner finds only one of the two issues (AI-written code against the brief's no-AI rule; the committed .env with an API key), and at 0 if they find neither. If the learner praises the 100% accuracy figure or calls the eval adequate, cap 'Judges the evaluation honestly' at 5. A verdict that the submission would go through to the review call without reservation should lose 5 points from 'Finds the disqualifying issues' unless the learner explains a reason that survives the two issues. Reward ranking: rule-breaking and the leaked key belong above polish issues. Don't reward length; a sharp, ranked list beats an exhaustive one."
anchors:
  - label: weak
    expect: [0, 45]
    answer:
      verdict: "Yes, this looks strong. 100% accuracy is impressive and there's even a UI."
      problems: "The README could be formatted better and the UI could look nicer. Maybe add more comments to the code. It could also use a diagram of the architecture so the reviewers understand it quickly."
      strengths: "Great accuracy, nice UI, uses a good model, and the candidate clearly worked hard on it."
      panel: "What would you add next? What was the hardest part? Did you enjoy the project?"
  - label: strong
    expect: [75, 100]
    answer:
      verdict: "No. Two things would likely end it before the eval is even read: the README says an AI assistant wrote most of the code when the brief said no AI tools, and a .env with an API key is in the repo."
      problems: "1. AI use against the brief. The brief said no AI tools; the README says Claude Code wrote most of it. That's breaking the assessment's rules, not a style issue. 2. Committed .env with a live key. A security failure in a customer-facing role; the key must be revoked. 3. The eval proves nothing: 12 notes the candidate wrote, also used to tune the prompt, '100% accurate'. No held-out set, no edge cases (abbreviations, missing fields, two medications), no per-field counts. 4. Time box blown: about 11 hours on a 4-hour brief, mostly on a React UI nobody asked for. 5. Cost is a guess: ignores thinking tokens billed as output, not from usage. 6. 'Production ready' with no review step for clinical content, no decision log, no rejected alternatives."
      strengths: "A clear problem statement; structured output with a schema rather than free text; model and effort choice with a reason; an honest line that clinicians must review summaries."
      panel: "1. 'How did you build the eval set, and how did you keep it separate from prompt tuning?' Strong: explains the leak, proposes 50+ held-out cases with edge cases and per-field counts. 2. 'The brief said no AI tools; walk me through how you built this.' Strong: honest, owns it, doesn't minimise. 3. 'What did you cut to fit four hours, and what would you do with another week?' Strong: drops the UI, spends the time on eval and error analysis, measured cost from usage."
---

Hana's note: *"A friend of a friend asked me to look at his take-home before the review call. I'd like your read first. Be specific, and rank what matters."*

Hana, the candidate and Pellwater Clinics are all fictional. The README below is invented for this exercise and deliberately flawed. Claude grades your review.

## What's known about take-homes

| Fact | Label |
|---|---|
| OpenAI's forward deployed loop: two 60-minute screens, or a take-home with a review call. | Reported |
| One candidate describes a week-long case study followed by a panel walking through it from several angles. | Anecdotal (module C1) |
| At Anthropic, take-homes are done without AI assistance unless the company says otherwise. | **Official** ([candidate AI guidance](https://www.anthropic.com/candidate-ai-guidance)) |

Module 11 (FDE mock loop) and E7 lessons 5c–5d give you a full take-home and panel to do yourself. This lesson teaches the strategy and trains the reviewer's eye, which is the fastest way to see your own work the way a panel will.

## Strategy (General)

The rest of this section is general practice from engineering hiring, not a lab's stated process.

1. **Read the rules first.** Time box, allowed tools, language, how to submit. If anything is unclear, especially AI use, ask before you start. Breaking a stated rule ends most processes regardless of quality.
2. **Scope down in writing.** List what you'll build and what you won't. A reviewer would rather see a small thing done properly than a large thing half-done.
3. **Respect the time box.** If the brief says four hours, spend about four, and say so. Going far over isn't impressive; it hides whether you can prioritise.
4. **Spend real time on proof.** Tests for the code, an eval for the model behaviour, honest numbers. For LLM take-homes this is usually what separates candidates.
5. **Keep a decision log.** Three or four decisions, the alternative you rejected, and why. It becomes your script for the review call.
6. **Write the README last, but budget for it.** About an hour of a four-hour brief is reasonable. Use the structure from E7 lesson 5c.
7. **Prepare for the walkthrough.** Expect "why this and not that?", "what fails?", "what would you do with a week?" and "how did you measure that?" Rehearse a five-minute tour.
8. **Clean up before you submit.** No secrets in the history, no customer data, runs from a clean clone with one command.

## The submission to review

The brief (fictional): *"Pellwater Clinics wants to summarise free-text appointment notes into structured fields (reason for visit, medications mentioned, follow-up needed, follow-up date). Build a prototype on the Claude API and show how well it works. Time box: 4 hours. No AI coding tools for this assessment. Submit a repo with a README."*

The candidate's README:

```text
# Pellwater Note Summariser

## Problem
Clinic staff spend time re-reading appointment notes to find follow-ups. This tool
turns a free-text note into structured fields so follow-ups aren't missed.

## How it works
- Claude Sonnet 5.5 with structured outputs (JSON schema for the four fields).
  Effort set to low: the task is extraction, not reasoning, and low keeps latency down.
- React front end with upload, history view and dark mode.
- Flask backend. .env file included for convenience so reviewers can run it straight away.

## Results
Tested on 12 example notes I wrote. After tuning the prompt on them, it now gets
100% accuracy. Production ready.

## Cost
About 500 input tokens and 100 output tokens per note, so roughly $0.002 per note.

## Notes
- Claude Code wrote most of the code; I reviewed and fixed it.
- Took about 11 hours in total, mostly the UI.
- Summaries should be reviewed by clinical staff before anyone acts on them.
```

## The task

Write the review Hana asked for, in four sections: a verdict, the problems ranked by seriousness, what to keep, and three questions a panel would ask with what a strong answer contains.

> **Coach's note (Hana):** "Rank ruthlessly. A reviewer reads the first problem you list as the one you think matters most."
