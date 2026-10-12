---
title: "Scoping Your Capstone in a Weekend"
type: reading
minutes: 15
---

> **By the end of this lesson you will be able to:**
> - Choose a track brief and a domain that make "your part" clear
> - Cut the project to something you can finish in one or two weekends
> - Plan the order of work so you have evidence early, not at the end

## Pick the brief that matches the job

The kit has three briefs in `capstone-kit/briefs/`. Pick the one for the role you want. If you're applying to two, pick the one closer to your next interview.

| Track | You build | The documents that matter most |
|---|---|---|
| Applied AI Engineer (`engineer.md`) | A RAG or agent service with a golden set, calibrated judge, CI gate | Cost and latency table, failure log, decision record |
| Applied AI Architect (`architect.md`) | A demo with an eval on a customer-style dataset | TCO sheet, platform-fit memo, security brief |
| Forward Deployed Engineer (`fde.md`) | An agent inside a fake customer system, reached through an MCP server, evals in CI against the real model | Design doc, Dockerfile and Terraform skeleton, a 3-minute demo script |

All three share the core: a golden set of 40 or more cases, results from at least three runs with intervals, measured cost and latency, a failure log and a decision record.

## Pick a domain you can talk about for an hour

The deep dive will wander off the code: "Who would use this? What does a wrong answer cost them?" Pick a domain where you can answer.

Good sources:
- **Your own field.** You know what a good answer looks like, so labelling is faster and your edge cases are real.
- **Public documents.** Government help pages, an open-source project's docs and issues, a public FAQ, published policies.
- **Synthetic data you write.** Fine, if you say so in the README and make the edge cases deliberate.

Never use an employer's or customer's confidential data. Not even "just for testing".

Name a fictional customer if your brief needs one. Write one paragraph: sector, size, the workflow that hurts, who signs off, one hard constraint (data residency, a budget, a latency target).

## Cut it to a weekend

Scope creep kills more capstones than bugs. Use these cuts:

1. **One use case.** "Answers billing questions with citations" beats "a support platform".
2. **Three to five tools, or one retrieval index.** Not both unless your brief asks for an agent with retrieval.
3. **No UI beyond a CLI or a single route.** Reviewers read the README and the eval output, not your CSS.
4. **One measured improvement.** Change one big thing (retrieval method, model routing, tool design, prompt structure) and measure before and after. This becomes the story of your deep dive.

## The order of work

Evidence first. The most common failure is a polished app with an eval bolted on the night before.

| Session | Goal | Done when |
|---|---|---|
| 1 (2 to 3 h) | Kit running on your key; four labs started | `python -m app.agent ...` returns an answer; lab 1 results in hand |
| 2 (3 h) | Your data and tools in; golden set drafted | 40+ cases labelled **before** you tune the prompt |
| 3 (3 h) | Baseline eval, 3 runs | Pass rate with an interval, first failure log |
| 4 (3 h) | One measured improvement; judge calibrated | Before and after numbers; kappa against your labels |
| 5 (2 to 3 h) | Gate in CI; track extras; README and decision record | Gate fails on a deliberate regression; README written |

That's 13 to 16 hours. FDE and architect extras add a few more.

## Budget on your own key

You pay the API provider directly; the course never sees your key. Target under $5 in total:

- Default to Claude Haiku 5.5 at effort `low` ($0.10 input and $0.50 output per million tokens for prompts up to 100K tokens). Use Claude Sonnet 5.5 ($2 / $10) for the judge and one comparison.
- Set `effort` explicitly on every call. All three current models think by default, and thinking tokens are billed as output. Haiku 5.5 and Opus 5.5 default to `medium`; Sonnet 5.5 defaults to `high`.
- Cache stable prompts over 512 tokens. On Sonnet 5.5 a cache read costs 0.05x the input price; on Haiku 5.5 it's 0.1x. Name the model whenever you quote a saving.
- Set a spend limit in the Claude Console, and keep the kit's per-script budget (`CAPSTONE_BUDGET_USD`).

Prices were checked on 2026-10-10. Check the pricing page again before you quote one in your README.

> **Key takeaways**
> - Pick the brief for the role you want; all three share golden set, runs with intervals, cost table, failure log and decision record.
> - Choose a domain you can discuss for an hour, from your field, public documents or clearly labelled synthetic data. Never confidential data.
> - One use case, one measured improvement, no UI polish.
> - Label the golden set before you tune. Evidence first, app polish last.
