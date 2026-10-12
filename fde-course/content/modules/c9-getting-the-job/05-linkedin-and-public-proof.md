---
title: LinkedIn and Public Proof
type: reading
minutes: 12
---

> **By the end of this lesson** you'll be able to set up a LinkedIn profile that matches your chosen role, publish one eval repository a stranger can run, and write one short technical write-up that gives an interviewer something specific to ask about.

## Why public proof matters for applied roles

Every lab in module C1 has a project deep dive (**Reported** at Anthropic, OpenAI and Perplexity). Your resume makes claims; public work lets a reader check one before they call you, and gives the deep-dive interviewer something concrete to dig into.

It also helps when your best work is confidential. If you can't show your employer's code, a public project that shows the same skills is the next best thing.

Everything else in this lesson is **General**: common practice in tech hiring, not any lab's stated process. No lab we checked says it reviews GitHub or LinkedIn as part of screening. Treat public proof as something that helps when someone looks, not something someone is guaranteed to look at.

## LinkedIn: make it agree with your resume

Recruiters often find candidates on LinkedIn, and people you contact for referrals (lesson 6) will look you up before replying (**General**). Three things matter.

| Part | What to do | Example (fictional) |
|---|---|---|
| **Headline** | Your role sentence from lesson 1, compressed. The role you want, the evidence for it. | "Backend engineer building LLM extraction and evals for logistics customers" |
| **About** | Three short paragraphs: what you do now, one proof story with a number, what you're looking for. Same facts as your resume. | 80–150 words. No "passionate". |
| **Featured** | Pin your eval repo and your write-up. These are the two links you want a stranger to click. | |

Make it consistent with your resume. Dates, titles and numbers that differ between the two look careless at best. And keep the same honesty standard: anything public can come up in an interview.

If you're employed, check your employer's policy on describing current work and on signalling you're looking. "Open to work" settings and their visibility are a personal choice (**General**).

## The eval repo: one project a stranger can run

For applied roles, the most useful public artefact is a small LLM project with a real evaluation. All three applied postings in C1 mention evals (**Official**, postings read 2026-10-08), and it's the thing most portfolio projects skip.

What makes one credible:

- **A README that answers the deep-dive questions.** What it does, how to run it, the model and settings, the decisions you made and what you rejected, and what you'd do next. E7's take-home lesson has a strong README structure to copy.
- **A golden set with a story.** How many cases, where they came from, who labelled them, which are edge cases. Kept out of prompt tuning, or the README says so.
- **Results as counts, not adjectives.** "74 of 84 correct" beats "high accuracy". Run-to-run variation if you measured it.
- **Cost and latency from measured usage.** Per request, with thinking tokens counted as output. C2 covers the arithmetic.
- **One command to run the eval.** If a reviewer can't run it in five minutes, assume they won't.
- **No secrets and no one else's data.** No API keys in the history, no customer data, no scraped content you don't have rights to. Check your commit history, not just the latest version.

Small and finished beats large and half-done. A 300-line repo with an honest eval says more than an ambitious agent framework with no tests.

### Your capstone is the obvious candidate

Module C8, the portfolio capstone, is built to be this repo: a project on the real API with a golden set, a calibrated judge, a cost and latency table and a decision record, which you choose and own. If you build it properly, it's your deep-dive project and your pinned repo at once. If you already have a strong project of your own, use that instead and borrow C8's checklist.

Remember the AI rules from C1 lesson 3: Anthropic's guidance encourages using Claude to prepare, and your public projects are preparation. If a lab gives you a take-home, though, that's an assessment: no AI unless they say so (**Official**).

## One write-up

A short post (600–1,200 words) about one decision in your project gives an interviewer a question to ask, and shows you can explain technical work in writing, which customer-facing roles do every day.

Good shapes:

1. **"What my eval caught."** The failure, how you found it, what you changed, the before and after numbers.
2. **"Why I chose X over Y."** One design decision, the alternatives, the numbers that settled it, and what it cost.
3. **"What broke in production."** An incident, how you debugged it, what you'd do differently.

Write it yourself. Claude can critique it. Link the repo, post it somewhere you control or on a common platform, and pin it on LinkedIn.

Avoid write-ups that summarise a lab's announcement or restate documentation. They show you can read, not that you can build.

## How this connects

| Artefact | Where it's used |
|---|---|
| LinkedIn headline and About | Referral and outreach notes (lesson 6); recruiters looking you up |
| Eval repo | Resume project line; the deep dive (C5 lesson 9, your track's loop) |
| Write-up | Outreach note ("I wrote about..."); a talking point in the recruiter screen (lesson 8) |

> **Key takeaways**
>
> - Public work lets a reader check your claims and gives the deep dive something concrete. No lab we checked says it reviews it, so treat it as a bonus that helps when someone looks (**General**).
> - Make LinkedIn agree with your resume: headline from your role sentence, a three-paragraph About, and two pinned links.
> - One small eval repo a stranger can run beats a large unfinished project. Results as counts, measured cost, no secrets.
> - The C8 capstone is designed to be that repo and your deep-dive project.
> - One short write-up about a single decision gives an interviewer a question to ask.
