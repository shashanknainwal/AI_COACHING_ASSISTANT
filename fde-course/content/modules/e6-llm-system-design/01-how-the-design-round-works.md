---
title: How the LLM Design Round Works
type: reading
minutes: 18
---

> **By the end of this lesson** you'll be able to say where LLM system design shows up in applied AI loops, run a 45-minute answer through eight time-boxed stages, and tell a strong answer from a weak one before your interviewer does.

## Where the round shows up

Every lab in this course reports some form of system design for LLM products. The details differ, so here is what the public accounts say, with labels.

| Lab | What candidates describe | Label |
|---|---|---|
| Anthropic | The first onsite loop includes system design, often about LLM infrastructure, alongside coding and a culture interview. Doing badly in that loop can cancel the second one. | Reported ([Yale SOM](https://cdo.som.yale.edu/blog/2026/05/18/get-a-job-at-anthropic-interview-process-and-top-questions/), [Educative](https://www.educative.io/blog/anthropic-interview-process), [Design Gurus](https://www.designgurus.io/answers/detail/what-is-the-anthropic-interview-process-like-round-by-round)) |
| OpenAI (forward deployed roles) | A virtual onsite of four to six interviews that includes system design for LLM deployment. Candidates are assessed on scoping ambiguous problems, building systems around models and proving them with evals. | Reported ([Exponent](https://www.tryexponent.com/guides/openai-forward-deployed-engineer-interview), [IGotAnOffer](https://igotanoffer.com/en/advice/openai-forward-deployed-engineer-interview)) |
| Perplexity | An onsite of four or five rounds that includes AI system design: retrieval-augmented generation, serving under latency limits, and caching. | Reported ([Design Gurus](https://www.designgurus.io/answers/detail/what-is-the-perplexity-interview-process-like-round-by-round), [Interview Query](https://www.interviewquery.com/prep-guides/perplexity-ai-software-engineer)) |

No lab publishes its design questions, and this course doesn't reconstruct them. Every prompt in this module is original, written in the style candidates describe. Treat the format above as a guide and confirm it with your recruiter, who knows the current loop.

## How it differs from classic system design

A classic design round is about storage, queues, sharding and consistency. Those still matter, but an LLM round adds four things the interviewer will listen for:

1. **The model is a probabilistic component.** It is right most of the time, not all of the time. Your design has to measure how often, and limit the damage when it's wrong.
2. **Quality is a requirement you have to define.** "Answers correctly" is not a spec. You need a golden set, a grading method and a launch bar.
3. **Tokens are the main cost and the main latency driver.** You should be able to turn token counts into dollars and milliseconds out loud.
4. **Untrusted text reaches the model.** Documents, emails and web pages can carry instructions. Prompt injection is a design concern, not a footnote.

## The 45-minute framework

Use this as a default clock. Interviewers steer, so be ready to skip ahead when they do, but don't let any stage vanish.

| Minutes | Stage | What you produce |
|---|---|---|
| 0–5 | Scope and numbers | Users, use cases, volume, latency target, quality bar, what's out of scope |
| 5–11 | API and data flow | The request path from caller to answer, and the offline pipelines |
| 11–17 | Models and prompts | Which model does which step, and why; prompt structure; output format |
| 17–24 | Retrieval and tools | Index design, chunking, ranking; tools the model can call and their limits |
| 24–31 | Evals and launch gate | Golden set, graders, thresholds, online metrics |
| 31–36 | Failure modes | What breaks, how you'd notice, what happens next |
| 36–41 | Cost and latency math | Tokens per request, dollars per day, a latency budget |
| 41–45 | Iteration plan | What ships first, what you'd measure, what comes next |

### 1. Scope and numbers (5 minutes)

Ask the questions that change the design, then commit to numbers even if the interviewer shrugs. Good questions are about **who** (internal staff or the public), **what** (top three use cases by volume), **how much** (requests per day, peak factor, corpus size), **how fast** (latency target, and whether it means first token or full answer) and **how good** (what a wrong answer costs).

Write the numbers on the board. "10,000 requests a day, peak three times the average, p95 under 3 seconds to first token, corpus of 500,000 documents." Every later decision should point back to one of these.

### 2. API and data flow (6 minutes)

Draw two paths:

- **Online path:** client, gateway (auth, rate limits), orchestrator, retrieval, model call, post-processing, response. Say whether you stream.
- **Offline path:** ingestion, parsing, chunking, embedding, indexing, and how updates and deletes flow through.

Define the API in one line, for example `POST /answer {question, conversation_id} -> stream of {text, citations}`. It shows you think about the contract, not only the internals.

### 3. Models and prompts (6 minutes)

Match each step to a model and give the reason:

| Step | Typical choice | Why |
|---|---|---|
| Routing, classification, query rewriting | Claude Haiku 5.5 | Fast and cheap: $0.10 input and $0.50 output per million tokens for prompts up to 100K tokens |
| Main answer over retrieved context | Claude Sonnet 5.5 | Strong quality at $2 / $10 per million tokens |
| Hard reasoning, long agentic work | Claude Opus 5.5 | Highest quality of the three at $4 / $20; thinking is always on, so control depth with `effort` |

Then describe the prompt: a stable system prompt first (rules, format, tool definitions), retrieved context next, the user's turn last. That order matters for prompt caching, which is a prefix match over tools, then system, then messages. Change one byte early and everything after it misses the cache.

Say how you get structured output. For example, use `output_config.format` with a JSON schema when downstream code needs fields, and say what happens when the model refuses or returns `stop_reason: "max_tokens"`.

### 4. Retrieval and tools (7 minutes)

Most design prompts hide a retrieval problem. Cover:

- **Chunking:** size, overlap, and keeping structure (headings, tables) attached to chunks.
- **Search:** hybrid lexical plus vector search beats either alone for names, codes and IDs. Add a reranker if the budget allows.
- **Permissions:** filter by the caller's access before ranking, not after generation.
- **Freshness:** how a changed or deleted document leaves the index, and how fast.

For tools, name each one, its inputs, and its limits. The model returns `stop_reason: "tool_use"`, your code runs the tool and sends back a `tool_result`. Your code, not the model, enforces limits such as refund caps or read-only access.

### 5. Evals and launch gate (7 minutes)

This is the stage weak answers skip and strong answers dwell on.

- **Golden set:** a few hundred real or realistic cases, stratified by use case, with expected answers or grading criteria.
- **Graders:** code checks where you can (citation present, JSON valid, correct tool called), an LLM judge with a written rubric where you can't, and a human-labelled sample to check the judge.
- **Component evals:** measure retrieval separately (did the right chunk come back in the top k?) so you know which part failed.
- **Launch gate:** explicit thresholds, for example "at least 90% graded correct, zero critical safety failures, p95 under target", agreed before you see the results.
- **Online signals:** thumbs, escalation rate, reopen rate, citation clicks, and a weekly sample reviewed by people.

### 6. Failure modes (5 minutes)

Pick the four or five that matter for this system and give each a detection and a response. A table works well on a whiteboard:

| Failure | Detection | Response |
|---|---|---|
| Confident answer with no support in the context | Grounding check; judge on a sample | Answer "I couldn't find this" and show what was searched |
| Prompt injection in a retrieved document | Red-team cases in the eval set | Treat retrieved text as data; tools enforce permissions in code |
| Model API errors or slowness | Error rate and latency alerts | Retries with backoff, a fallback model, a graceful message |
| Stale or deleted content returned | Freshness metric on the index | Incremental sync with delete handling |

### 7. Cost and latency math (5 minutes)

Do the arithmetic out loud. Tokens per request multiplied by price, multiplied by volume. Then a latency budget that adds up to your target. A rough number with stated assumptions is what the interviewer wants. Lesson 2 walks through a full example.

Two facts that move the numbers a lot:

- **Prompt caching.** Cache reads cost $0.20 per million tokens on Claude Opus 5.5 and $0.10 on Claude Sonnet 5.5 (5% of base input), against $4 and $2 for fresh input. Cache writes cost about 1.25 times the base input price for the default 5-minute lifetime, and a 1-hour lifetime exists. Check hits with `usage.cache_read_input_tokens`.
- **Batch processing.** Work nobody is waiting on (eval runs, backfills) can go through the Message Batches API at half price.

### 8. Iteration plan (4 minutes)

End with a sequence, not a wish list: what ships first to a small group, which metric decides the next step, and the two or three improvements you'd try in order. "Week 1: one team, read-only, measure grounded-answer rate. If retrieval misses are the top failure, add a reranker before touching the prompt."

## What separates strong from weak answers

| Weak | Strong |
|---|---|
| Starts drawing boxes in minute one | Spends five minutes on scope and writes numbers down |
| "We'll use the best model" | Picks a model per step and gives the cost or latency reason |
| "We'll fine-tune it" as a first move | Tries prompting, retrieval and evals first; says what result would justify fine-tuning |
| Quality is "we'll test it" | Golden set, graders, a launch gate with thresholds, online signals |
| Lists every component they know | Explains two or three tradeoffs and the alternative they rejected |
| Never says a dollar figure | Cost per request and per month, with one lever to cut it |
| Lets the model take actions freely | Limits enforced in code, human review for risky actions |
| Ends when time runs out | Ends with a staged rollout and what they'd measure |

Interviewers also listen to how you handle pushback. When they change a requirement ("now it has to be under one second"), say what changes and what it costs. Don't defend the old design.

## Practice prompts

These are original prompts in the style of the round. Run each against the clock with the framework above.

- **Practice prompt:** Design a meeting-notes assistant that summarises recorded calls for a 2,000-person sales team.
- **Practice prompt:** Design a code-review bot that comments on pull requests for a company with 300 engineers.
- **Practice prompt:** Design an extraction service that pulls 40 fields out of 50,000 scanned contracts a month.

> **Key takeaways**
>
> - LLM system design is reported in the Anthropic, OpenAI and Perplexity loops. Confirm the current format with your recruiter.
> - Run the clock: scope, data flow, models and prompts, retrieval and tools, evals, failure modes, cost and latency, iteration.
> - Write numbers down in minute one and tie later decisions back to them.
> - Evals and a launch gate are where strong answers pull away from weak ones.
> - Do the cost and latency math out loud, and name at least one lever such as caching, routing or batching.
