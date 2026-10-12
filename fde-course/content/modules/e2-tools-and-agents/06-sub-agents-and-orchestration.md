---
title: "Sub-agents and Orchestrator-Workers"
type: reading
minutes: 18
---

> **By the end of this lesson** you will be able to:
> - Explain what a sub-agent is in API terms, and the four reasons to split work across them
> - Say when not to split, including the "extra checker" trap
> - Design the brief a worker receives and the report it hands back
> - Budget a fan-out, contain worker failures, and estimate its cost with thinking included
> - Name the platform options: your own orchestrator, or Claude Managed Agents multiagent sessions

## How this shows up in interviews

Anthropic's Forward Deployed Engineer posting lists sub-agents next to MCP servers and agent skills as things the role builds inside customer systems (Official, from the job posting). Agent design prompts are common in applied AI design rounds (Reported). The question rarely says "sub-agents". It sounds like "design a research assistant that reads 300 contracts" or "your agent's quality drops after step 30; what do you change?" A candidate who reaches for one giant loop, or one who splits everything into five agents by reflex, both lose points. The interviewer wants to hear *why* you split, where the boundary is, and what it costs.

## What a sub-agent is

Strip away the vocabulary and a sub-agent is **a separate conversation**. It has its own `messages`, its own system prompt, its own tools and possibly its own model. The orchestrator (also called the lead or coordinator) starts it with a brief, the sub-agent runs its own loop, and only its final report comes back.

```text
Orchestrator (Opus 5.5)            Worker A (Haiku 5.5)      Worker B (Haiku 5.5)
  plan: 2 independent questions ─►  brief A ─► tool loop      brief B ─► tool loop
                                     report A ◄─┘              report B ◄─┘
  verify + synthesize ◄────────────── report A, report B
```

The worker's tool results, retries and thinking never enter the orchestrator's context. That single property is where every benefit comes from, and also where most bugs come from.

## Four reasons to split

| Reason | What it buys | Example |
|---|---|---|
| **Context isolation** | Each worker reads a lot and returns a little. The lead's context holds reports, not raw tool output, so quality doesn't decay late in long runs | Checking 40 bookings: 160 tool results stay in 40 short worker conversations |
| **Parallelism** | Independent pieces run at the same time; wall-clock drops toward the slowest worker | Five sources researched at once instead of in sequence |
| **A cheaper model for bulk work** | Reading and extracting needs little hard reasoning. Haiku 5.5 is $0.10/$0.50 per million tokens (prompts up to 100K) against Opus 5.5 at $4/$20 | The lead plans and writes on Opus 5.5; workers search and extract on Haiku 5.5 |
| **Narrower permissions** | A worker can be read-only. Injected text in a document it reads has no write tool to abuse | Research workers get search and fetch; only the lead (behind an approval gate) can send email |

There's a caching angle too. Switching `model` in the middle of one conversation invalidates its prompt cache. Anthropic's agent-design guidance says to spawn a sub-agent on the cheaper model for the sub-task instead, and keep the main loop on one model.

## When not to split

Splitting has real costs: every worker pays for its own system prompt and tool definitions, the lead pays to read every report, and you now have a distributed system to debug.

- **One question at a time.** A support agent or a Q&A bot answers each request itself. Don't add a roster of extra solvers, checkers or voters that redo or grade the same answer: Anthropic's multiagent guidance is explicit that each extra pass multiplies the cost of every answer. A check in your own code that calls no model (does every cited quote appear in the source?) is fine.
- **Tightly coupled steps.** If step 3 needs everything steps 1 and 2 learned, a worker boundary forces you to serialize that knowledge into a brief and back. A single loop is simpler.
- **Shared writes.** Two workers updating the same record need coordination you'd rather not build. Keep writes in one place.
- **Small jobs.** Three tool calls don't need a fan-out. The overhead of briefs and reports dominates.

A good one-line rule for an interview: *split when the work is "look into N independent things, then combine", or when one piece would flood the context with reading; otherwise keep one loop.*

## The brief and the report

The boundary between lead and worker is an API contract. Design it like one.

**The brief** a worker receives should be self-contained. The worker can't see the lead's conversation, so anything it needs must be in the brief:

- The goal and the scope: "Check booking FW7Q2K against this disruption." One item, not "the bookings".
- The constraints that matter: what counts as affected, what to do when a lookup fails.
- The shape of the answer: a schema (`output_config.format`) beats a paragraph of instructions.
- Nothing else. Other items' data in a brief is a context leak and a privacy problem.

**The report** that comes back should be compact and checkable:

- Structured fields the lead (and your code) can rely on, with an explicit `unknown` value instead of a guess.
- Evidence or a short `rationale` naming the source of each claim, so the lead can verify rather than trust.
- No transcript. Pass reports as text or JSON. Don't paste a worker's assistant turns into the lead's history: on current models thinking blocks are bound to the conversation that produced them, and the lead doesn't need them anyway.

Then **check the report in code** before the lead sees it. Does it describe the item the worker was given? Does it parse? Is every quoted figure present in the tool output? These checks call no model and catch the cross-talk bugs that are hardest to spot in a summary.

## Budgets and failure

A fan-out multiplies everything, including runaway behavior.

- **Per-worker caps.** An iteration cap and an output-token budget on each worker, checked before it starts more tool calls.
- **A run budget.** The sum across workers plus the lead, so you can stop dispatching when the run is over budget.
- **Partial results are normal.** One worker failing (a 529 after retries, a refusal, a bad report) should never sink the run. Record the failure and tell the lead explicitly which items have no report, so the summary says "not checked" instead of silently dropping them.
- **A tool failure is not a worker failure.** A worker whose lookup failed can still report `unknown`. That's useful information.
- **Rate limits.** Ten parallel workers are ten times the requests per minute. Cap concurrency with a semaphore sized to your limits, and remember that each worker's SDK retries add to the load.
- **Prompt injection still applies.** A worker's report is derived from untrusted content, so the lead treats it as data. Narrow worker permissions are the stronger defence.

## What it costs, with thinking included

Rough numbers for the 40-booking disruption check you'll build next. The thinking figures are assumptions for illustration; measure `usage.output_tokens` (which includes thinking) on your own traffic.

| Component | Model and effort | Tokens | Cost |
|---|---|---|---|
| One worker: 4 calls, ~1,500 input each | Haiku 5.5, `effort: "low"` | 6,000 in; 4 × (60 visible + ~200 thinking) = 1,040 out | ~$0.0011 |
| 40 workers | | 240,000 in; 41,600 out | ~$0.045 |
| Lead: one call over 40 short reports | Opus 5.5, `effort: "medium"` | ~5,400 in; 400 visible + ~1,500 thinking = 1,900 out | ~$0.060 |
| **Total per disruption** | | | **~$0.105** |

Two things to notice. First, the lead's single call costs more than all 40 workers together, so the lead's effort setting is the biggest cost lever. Second, compare a single Opus 5.5 loop doing all 160 lookups itself: about 120 calls whose history grows to hold every tool result. At an average of 20,000 input tokens per call that's 2.4 million input tokens, about $9.60 before caching. Caching (reads at 0.05x on Opus 5.5) narrows the cost gap a lot, but not the quality problem of a context full of stale tool results.

## Where to build it

| Option | Who writes the orchestration | Notes |
|---|---|---|
| Your own code over the Messages API | You | Full control over briefs, budgets, concurrency and checks. This is what the next exercise builds |
| Claude Managed Agents multiagent sessions | Anthropic's harness | A coordinator agent with a roster: `self` (copies of itself) and other agents, for example a read-only researcher on Haiku 5.5. Each runs in its own context-isolated thread; threads share the session's container and filesystem, and only each sub-agent's report comes back. One level of delegation. Beta; check the current docs for limits |

Other Anthropic products (Claude Code, the Claude Agent SDK) also have sub-agent features. Check their current docs before you describe their configuration in an interview.

## Practice

Original prompts in the style of a design round. Two minutes each.

1. "A customer wants an agent that reviews 300 supplier contracts for a change-of-control clause. Single loop or orchestrator-workers? Walk me through the brief and the report."
2. "Your colleague proposes adding a second Opus 'verifier agent' that re-answers every support ticket and votes with the first. What do you say?"
3. "One of your ten workers keeps timing out. What does the user see, and what does your dashboard show?"

> **Key takeaways**
> - A sub-agent is a separate conversation with its own context, tools and model; only its report comes back.
> - Split for context isolation, parallelism, a cheaper model on bulk reading, or narrower permissions. Don't split one-question-at-a-time work or add checker passes that multiply cost.
> - Briefs are self-contained and scoped to one item; reports are structured, compact, carry evidence, and are checked in code before the lead reads them.
> - Cap each worker, budget the run, treat partial results as normal, and tell the lead what wasn't checked.
> - Put thinking in the cost estimate and set effort explicitly on both tiers; the lead's call is often the biggest line.
