---
title: "Cost Modeling: Caching, Effort, Batches and Model Choice"
type: reading
minutes: 6
---

> **By the end of this lesson you will be able to:**
> - Build a per-request and monthly cost model from measured usage
> - Rank the cost levers: model, effort, caching, batching, prompt size
> - Pick the cheapest configuration that meets the eval bar

Brightway's CFO asks Jordan what the agent will cost per month, and whether something cheaper is just as good. *"$340 a month at 5,000 tickets a day"* moves the project forward; "it depends on usage" stalls it.

## Measure, then project

Run the system on realistic inputs (your eval set) and read `response.usage`:

```python
usage = response.usage
usage.input_tokens                 # uncached input
usage.cache_creation_input_tokens  # written to cache this request
usage.cache_read_input_tokens      # read from cache
usage.output_tokens                # includes thinking
```

Price all four, then `monthly cost = cost per request × requests per day × 30`. State assumptions (traffic, token sizes, cache hit rate, model, effort) and show a range: "$340 today; $1,140 if caching stops working; $680 at double the volume."

## The levers

| Lever | Typical effect | Trade-off |
|---|---|---|
| **Model choice** | 2-4× between tiers | Quality on hard cases; check with evals |
| **Prompt caching** | Up to ~95% off a long, stable prefix | Prefix must be identical and over the minimum length; first request pays a write premium |
| **Effort** | Large changes in output (thinking) tokens | Less reasoning on hard cases |
| **Message Batches** | 50% off every token type | Results arrive asynchronously (usually well within 24 hours) |
| **Shorter outputs and prompts** | Output costs 5× input per token | Don't cut what drives quality |

- **Effort:** output (including thinking) is the priciest token type. For classification, `effort: "low"` often matches higher effort at a fraction of the output tokens. (Claude Haiku 4.5 doesn't accept `effort`.)
- **Caching:** stable content first, the varying ticket last. A prefix under the minimum cacheable length silently gets no caching, so **verify with `cache_read_input_tokens`**. The cache expires after a few minutes without use: at 5,000 requests a day nearly every request hits; at 20 a day, few do.
- **Batches:** half price for anything that can wait (nightly re-triage, eval runs); combines with caching.

## Choosing a configuration

| Configuration | Eval pass rate | Monthly cost |
|---|---|---|
| Opus 5.5, medium effort | 95% | $1,518 |
| Opus 5.5, low effort | 94% | $768 |
| Sonnet 5.5, low effort | 93% | $339 |
| Haiku 4.5 | 86% | $161 |

With a 92% bar, Sonnet at low effort wins at under a quarter of the top option's cost. Haiku fails the bar, however cheap, and so does anything failing a critical-slice rule (lesson 7). Present it as a decision: "Sonnet at low effort: 93%, $339 a month. Opus would add one to two points for an extra $429-1,179 a month. We recommend Sonnet and will re-check quarterly."

In production, log usage per request, set budget alerts, and re-measure after prompt changes: a timestamp in the system prompt silently breaks caching.

> **Key takeaways**
> - Measure on realistic inputs, price all four token types, project with stated assumptions and a range.
> - Biggest levers: model, caching, effort, batches, then output and prompt size.
> - Verify caching with `cache_read_input_tokens`.
> - Choose the cheapest configuration that clears the bar, critical slices included, and present options.
