---
title: "Exercise: A Cost Model for the Deployment"
type: exercise
minutes: 30
hints:
  - "`request_cost`: `(usage.input_tokens * p[\"input\"] + usage.cache_creation_input_tokens * p[\"cache_write\"] + usage.cache_read_input_tokens * p[\"cache_read\"] + usage.output_tokens * p[\"output\"]) / 1_000_000`, then multiply by `BATCH_DISCOUNT` if `batch`."
  - "`measure`: collect the responses first, then price each with `request_cost(r.model, r.usage)`. A cache hit is a response with `usage.cache_read_input_tokens > 0`."
  - "`monthly_cost` per request: `(input_tokens - cached_tokens)` uncached, `cached_tokens * cache_hit_rate` read from cache, `cached_tokens * (1 - cache_hit_rate)` written to cache, plus output."
  - "`cheapest_passing`: compute `monthly_cost(**option[\"params\"])` for options that meet the bar, then `min(passing, key=lambda o: o[\"monthly_cost\"])`."
---

The eval suite says several configurations are good enough. Brightway's CFO asks the next question: **"What will this cost per month, and is there a cheaper option that's just as good?"** You'll build a cost model from real usage data, project it to production traffic, and pick the cheapest configuration that clears the quality bar.

`PRICES` (per million tokens, all four token types), `BATCH_DISCOUNT`, and `triage_cached(client, text, model)` are given. `triage_cached` sends one triage request with a long system prompt marked for caching and returns the full response.

## Your task

**1. `request_cost(model, usage, batch=False)`** returns the dollar cost of one request from its `usage` (`input_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, `output_tokens`), rounded to 6 decimals. With `batch=True`, multiply by `BATCH_DISCOUNT`. Unknown model → `ValueError("no prices for <model>")`.

**2. `measure(client, tickets, model="claude-sonnet-5-5")`** runs `triage_cached` on every ticket and returns:

```python
{"requests": 20, "total_cost": 0.010109, "per_request": 0.000505, "cache_hit_rate": 0.95}
```

Round costs to 6 decimals and the hit rate to 3. A hit is a response that read from the cache.

**3. `monthly_cost(model, requests_per_day, input_tokens, output_tokens, cached_tokens=0, cache_hit_rate=0.0, batch=False, days=30)`** projects the monthly bill, rounded to 2 decimals. Of each request's `input_tokens`, `cached_tokens` are the cacheable prefix:
- `input_tokens - cached_tokens` are billed as normal input.
- `cached_tokens × cache_hit_rate` are billed as cache reads.
- `cached_tokens × (1 - cache_hit_rate)` are billed as cache writes.

**4. `cheapest_passing(options, min_pass_rate)`**: each option is `{"name", "pass_rate", "params"}`, where `params` are the keyword arguments for `monthly_cost`. Return `{"choice": {"name", "monthly_cost"}, "rejected": [names below the bar]}`, where `choice` is the cheapest option with `pass_rate >= min_pass_rate`, or `None` if no option qualifies.

Press **Run** to see measured costs and the monthly comparison (including what caching saves), then **Submit**.
