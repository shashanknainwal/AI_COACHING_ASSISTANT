---
title: The Online Assessment Environment
type: reading
minutes: 10
---

> **By the end of this lesson** you'll know what's officially said and what's reported about the coding environment, how to set yourself up so the tool doesn't cost you time, and how to manage a 90-minute progressive problem when you're stuck.

## What's known

Module C3 lesson 1 covers the format of the problem itself. This lesson is about the environment around it.

| Fact | Label |
|---|---|
| Anthropic's careers page says technical interviews use live coding tools such as Colab and CodeSignal, that you can look things up, and that you should be comfortable enough with basic syntax and the standard library that they don't slow you down. All interviews run over Google Meet. | **Official** ([careers page](https://www.anthropic.com/careers), checked 2026-10-10) |
| The online assessment is one progressive problem on CodeSignal, about four levels, about 90 minutes; a level opens when the previous level's checks pass. | Reported (many accounts; see C1 and C3) |
| No AI assistance in assessments or live interviews unless Anthropic says otherwise. | **Official** ([candidate AI guidance](https://www.anthropic.com/candidate-ai-guidance)) |
| The Python version, exactly how partial credit is counted, and whether a level's hidden checks are all-or-nothing. | No reliable public source. Read the on-screen instructions and ask your recruiter. |
| Perplexity: a project-style online assessment with multi-part tasks and predefined tests, or live coding. | Reported (C1) |

So: the platform name for Anthropic is official in general terms, the exact OA shape is reported, and the scoring details are unknown. Plan around what's known and read the instructions on the day.

## Set up so the tool can't hurt you

This section is **General**: practical advice for any browser-based coding assessment.

- **Practise in a plain browser editor.** No local autocomplete, no linter, no AI. This course's editor is close enough: run the C3 drills with the clock on and the tutor off.
- **Check your setup the day before.** Browser up to date, camera and microphone working if the session is proctored or live, a stable connection, notifications off. If the platform offers a practice or system check, do it.
- **Learn the editor's basics in advance.** How to run the tests, where the output appears, whether you can add your own print statements, how to reset. Don't spend minute five finding the run button.
- **Know your standard library.** The official line says you can look things up. Looking up `bisect` is fine. Looking up how to sort a list of dicts by two keys costs the level. C3 lesson 1 lists what to know cold.
- **Ask for accommodations early** if you need them. Anthropic's guidance says to tell your recruiter (**Official**; C1 lesson 3).

## Managing the clock

Also **General**, drawn from how progressive problems work.

| Minute | What to do |
|---|---|
| 0–5 | Read the whole first level twice. Write method signatures and return types as comments. Note edge cases the spec mentions. |
| 5–25 | Build level 1 with a data model that can grow (C3 lesson 3). Run the visible tests early and often. |
| Each new level | Read the new spec fully before typing. Ask: does my model already support this? Extend; don't rewrite. |
| Stuck for 10 minutes | Re-read the spec line by line against your output. Most failures are misread requirements, not hard algorithms. Print the failing input. |
| Last 10 minutes | Stop starting new features. Make what you have pass cleanly. Partial progress on a level you've started may or may not count (unknown), but broken code that crashes earlier levels certainly doesn't help. |

Two habits help most:

1. **Small runs.** Run after every function, not after every level. A failing test you see in minute 12 is cheap; one you find in minute 70 isn't.
2. **Spec notes.** Keep a three-line comment at the top: the rules you've misread before. "Ties sort by id." "Return None, not False." It slows you down by seconds and saves minutes.

## If it goes badly

Finish anyway, and keep the code clean. You don't know how it's scored, so the rest of what you write may still count. Then write down what tripped you up while it's fresh, and do one more C3 drill aimed at it. If it does end the process, many companies ask you to wait a while before reapplying (lesson 13; **General**).

## Practise it

Do [C3's feature-flag drill](/learn/c3-progressive-coding/02-drill-feature-flag-service) and the gateway-ledger drill under real conditions: timed, tutor off, one sitting, in this course's browser editor. Then do them again a week later without looking at your first attempt.

> **Key takeaways**
>
> - **Official:** Anthropic names live coding tools such as Colab and CodeSignal, lets you look things up, and expects fluency with basic syntax and the standard library. **Reported:** one progressive CodeSignal problem, about four levels, about 90 minutes.
> - Scoring details such as partial credit aren't public. Read the on-screen instructions and ask your recruiter.
> - Practise in a plain browser editor with the tutor off; test your setup the day before.
> - Read every level fully, extend rather than rewrite, run small and often, and stop adding features in the last ten minutes.
