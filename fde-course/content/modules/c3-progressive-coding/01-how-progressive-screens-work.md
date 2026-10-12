---
title: How Progressive Coding Screens Work
type: reading
minutes: 15
---

> **By the end of this lesson** you'll know what a progressive coding screen is, why it rewards a different skill from algorithm puzzles, and the routine to run in the first ten minutes.

## The format

Candidates who have taken Anthropic's online assessment describe the same shape again and again: **one problem, about four levels, roughly 90 minutes, in Python, on CodeSignal.** Each level extends the code you wrote for the previous one, and a level only opens when every check on the previous one passes. The checks are hidden and the scoring is automatic. These are candidate reports (**Reported**), not an official description, so treat the details as approximate; recruiters confirm the format for each role.

## The environment

Here is what's official and what isn't.

| Fact | Label |
|---|---|
| Anthropic's [careers page](https://www.anthropic.com/careers) says technical interviews use live coding tools such as Colab and CodeSignal. | **Official** (checked 2026-10-10) |
| The same page says you can look things up, but should be comfortable enough with basic syntax and the standard library that it doesn't eat your time. | **Official** |
| The online assessment is a single progressive problem on CodeSignal, with levels that unlock in turn. | Reported (many accounts) |
| Exact details such as the Python version, how partial credit is counted, or whether a level's hidden checks are all-or-nothing. | No reliable public source. Ask your recruiter, and read the instructions on the screen. |

What follows from the official part is practical:

- **Practise without your setup.** A browser editor won't have your linters, snippets, local test runner or familiar shortcuts. Do at least one drill in this course in a plain editor with autocomplete off, using only the standard library.
- **Know the standard library cold.** `collections` (`defaultdict`, `Counter`, `deque`), `heapq`, `bisect`, `dataclasses`, `sorted` with tuple keys, f-string formatting. Looking up `bisect_left` costs a minute. Looking up how dictionaries work costs the level.
- **"You can look things up" isn't "you can use AI".** Anthropic's candidate guidance says assessments and live interviews are AI-free unless they tell you otherwise. Documentation is fine where the page says so; an assistant is not.
- **If your invitation links a practice or setup page, use it** before the real attempt, so the editor isn't new on the day.

Other labs describe similar ideas in other wrappers. Perplexity's assessments are reported as project-style, multi-part tasks with predefined tests. OpenAI's forward deployed engineering loop is reported to favour practical, production-style coding over puzzles. The common thread: **can you build and extend working software quickly, without making a mess?**

## What it actually tests

A puzzle round asks whether you can find the clever idea. A progressive round asks something closer to the job:

- **Data modelling.** Level 1 is easy with almost any model. Level 4 is easy only with a model that anticipated it.
- **Reading a spec carefully.** Most lost points are misread requirements: an off-by-one on "at exactly time `t`", a wrong sort order, a `None` where `False` was asked for.
- **Extending, not rewriting.** If Level 3 forces you to rewrite Level 1, you've lost twenty minutes you don't have.
- **Speed with control.** No one optimises in these rounds. Clean, obvious code you can change quickly wins.

> **The most common failure** is building Level 1 to pass Level 1. Candidates who struggle aren't slow typists; they chose a data structure that can't answer the next question.

## The first ten minutes

1. **Read the whole Level 1 spec twice.** Write the method signatures and return types as a comment block at the top of your file.
2. **Ask "what will they ask next?"** Anything with timestamps will probably ask about the past (history) and the future (scheduling or expiry). Anything with entities will probably ask for rankings and filters.
3. **Pick the boring, extensible model.** A dict of records plus an append-only log of changes survives almost any Level 4.
4. **Write one shared helper early.** If time matters, every public method should start by bringing the state up to date for the current timestamp.
5. **Submit early, submit often.** The checks are your spec's tests. A failing check message tells you exactly which sentence you misread.

## In the drill

The next lesson is a full four-level drill on an original problem: a feature-flag service. Start the clock only when you're ready to give it a real 90 minutes. Hints and the AI tutor switch off while it runs, because the real thing doesn't allow AI either: Anthropic's published candidate guidance says take-homes and live interviews are done without AI unless they say otherwise.

> **Key takeaways**
>
> - One problem, several levels, a clock: data modelling and careful reading matter more than algorithms.
> - Anthropic officially names CodeSignal and Colab as its live coding tools; the one-problem, four-level OA shape is reported. Practise in a plain browser editor with only the standard library.
> - Design Level 1's data model for the history and scheduling questions that usually follow.
> - Submit often; each failing check names the requirement you missed.
