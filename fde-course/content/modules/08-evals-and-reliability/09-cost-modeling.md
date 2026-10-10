---
title: "Cost Modeling: Caching, Effort, Batches and Model Choice"
type: reading
minutes: 8
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
| **Model choice** | 20-40× between tiers: Haiku 5.5 ($0.10/$0.50) is 20× cheaper than Sonnet 5.5 and 40× cheaper than Opus 5.5 | Quality on hard cases; check with evals |
| **Prompt caching** | A long, stable prefix read from cache costs 0.05× input on Opus 5.5 and Sonnet 5.5 (95% off), 0.1× on Haiku 5.5 and most other models (90% off) | Prefix must be identical and at least 512 tokens on current models; the first request pays a write premium (1.25× for the 5-minute cache) |
| **Effort** | Large changes in output (thinking) tokens | Less reasoning on hard cases |
| **Message Batches** | 50% off every token type | Results arrive asynchronously (usually well within 24 hours). Only on the Claude API and Claude Platform on AWS |
| **Shorter outputs and prompts** | Output costs 5× input per token | Don't cut what drives quality |

- **Effort:** output (including thinking) is the priciest token type, and every current model thinks by default. With no `effort` set, Sonnet 5.5 runs at `high` and Opus 5.5 and Haiku 5.5 at `medium`. Set it explicitly in your cost model, or your output-token estimate is a guess. For classification, `effort: "low"` often matches higher effort at a fraction of the output tokens.
- **Caching:** stable content first, the varying ticket last. A prefix under the minimum cacheable length silently gets no caching, so **verify with `cache_read_input_tokens`**. The cache expires after a few minutes without use: at 5,000 requests a day nearly every request hits; at 20 a day, few do. Always say which model a caching saving is for.
- **Batches:** half price for anything that can wait (nightly re-triage, eval runs); combines with caching. **Check the platform first.** Message Batches isn't available on Amazon Bedrock, Google Vertex AI or Microsoft Foundry. A customer who buys Claude through one of those can't count on the 50% saving; Bedrock and Vertex have their own batch offerings with their own terms, so check those platforms' docs. The [platform fit checker](/learn/a2-enterprise-deployment/03-exercise-platform-fit-checker) in the Architect track walks through these gaps.

## Choosing a configuration

At 5,000 tickets a day, 3,200 input tokens each (3,000 cached, 95% hit rate). Output tokens include thinking, so each row states its effort:

| Configuration | Output tokens (incl. thinking) | Eval pass rate | Monthly cost |
|---|---|---|---|
| Opus 5.5, medium effort | 400 | 95% | $1,518 |
| Opus 5.5, low effort | 150 | 94% | $768 |
| Sonnet 5.5, low effort | 120 | 93% | $339 |
| Haiku 5.5, low effort | 100 | 89% | $18 |

With a 92% bar, Sonnet at low effort is the cheapest option that passes, at under a quarter of the top option's cost. Haiku 5.5 fails the bar, and so does anything failing a critical-slice rule (lesson 7). But notice the gap: Haiku 5.5 costs about a twentieth of Sonnet. Before you accept Sonnet, spend one iteration on Haiku 5.5 (better examples in the prompt, a look at the failing slice). If it clears 92%, the saving is about 95%. At this volume that is $320 a month, which is small next to one misrouted safety ticket; at 500,000 tickets a day it is $32,000 a month, and worth weeks of prompt work.

Present it as a decision: "Sonnet at low effort: 93%, $339 a month. Opus would add one to two points for an extra $429-1,179 a month. Haiku 5.5 would cost about $18 but misses the bar by three points; we're running one more prompt iteration on it and will switch only if it passes, critical slices included. We'll re-check quarterly."

In production, log usage per request, set budget alerts, and re-measure after prompt changes: a timestamp in the system prompt silently breaks caching.

> **Key takeaways**
> - Measure on realistic inputs, price all four token types, project with stated assumptions and a range.
> - Biggest levers: model (20-40× between tiers), caching (state the model), effort, batches (Claude API and Claude Platform on AWS only), then output and prompt size.
> - Verify caching with `cache_read_input_tokens`.
> - Choose the cheapest configuration that clears the bar, critical slices included, and present options.
