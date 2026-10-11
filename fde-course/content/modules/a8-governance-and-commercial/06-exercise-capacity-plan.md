---
title: "Exercise: Peak Capacity Planner"
type: exercise
minutes: 35
hints:
  - "Write a small `_validate` helper first: raise `ValueError` if `peak_factor < 1`, or if cache reads plus cache writes exceed `input_tokens`. Call it at the top of both functions."
  - "Peak requests are `math.ceil(calls_per_minute * peak_factor)`. Counted input per call is `input_tokens - cache_read_tokens`, unless the platform's limits say `cache_reads_count: True`, in which case all input counts. Cache writes always count."
  - "Build a `need` dict for rpm, itpm and otpm, then loop over `(\"rpm\", \"itpm\", \"otpm\")`: a breach is `need > limit`; tight is not a breach and `need > headroom * limit`. Use strict `>` both times, so exactly-at-limit is tight, not a breach."
  - "For `binding`, take the metric with the highest `need / limit`; on a tie keep the earlier metric in the order rpm, itpm, otpm. `max(METRICS, key=lambda m: (need[m] / lim[m], -METRICS.index(m)))` does it."
  - "Input burn per call is `(reads * rates['cache_read'] + writes * rates['cache_write_' + ttl] + uncached) * geo`, where geo is `rates['us_only']` when `inference_geo == 'us'`, else 1. Covered calls are `floor(min(itpm / in_burn, otpm / out_burn))`, capped at peak calls."
---

Owen Hartwell here, Head of AI Platform at **Brackenridge Bank** (fictional). Our customer-service assistant goes live before the end-of-year rush, and the last time we launched something, nobody checked the limits against peak. We found out on the first Monday.

I want a planner I can rerun every time the forecast or the limits change. It takes the workload, a peak factor and a table of limits per platform and region, and tells me which deployments breach at peak, which are uncomfortably close, and what the binding constraint is. Our procurement team also has a question about a capacity commitment measured the Priority Tier way, so I want the burn-down too.

The limits table loaded as `EXAMPLE_LIMITS` is **made-up placeholder numbers**. Real limits come from our own console and quota pages on the day. Never hard-code them.

## The data

A workload describes one model call at average load:

```python
{
    "calls_per_minute": 400,      # average model calls per minute
    "input_tokens": 14_000,       # TOTAL input per call: cache reads + cache writes + uncached
    "cache_read_tokens": 10_000,  # read from cache
    "cache_write_tokens": 500,    # written to cache
    "output_tokens": 700,         # includes thinking at the effort level you'll run
    "cache_ttl": "5m",            # "5m" or "1h" (used by the burn-down)
    "inference_geo": "global",    # "global" or "us" (used by the burn-down)
}
```

`limits` maps a deployment name to `{"rpm", "itpm", "otpm"}` and an optional `"cache_reads_count"` (default `False`: cache reads don't count toward input limits, as the Claude API docs say for most models).

## Your task

**1. `capacity_plan(workload, peak_factor, limits, headroom=0.8)`** returns a list with one row per deployment, sorted by name:

```python
{"platform": "bedrock_eu_sonnet", "peak_rpm": 1200, "peak_itpm": 4_800_000, "peak_otpm": 840_000,
 "utilization": {"rpm": 0.6, "itpm": 0.8, "otpm": 1.05},   # need / limit, rounded to 3 places
 "breaches": ["otpm"],      # need > limit, in the order rpm, itpm, otpm
 "tight": [],               # not a breach, but need > headroom x limit
 "status": "breach",        # "breach" if any breach, else "tight" if any tight, else "ok"
 "binding": "otpm"}         # highest utilization; ties go to the earlier metric
```

- Peak calls per minute: `calls_per_minute x peak_factor`, rounded **up**.
- Counted input per call: total input minus cache reads (unless `cache_reads_count` is true). Cache writes always count.
- Raise `ValueError` if `peak_factor` is below 1, or if cache reads plus cache writes exceed `input_tokens`.
- Don't modify the arguments.

**2. `priority_burndown(workload, peak_factor, commitment, rates)`** models a commitment of `{"itpm", "otpm"}` measured with the burn-down rates in `rates` (loaded as `PRIORITY_RATES`, from Anthropic's service tiers page). Return:

```python
{"input_burn_per_call": 5125.0, "output_burn_per_call": 700.0,   # rounded to 2 places
 "peak_input_burn": 6150000, "peak_output_burn": 840000,         # peak calls x burn, rounded
 "covered_rpm": 585, "overflow_rpm": 615, "covered_share": 0.487}
```

- Input burn per call: cache reads x `cache_read` + cache writes x `cache_write_5m` or `cache_write_1h` (from `cache_ttl`, default `"5m"`) + uncached input x 1. Multiply the whole input burn, and the output burn, by `us_only` when `inference_geo` is `"us"`. (The docs say the burn-down rates reflect relative pricing, and the pricing page applies the 1.1x US-only multiplier to every token category; that's the assumption here. Confirm it with the account team for a real commitment.)
- `covered_rpm`: how many calls per minute the commitment absorbs, limited by whichever of input or output runs out first, rounded down and capped at peak calls. The rest is `overflow_rpm`, which falls back to standard tier. `covered_share` is covered / peak, to 3 places.

## Example

With the Brackenridge workload, a peak factor of 3 and the placeholder table, the planner says the Claude API row breaches on input tokens (120%), the Bedrock row breaches on output tokens (105%), and the Vertex row is tight on input tokens (84%, because cache reads count there in this made-up table). Nothing is "ok". That's a useful answer: raise limits before launch, improve the cache hit rate, or lower output at the measured `effort` level, then rerun.

The burn-down shows a commitment of 3,000,000 ITPM and 500,000 OTPM covers 585 of 1,200 peak calls a minute. Remember the lesson: Priority Tier isn't sold to new customers and isn't supported on current 5.x models such as Sonnet 5.5. The function models existing commitments, or any capacity measured the same way.

> **Architect tip:** Present one line per deployment: status, binding meter, and the one change that fixes it. "Claude API: input tokens at 120% of the placeholder limit at peak. Raise the limit or lift the cache hit rate from 71% to 80%." Then rerun with the real numbers.
