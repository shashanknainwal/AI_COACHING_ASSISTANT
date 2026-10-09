---
title: "Cost at Scale: Caching, Routing, Batch and the Number That Matters"
type: reading
minutes: 20
---

> **By the end of this lesson** you'll be able to price a workload from its four token meters, design prompts that cache at volume, decide when routing and the Batch API pay off, control output length, and defend a cost estimate in units of cost per completed task.

## How this comes up in interviews

Applied AI roles are customer-facing: Anthropic's Applied AI Engineer posting describes a technical advisor who takes customers from discovery to deployment (Official, from the job posting). Customers ask what it will cost before they ask anything else. In design rounds, cost is the follow-up to almost every architecture choice (Reported, see module E6). The interviewer wants three things: arithmetic done out loud, the levers in a sensible order, and a unit of measure that can't be gamed.

Module C2 covered the caching basics and break-even math. This lesson is about running the numbers for a real workload at volume. The FDE track's "Cost Modeling" lesson is optional background.

## The unit: cost per completed task

Cost per token and cost per request both mislead. A cheap model that fails a third of the time bills its tokens, then the retry, then whatever the failure costs downstream. Anthropic's own cost guidance frames optimization in units of **cost per completed task**: total spend on a task type, including failed attempts and retries, divided by the number of tasks that actually finished correctly.

That definition forces two things into your design:

1. **A definition of "completed".** A validator, a schema check, an eval grader, or a human acceptance signal. Without one you can't compute the number.
2. **Per-task accounting.** Every call carries a task id and type, so failures are charged to the task that caused them.

In an interview, say it early: "I'll compare options on cost per completed task, measured against our eval, not on price per million tokens."

## Four meters, five rates

Every response's `usage` reports four token counts. Each has its own rate. Claude Opus 5.5 (US dollars per million tokens):

| Meter | Opus 5.5 rate | Notes |
|---|---:|---|
| `input_tokens` (uncached remainder) | $4.00 | Only the part after the last cache hit |
| `cache_creation_input_tokens` | $5.00 (5-minute TTL), $8.00 (1-hour TTL) | 1.25x and 2x input; `usage.cache_creation` splits it by TTL |
| `cache_read_input_tokens` | $0.20 | 0.05x input on this model and on Sonnet 5.5; 0.1x on most others |
| `output_tokens` | $20.00 | Includes thinking tokens |
| Batch API | $2.00 input / $10.00 output | 50% off every meter, cache reads and writes included |

Two consequences that strong candidates mention unprompted:

- **Output is five times the price of input here, and thinking is output.** Effort is a cost lever, not just a quality dial.
- **With deep cache discounts, a cache miss is relatively expensive.** Anything that silently breaks the cache multiplies the bill without a single error.

## Worked example: invoice extraction at volume

Ledgerline (fictional) extracts fields from 200,000 invoices a month. Each request has a 12,000-token stable prefix (instructions, schema, worked examples), a 3,000-token invoice, and a 600-token JSON answer. On Claude Sonnet 5.5 ($2 input, $10 output, $0.10 cache read):

| Configuration | Per request | Per month |
|---|---:|---:|
| No caching: 15,000 × $2 + 600 × $10 | $0.0360 | $7,200 |
| Prefix cached (steady state): 12,000 × $0.10 + 3,000 × $2 + 600 × $10 | $0.0132 | $2,640 |
| Cached and sent through the Batch API (half of the line above) | $0.0066 | $1,320 |

Read the table the way an interviewer would:

- Caching cut the bill by about 63%. Output is now 45% of what's left, so the next lever is output length, then effort, then model choice.
- The batch line is a ceiling, not a promise: cache hits inside a concurrent batch are best-effort.
- Per-token prices differ by 40x between Haiku 5.5 ($0.10 input) and Opus 5.5 ($4). That spread is why routing matters, and also why you must measure quality per route before trusting a cheap one.

## Caching at scale

The C2 rules still hold: prefix match over tools, then system, then messages; stable content first; verify with `cache_read_input_tokens`. At volume, five more things decide your hit rate:

1. **Put the breakpoint at the end of the shared part.** If every request ends with unique content (an invoice, a retrieved chunk), automatic caching places the breakpoint after that unique tail, and you pay the write premium on bytes nobody reads back. Mark the end of the shared prefix explicitly. You get up to four breakpoints per request.
2. **Choose the TTL from the gaps between requests.** A cache read refreshes the timer for free. Requests that share a prefix and start less than five minutes apart keep the default cache warm forever; the 1-hour TTL pays only when gaps run 5 to 60 minutes. Measure the start-to-start gaps, not their average.
3. **Caches are per model and per workspace.** A router that sends the same prefix to three models writes three cache entries. Two workspaces sending the same prompt don't share one either.
4. **Short prefixes don't cache.** Each model has a minimum cacheable length (listed as 512 tokens for the newest models, up to 4,096 on some older ones). Below it, nothing is cached and nothing errors.
5. **Settings are part of the cache key.** Changing top-level `effort` or `thinking` between requests invalidates the messages cache, so pin them per route rather than per request.

Caching also buys throughput: on the Claude API, cache reads don't count toward input-token rate limits on most models.

## Model routing

Routing sends each task to the cheapest model that does it well enough. It's the lever with the biggest per-token spread and the most ways to go wrong.

**Measure the simple alternative first.** Before building a multi-model cascade, run the most capable model at lower effort on the same tasks. Anthropic's guidance notes that lower effort on the newest models often matches older models at higher effort, and one model means one cache namespace and one thing to evaluate.

**Route by task type, not by guesswork.** Classification and field extraction with checkable outputs are the classic cheap routes. Long agentic loops and judgment-heavy work are not.

**Know each route's constraints:**

| Route detail | Why it matters |
|---|---|
| Haiku 5.5's $0.10 / $0.50 price applies to prompts up to 100K tokens | Higher rates apply beyond it; send long prompts elsewhere |
| Haiku 5.5 has no server-side refusal fallback | Handle refusals in your own code on that route |
| Opus 5.5, Sonnet 5.5 and Haiku 5.5 each have their own rate-limit pool | Routing spreads load across pools; a fallback model needs its own headroom |
| Switching models mid-conversation | Cold cache, and the new model runs without the old model's thinking blocks |

**Price the tail.** On easy tasks every model looks alike and the cheapest looks best. The bill is decided by the hard tenth, where the cheap model fails and you pay twice.

## Batch: when nobody is waiting

The Message Batches API runs requests asynchronously at 50% of standard prices, and the discount stacks with caching.

- Up to 100,000 requests or 256 MB per batch. Most finish within an hour; the limit is 24 hours, and that's an expiry, not a service-level promise.
- Results come back in any order. Key them by `custom_id`, never by position.
- Each request is single-shot: no tool loop inside a batch.
- Some features aren't accepted there, including the server-side `fallbacks` parameter and fast mode.

Good fits: nightly re-extraction, eval runs, backfills, re-scoring a corpus after a prompt change. Bad fits: anything a user is watching.

## Output length and effort

- **`max_tokens` is a backstop, not a tuning knob.** The model doesn't see it. Hitting it cuts the answer off with `stop_reason: "max_tokens"`, and you pay for a broken result. Treat that as a failed attempt.
- **Shorten answers with a spec.** "Return only the JSON object" or a short example of the expected shape cuts output tokens more reliably than a low cap.
- **Sweep effort per route.** On Opus 5.5 the default is `medium`. Run your eval at neighbouring levels and keep the lowest one that holds quality. Workloads differ: knowledge work often has flat curves; long-horizon coding usually doesn't.

## Measuring spend

- **Log `usage` on every call**, with the route, model, task id and whether the task completed. That gives you hit rate, the input/output split and cost per completed task without any extra API calls.
- **Reconcile with the bill.** With an Admin API key, the Usage and Cost Admin API reports token usage (`GET /v1/organizations/usage_report/messages`) and dollar cost (`GET /v1/organizations/cost_report`) by model and workspace. Data shows up within about five minutes. Traffic on Amazon Bedrock, Google Vertex AI or Microsoft Foundry is billed by those platforms and isn't in these reports.
- **Apply levers one at a time** and re-run the eval after each, so you know which change saved money and which one cost quality.

## Practice (say it out loud)

Original prompts in the style of an applied AI design or customer round:

- "A customer runs 50,000 support conversations a day, averaging six turns, with an 8,000-token system prompt. Estimate the monthly bill on Sonnet 5.5 with and without caching, then tell me the next two levers."
- "Finance wants a 30% cut by next quarter without a drop in quality. What do you do in week one?"
- "Your teammate proposes routing everything to Haiku. What do you need to see before you agree?"

> **Key takeaways**
>
> - Compare options on cost per completed task, including failures and retries, measured against an eval.
> - Price all four meters. Output (and thinking) usually dominates once the prefix is cached.
> - At volume, hit rate depends on breakpoint placement, TTL versus request gaps, and keeping one model and stable settings per route.
> - Routing has the biggest price spread but splits caches and adds routes to evaluate. Try the strong model at lower effort first.
> - Batch halves every meter for work nobody is waiting on. `max_tokens` is a backstop; shorten output with a spec.
