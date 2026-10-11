---
title: "Why a Portfolio Project"
type: reading
minutes: 12
---

> **By the end of this lesson you will be able to:**
> - Explain why every applied AI loop rewards a project you built and can defend
> - Say what the Foundations portfolio capstone is, and how it differs from the in-course capstone
> - List the evidence a deep-dive interviewer looks for, and plan to have it

## The round you can't cram for

Strip away the company names and applied AI loops share four parts: practical coding, LLM system design, a deep dive into something you built, and motivation and values (module C1). Candidates report a project deep dive in the loops at every lab this course covers (**Reported**). Some forward deployed loops add a take-home followed by a review call (**Reported**), and one account describes a week-long case study walked through by a panel (**Anecdotal**).

You can practise coding with drills and design with mock rounds. The deep dive is different. The interviewer picks one thing you built and goes three or four levels down: why this model, how you knew it worked, what broke, what it cost, what you'd change. If the project is thin, the second question exposes it. No amount of reading fixes that. You need a real project.

## The Foundations portfolio capstone

This module is the **Foundations portfolio capstone**: a project you build in your own repository, against the real Claude API, with your own API key, in a domain you choose. The course gives you a starting template, `capstone-kit/`, with a working agent, an eval harness, four labs and deployment skeletons. You make it yours.

How it differs from the module 10 capstone:

| | Module 10 capstone | Foundations portfolio capstone (C8) |
|---|---|---|
| Model | The in-browser simulator. It never calls a real model. | The real API, on your key |
| Domain | Given (NorthStar Logistics, fictional) | You choose |
| Grading | Hidden tests in the browser | Your written reports, graded by a rubric, plus the deep-dive role-plays |
| What it proves | You can follow the steps | You can build, measure and defend a system |

Do module 10 first if you're on the FDE track. Then apply the same steps here to a problem you pick.

## Why your own key

Real models vary from run to run. They refuse sometimes. They take real seconds and cost real money. The simulator can't show you any of that, and those are exactly the things interviewers probe. Running on your own key means the course never sees your key or your bill, and you keep full control of spend. The kit defaults to the cheapest current model with low effort and stops every script at a budget you set. The whole capstone should cost under $5.

## What a deep-dive interviewer looks for

Use this as your checklist from day one, not the night before.

1. **Your part is obvious.** "We built" is a red flag. The repo, README and decision record should show what you decided.
2. **Numbers with a source.** A pass rate with a case count and an interval, a cost from measured usage, latency from timing. "It worked well" earns nothing.
3. **A failure you understood.** Real failing cases, grouped, with the fix you chose and why.
4. **A road not taken.** For each big decision, the alternative you rejected and the evidence.
5. **Limits stated plainly.** What your eval can't tell you, and what production would need.

The personas in the loop modules read your capstone README before they question you. Marcus (E7), Theo (FDE module 11) and the practice reviewer at the end of this module all use it. That is why the README lesson in this module matters more than any other.

## How this module runs

1. Scope the project in a weekend (next lesson), by track.
2. Run the four real-model labs and paste your numbers into the report lessons.
3. Write the capstone README and decision record, then the eval report.
4. Defend it to a practice reviewer who has read both.

A word on AI help. Anthropic's [candidate AI guidance](https://www.anthropic.com/candidate-ai-guidance) asks candidates to write their own first drafts and not to use AI in take-homes or live interviews unless permitted, while practising with Claude is fine (**Official**). Your portfolio project isn't a take-home, but the same spirit applies: you must be able to explain every line and every number, so write the README and decision record yourself.

> **Key takeaways**
> - Every loop has a project deep dive (**Reported**). A real project you can defend is the only preparation that works.
> - The Foundations portfolio capstone runs on the real API, on your key, in your domain. The simulator never calls a real model.
> - Interviewers look for your part, sourced numbers, an understood failure, a rejected alternative and honest limits.
> - The README you write in this module is what the deep-dive personas read before they question you.
