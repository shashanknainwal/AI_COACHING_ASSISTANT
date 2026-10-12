---
title: "Study Guide: Engineering Posts and Other Labs' Documents"
type: reading
minutes: 22
---

> **By the end of this lesson** you'll be able to summarise three of Anthropic's engineering posts that matter most in applied roles, name the ideas from them you can use in a design round, and read OpenAI's Model Spec and Preparedness Framework with the six-note framework from lesson 1.

## Why engineering posts belong in this module

The essays in lessons 2 and 3 tell you how a lab's leadership sees the world. Engineering posts tell you how the lab thinks you should build. For an Applied AI Engineer, Architect or FDE, that's closer to the job: the people interviewing you, and the customers you'd serve, read these posts too.

Read them with the same six notes, with two changes:

- **Note 6 (the job) carries most of the weight.** For each idea, ask: where would I use this with a customer, and how would I know it worked?
- **Add a seventh note: what you'd test.** Engineering advice is a hypothesis about your system. "Fewer, better tools help" is something you can check with an eval on your own task.

Read the originals; what follows is a study guide in our own words, checked against the posts on 2026-10-10. Posts get updated, so quote the date you read them.

## Building effective agents

[Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) (Anthropic engineering, December 2024). The post now carries a note that much of the tooling it mentions has changed since it was written. The design ideas are what to take from it.

**The claim, in two sentences.** The most successful agent builds the authors saw used simple, composable patterns rather than complex frameworks. Start with the simplest thing (often a single well-prompted call with retrieval and examples) and add steps or autonomy only when it measurably improves results.

**The ideas to know:**

- **Workflows versus agents.** In a *workflow*, your code decides the path and calls the model at fixed steps. In an *agent*, the model directs its own process and tool use. Both are "agentic systems"; the difference is who controls the path.
- **The building block** is an "augmented LLM": a model with retrieval, tools and memory.
- **Five workflow patterns:**

| Pattern | What it does | Fits when |
|---|---|---|
| Prompt chaining | A fixed sequence of calls, each using the last one's output, with programmatic checks between steps | The task splits cleanly into fixed sub-tasks |
| Routing | Classify the input, then send it to a specialised prompt, tool set or model | Distinct categories are better handled separately, such as easy questions to a small model |
| Parallelisation | Split into independent sub-tasks (sectioning) or run the same task several times (voting) | Speed, or more confidence from several attempts |
| Orchestrator-workers | A central model breaks the task down at run time and delegates to workers | You can't predict the sub-tasks in advance |
| Evaluator-optimizer | One call generates, another critiques, in a loop | Clear criteria exist and feedback measurably improves the output |

- **Agents** are, in the post's framing, a model using tools in a loop, getting "ground truth" from the environment at each step, with stopping conditions such as a maximum number of iterations. They cost more and errors compound, so test them in sandboxes with guardrails.
- **Three principles:** keep the design simple, make the agent's planning visible, and invest in the agent-computer interface (tool definitions and documentation) as much as you would in a human interface.
- **Frameworks** help you start, but can hide the prompts and responses. Start with the API directly, and if you use a framework, understand what it does underneath.
- **Tool design (appendix):** pick formats that are easy for a model to write, give it room to think before it commits, and "poka-yoke" tools so mistakes are hard to make. The post's example: the authors changed a tool to require absolute file paths after the model kept getting relative paths wrong.

**A load-bearing assumption worth naming:** "add complexity only when it demonstrably improves outcomes" assumes you can measure outcomes. Without an eval, you can't tell whether the orchestrator beat the single call. That's why this post and the evals material in your track go together.

## Effective context engineering for AI agents

[Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) (Anthropic engineering, September 2025).

**The claim, in two sentences.** Context is a finite resource with diminishing returns: as it grows, a model's ability to recall and use what's in it declines, which the post calls *context rot*. So the job shifts from writing one good prompt to curating, at every step, the smallest set of high-signal tokens that makes the desired behaviour likely.

**The ideas to know:**

- **An "attention budget".** The post ties context rot to how transformers work: every token attends to every other, so attention gets stretched as context grows, and models see fewer very long sequences in training. The result is a gradient, not a cliff.
- **System prompts at the right altitude.** Between brittle, hard-coded if-else logic and vague guidance that assumes shared context. Start minimal with a strong model, then add instructions and examples for the failures you observe.
- **Lean tool sets.** If a human engineer can't say which tool fits a situation, the agent can't either.
- **Examples over rule lists.** A few diverse, canonical examples instead of a laundry list of edge cases.
- **Just-in-time retrieval.** Instead of loading everything up front, keep lightweight references (file paths, queries, links) and let the agent load data when it needs it. It's slower than pre-computed retrieval, so a hybrid often works best.
- **Long-horizon techniques:** *compaction* (summarise a context near its limit and continue in a fresh one; clearing old tool results is the lightest form), *structured note-taking* (the agent writes notes outside the context and reads them back later), and *sub-agents* (each explores with a clean context and returns a condensed summary, the post says often 1,000–2,000 tokens).

**Where it meets C2:** this is the quality reason behind "retrieve 5–10 chunks instead of stuffing the window" (C2 lesson 1), and compaction is the append-only-friendly way to keep history short (C2 lesson 4).

## Writing effective tools for agents

[Writing effective tools for agents, with agents](https://www.anthropic.com/engineering/writing-tools-for-agents) (Anthropic engineering, September 2025).

**The claim, in two sentences.** Tools are a contract between deterministic software and a non-deterministic agent, so they should be designed for agents rather than copied from your existing API. Build a prototype, measure it with a realistic evaluation, and improve it from the transcripts, including with the help of an agent.

**The ideas to know:**

- **Evaluate tools with realistic tasks.** Strong eval tasks look like real work and may need many tool calls ("find all log entries for this double charge and check whether other customers were affected"), not one-step lookups. Pair each with a verifiable outcome, and avoid verifiers so strict that they reject correct answers over formatting.
- **Measure more than accuracy:** number of tool calls, tokens, runtime and tool errors. Lots of redundant calls suggests pagination or limits need adjusting; lots of invalid-parameter errors suggests unclear descriptions. Keep a held-out test set so you don't overfit.
- **Fewer, more targeted tools.** `search_contacts` rather than `list_contacts`; a `schedule_event` that finds availability, rather than three separate tools the agent must chain.
- **Namespacing** related tools with a shared prefix (by service or resource) helps the agent choose. The post says prefix versus suffix naming had measurable effects, and that you should test on your own evals.
- **Return meaningful context.** Prefer names over cryptic IDs: the post reports that resolving UUIDs to meaningful language reduced hallucinations in retrieval tasks. A `response_format` parameter ("concise" or "detailed") lets the agent choose.
- **Token efficiency.** Pagination, filtering and truncation with sensible defaults. The post notes Claude Code limits tool responses to 25,000 tokens by default. Error messages should say how to fix the call, not just return a code.
- **Descriptions are prompts.** Write them as you'd brief a new hire, with unambiguous parameter names (`user_id`, not `user`).

## Using these posts in an interview

| If the interviewer asks... | An idea to draw on | How to say it |
|---|---|---|
| "Would you build an agent for this?" | Workflows versus agents; start simple | "The path is predictable, so I'd start with a routed workflow and only move to an agent if the eval shows the fixed path fails." |
| "The agent picks the wrong tool." | Lean, namespaced, well-described tools | "First I'd check whether a human could tell the tools apart from their descriptions. Then merge or rename, and measure tool-selection accuracy." |
| "It gets worse in long sessions." | Context rot, compaction, notes, sub-agents | "Long contexts degrade recall. I'd compact, or move exploration into sub-agents that return short summaries." |
| "How would you test the tools?" | Realistic multi-step eval tasks and metrics | "Real tasks, verifiable outcomes, and I'd track calls, tokens and errors as well as pass rate." |

Attribute ideas fairly ("Anthropic's engineering post on agents argues...") and add your own experience. An idea you've tested on a real system is worth far more than one you can quote.

## OpenAI: the Model Spec and the Preparedness Framework

If you're interviewing at OpenAI, two documents play the role that the constitution and the RSP play in lesson 4:

- **The Model Spec:** OpenAI's public description of how it wants its models to behave. It's published at [model-spec.openai.com](https://model-spec.openai.com/).
- **The Preparedness Framework:** OpenAI's process for tracking and preparing for severe risks from frontier model capabilities. Search openai.com for "Preparedness Framework" and read the latest version and its change log.

We couldn't reach openai.com from our build environment when this lesson was written (2026-10-10), so this guide doesn't summarise either document. That's deliberate: a second-hand summary of a document you'll be asked about is a liability. Read the current versions yourself and answer these questions with the six notes:

**For the Model Spec:**

1. **Who and what does it order?** When instructions from different parties conflict (the company, a developer building on the API, an end user), whose wins, and where does the document say so?
2. **Rules or judgment?** Which parts are firm rules and which are defaults a developer or user can change? Compare with the "judgment over rules" approach of Claude's constitution in lesson 4.
3. **How would an outsider check it?** What behaviour could you test with prompts to see whether a model follows the spec?
4. **The job:** if a customer's product needs behaviour outside the defaults, what does the spec say they can and can't change?

**For the Preparedness Framework:**

1. **What does it track?** List the risk categories and the capability levels it defines, in its own words.
2. **What does each level trigger?** For each threshold, what has to happen before a model is deployed or developed further, and who decides?
3. **Commitments versus goals.** Which parts bind the company and which are aims? This is the same question lesson 1's worked example asked of Anthropic's RSP.
4. **Compare carefully.** Put it next to the RSP from lesson 4 only after reading both. Note one real similarity and one real difference, with the section of each document that shows it.

If you can answer these from the documents themselves, with dates and versions, you'll be better prepared than most candidates.

> **Key takeaways**
>
> - Engineering posts are the most job-relevant lab reading for applied roles. Read them with the six notes, weight the "job" note heavily, and add "what would I test?".
> - *Building effective agents:* workflows versus agents, five workflow patterns, and add complexity only when an eval shows it helps.
> - *Context engineering:* context rot makes context a finite budget; curate the smallest high-signal set, and use compaction, notes and sub-agents for long tasks.
> - *Writing tools:* fewer targeted tools, clear names and descriptions, token-efficient responses, helpful errors, and realistic evals with held-out tests.
> - For OpenAI's Model Spec and Preparedness Framework, read the current versions yourself and answer the framework questions; don't rely on summaries.
