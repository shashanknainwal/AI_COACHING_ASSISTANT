---
title: "Sub-Agents in Practice: When Splitting Pays and When It Doesn't"
type: reading
minutes: 14
---

> **By the end of this lesson you will be able to:**
> - Explain the orchestrator-workers pattern and what context isolation buys you.
> - Size a worker model, an effort level and a per-worker budget, with thinking tokens counted.
> - Design failure isolation so one bad worker never sinks the run, and say when not to split at all.

E2's sub-agents lesson introduced the pattern. This one is about the decisions a customer will push you on: which model the workers run, what a run costs, what happens when a worker fails, and whether splitting was worth it compared with one agent.

## The pattern in one paragraph

An orchestrator plans the work and hands each independent piece to a worker. Each worker gets a fresh context holding only its piece, does the reading, and returns a short structured report. The orchestrator never sees the raw material, only the reports, so its context stays small however much work fans out. On Managed Agents, a multiagent session does this for you: each worker runs in its own thread with its own history, model and tools, sharing the container's filesystem but not its conversation.

## What context isolation buys

- **A small orchestrator context.** Twenty contracts produce twenty short reports, not twenty full documents in one window.
- **No cross-talk.** A worker that only ever sees contract CC-104 can't confuse its liability cap with CC-105's.
- **Failure you can see.** When one worker fails, the others are untouched and the orchestrator is told exactly what wasn't covered.

Isolation is about what goes into each worker's messages. If a worker's first request mentions another item, you leaked context, and you lose all three benefits.

## Cheaper workers, honestly priced

Reading-heavy worker tasks (search, read, extract) are many input tokens and little hard reasoning, which is what a smaller model is for. Use the current generation: **Claude Haiku 5.5** ($0.10 input, $0.50 output per million tokens for prompts up to 100K tokens) for bulk extraction, or Claude Sonnet 5.5 when a worker needs more judgement. Keep planning, checking and synthesis on Claude Opus 5.5 ($4 / $20).

Every cost estimate needs the thinking line. All three current models think by default with adaptive thinking, thinking tokens are billed as output, and `max_tokens` covers thinking. Haiku 5.5 and Opus 5.5 default to `medium` effort, Sonnet 5.5 to `high`. So set `effort` explicitly on every worker call (`low` is usually right for extraction) and leave `max_tokens` room for the thinking, or your estimate understates the bill and your workers get cut off mid-thought.

## Budgets and failure isolation

- **Check budgets before spending.** Count a worker's input tokens before the call (`messages.count_tokens` is cheap) and route an oversized item to a different path instead of letting it blow the run.
- **Cap each worker.** A per-worker cap on calls and output tokens stops one wandering worker.
- **Never let a worker raise.** Catch the SDK's API error after its own retries, a refusal, a cut-off answer and a report about the wrong item, and turn each into a failed result with a reason.
- **Tell the orchestrator what wasn't done.** A gap reported as a gap gets a human check. A gap that silently disappears looks like a clean result.

## When not to split

Splitting has overheads: more calls, an orchestrator turn, and a cache that doesn't carry across models. Don't split when:

- **The work doesn't divide.** A single question answered by one reasoning chain gains nothing from workers.
- **The pieces depend on each other.** If item 7 needs item 3's answer, a fan-out serialises anyway.
- **The task is answered one question at a time.** A support or Q&A agent should do its own work and check it; adding checker or voter agents multiplies the cost of every answer.
- **A simpler baseline wins.** Before claiming sub-agents beat one big call, measure the single call on a cheaper model or at lower effort against the same answer key. Lower effort on the newest models often holds quality, and one model means one cache.

## Proving it paid off

The claim "sub-agents are cheaper and better" is an eval result, not an architecture fact. Measure cost per completed task and recall against an answer key for both designs, and report what each one failed to cover. In the next exercise the fan-out is cheaper, but the bigger win is that it names the two contracts it couldn't review while the single long-context run silently skipped three.

> **Key takeaways**
> - Orchestrator-workers keeps the orchestrator's context small by giving each worker only its piece and passing back short reports.
> - Run bulk reading on Haiku 5.5 or Sonnet 5.5 and synthesis on Opus 5.5; set `effort` explicitly and count thinking as output.
> - Check budgets before spending, cap each worker, never let a worker raise, and report every gap to the orchestrator.
> - Don't split work that doesn't divide, pieces that depend on each other, or one-question-at-a-time agents.
> - "Sub-agents won" is an eval result: compare cost and recall against a fair single-agent baseline.
