---
title: "Cost Modeling: Caching, Effort, Batches and Model Choice"
type: reading
minutes: 16
---

> **By the end of this lesson you will be able to:**
> - Build a per-request and monthly cost model from measured token usage
> - Rank the cost levers by impact: model, effort, caching, batching and prompt size
> - Choose the cheapest configuration that meets the quality bar set by your evals
> - Present cost to a customer with clear assumptions

## Cost is a feature

Customers approve projects on two numbers: how well it works, and what it costs. An FDE who can say *"$380 a month at 5,000 tickets a day, about 8 cents per 100 tickets, and here's how it scales"* moves a project forward. "It depends on usage" stalls it.

## Measure, then project

**Measure** real usage by running your system on realistic inputs (your eval set is perfect for this) and reading `response.usage`:

```python
usage = response.usage
usage.input_tokens                 # uncached input
usage.cache_creation_input_tokens  # written to cache this request
usage.cache_read_input_tokens      # read from cache
usage.output_tokens                # includes thinking
```

Price all four (Module 6 covered the formula). Then **project**:

```
monthly cost = cost per request × requests per day × 30
```

Write down every assumption: traffic (and peaks), average input and output size, cache hit rate, model and effort. Show a range: "$340 at today's volume; $1,140 if caching stops working; $680 at double the volume." Customers trust models that show their assumptions.

## The levers, roughly by impact

| Lever | Typical effect | Trade-off |
|---|---|---|
| **Model choice** | 2-4× between tiers | Quality on hard cases; check with evals |
| **Prompt caching** | Up to ~95% off a long, stable prefix | Prefix must be identical and over the minimum length; first request pays a write premium |
| **Effort** | Large changes in output (thinking) tokens | Less reasoning on hard cases |
| **Message Batches** | 50% off every token type | Results arrive asynchronously (usually well within 24 hours) |
| **Shorter outputs** | Output costs 5× input per token | Answers must stay complete |
| **Smaller prompts** | Fewer input tokens per request | Don't cut instructions that drive quality |

### Model choice

Run the eval suite on each candidate model and pick the cheapest that clears the bar, as you did with routing in Module 6. Often the answer is "different models for different tasks": a fast model for triage, the most capable model for complex customer conversations.

### Effort and thinking

Output tokens include thinking, and output is the most expensive token type. For classification and extraction, `effort: "low"` often matches higher effort in quality at a fraction of the output tokens. Measure: compare output tokens and eval scores at each effort level. (Remember that Claude Haiku 4.5 doesn't accept the effort parameter.)

### Prompt caching

Caching pays off when a long prefix (system prompt, examples, documents, tool definitions) repeats across requests:

- Put stable content first and anything that varies (the ticket, the user's question) last.
- Check your prefix is above the minimum cacheable length. A prompt just under the minimum silently gets no caching. **Verify with `cache_read_input_tokens`**, never assume.
- The cache expires after a few minutes without use, so the hit rate depends on traffic. At 5,000 requests a day, nearly every request hits. At 20 a day, few will.

### Batches

The Message Batches API processes large sets of requests asynchronously at half price. It suits anything that doesn't need an immediate answer: nightly re-triage of the backlog, running evals, enriching a CRM export, summarizing yesterday's calls. Live chat and real-time routing still use normal requests. Batching and caching can be combined.

## Choosing a configuration

Put eval results and cost side by side:

| Configuration | Eval pass rate | Monthly cost |
|---|---|---|
| Opus 5.5, medium effort | 95% | $1,518 |
| Opus 5.5, low effort | 94% | $768 |
| Sonnet 5.5, low effort | 93% | $339 |
| Haiku 4.5 | 86% | $161 |

With a 92% bar agreed with the customer, Sonnet at low effort wins: it clears the bar at under a quarter of the top option's cost. Haiku is cheapest but fails the bar, so it isn't an option, however tempting the price. Also check the slices: a configuration that clears the overall bar but fails the critical-slice rules from lesson 7 doesn't qualify either.

Present it as a decision with options: "Sonnet at low effort: 93%, $339 a month. Opus would add one to two points for an extra $429-1,179 a month. We recommend Sonnet and will re-check quarterly."

## Cost in production

- **Log usage per request** with a feature tag, so you can see which feature drives cost.
- **Set budgets and alerts:** a bug that disables caching or a loop that calls Claude repeatedly can multiply cost overnight.
- **Re-measure after changes:** a prompt edit that moves a timestamp into the system prompt can silently break caching.

> **Key takeaways**
> - Measure usage on realistic inputs, price all four token types, project monthly with stated assumptions and a range.
> - Biggest levers: model choice, caching, effort, batches, then output and prompt size.
> - Verify caching with cache_read_input_tokens; a prompt under the minimum length silently gets no caching.
> - Choose the cheapest configuration that clears the eval bar (including critical slices), and present it as a decision with options.
