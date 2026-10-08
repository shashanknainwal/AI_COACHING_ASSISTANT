---
title: "Exercise: A 12-Month Cost of Ownership Model"
type: exercise
minutes: 40
hints:
  - "`monthly_api_cost`: return `0.0` when `prices is None`. Use `workload.get(key, default)` everywhere so missing fields count as 0 (and `caching` as False)."
  - "The prefix rate is `prices[\"input\"]` without caching, otherwise `hit * prices[\"cache_read\"] + (1 - hit) * prices[\"cache_write\"]`. Per request: `(prefix * prefix_rate + input * prices[\"input\"] + output * prices[\"output\"]) / 1_000_000`."
  - "Batch: multiply the monthly total by `1 - batch_share * (1 - BATCH_DISCOUNT)`. Round only the final number to 2 decimals."
  - "`cumulative_costs`: start `total` at `one_time`. For each month 1..months add the option's run cost if `month >= go_live_month`, else the baseline's run cost (0 with no baseline). Append `round(total, 2)`."
  - "`compare`: build the baseline curve once. For every other option, the break-even month is the first `m + 1` where `curve[m] <= base_curve[m]`, else `None`. Sort by `(total, name)` and add `rank` starting at 1."
---

Grace Liu here. **Harborview Mutual** (fictional) is an insurer that processes about 40,000 claim documents a month. Today a team of adjusters reads every one: eight minutes each, at a fully loaded $42 an hour. The VP of Claims has two proposals on her desk. One is a claims-intake product from an independent software vendor built on a frontier model. The other is an internal build on the Claude API that her platform team wants to own.

She asked us one question: "Which one is cheaper, and when does it pay for itself?" The honest answer is "it depends on the horizon and on how much human review each option still needs", so we'll show her the numbers instead of an opinion. Build the model in plain Python. Prices are passed in, never hard-coded in the math, so we can re-run it when the price list changes or the customer moves to a cloud platform with different rates.

## The inputs

An **option** looks like this (three are given in `OPTIONS`):

```python
{
    "name": "build_api",
    "one_time": 250_000,      # build cost, charged in month 1
    "monthly_fixed": 18_000,  # ops, hosting, licences, maintenance engineering
    "go_live_month": 4,       # first month the option runs; before that the old process continues
    "prices": SONNET_PRICES,  # $ per million tokens, or None if the option makes no API calls we pay for
    "workload": {
        "requests": 40_000, "prefix_tokens": 6_000, "caching": True, "cache_hit_rate": 0.95,
        "input_tokens": 4_000, "output_tokens": 800, "batch_share": 0.6,
        "review_rate": 0.15, "review_minutes": 4, "reviewer_hourly": 42,
    },
}
```

`prefix_tokens` is the shared, stable part of each prompt (instructions, schema, examples). `input_tokens` is the per-document part. Missing workload fields count as 0 (`caching` defaults to False).

## Your task

**1. `monthly_api_cost(workload, prices)`**, rounded to 2 decimals. `prices=None` returns `0.0`.

- Prefix rate: `input` without caching. With caching, a `cache_hit_rate` share of requests reads the prefix at `cache_read` and the rest write it at `cache_write`.
- Per request: `(prefix x prefix rate + input_tokens x input + output_tokens x output) / 1,000,000`.
- Monthly: `requests x per request`, then apply the batch discount to the `batch_share` fraction of traffic: multiply by `1 - batch_share x (1 - BATCH_DISCOUNT)`.

**2. `monthly_review_cost(workload)`**: `requests x review_rate x review_minutes / 60 x reviewer_hourly`, rounded to 2 decimals.

**3. `monthly_run_cost(option)`**: `monthly_fixed` plus the two costs above, rounded to 2 decimals.

**4. `cumulative_costs(option, months=12, baseline=None)`**: a list of `months` running totals, each rounded to 2 decimals. Month 1 includes `one_time`. Months before `go_live_month` cost the **baseline's** run cost (the old process is still doing the work), or 0 with no baseline. From go-live on, the option's own run cost applies.

**5. `compare(options, months=12, baseline_name=None)`**: one row per option, sorted by total ascending (ties by name):

```python
{"name": "build_api", "total": 1239564.64, "monthly_run": 35284.96, "break_even_month": 5, "rank": 1}
```

- `total` is the last cumulative value. Each non-baseline option uses the baseline for its pre-live months.
- `break_even_month` is the first month (1-based) where the option's cumulative cost is at or below the baseline's. `None` for the baseline itself, for an option that never catches up within the horizon, and for every option when `baseline_name` is `None`.
- Raise `ValueError("unknown baseline: <name>")` if the baseline isn't in the list, and `ValueError` mentioning "unique" if two options share a name.

Press **Run** to print Harborview's comparison, then **Submit**.

## Read the result like an architect

Once it passes, look at what the numbers say. They are the point of the exercise:

- **Model spend is under $500 a month.** Human review is $16,800 and fixed costs are $18,000. On most document workflows the API bill is the smallest line. The decision turns on review rate and time to value, not token prices.
- **The horizon flips the answer.** Over 12 months the build is cheapest. Over 6 months, buying wins because it goes live in month 2. State the horizon in the first line of your recommendation.
- **Every input is an assumption.** The 15% review rate is a guess until a proof of concept measures it. Run the model at 25% and see how the ranking moves. That is your sensitivity analysis, and the subject of lesson 4.

## Defend it

Original practice prompts in the style of a solutions architect case round:

- "The vendor quotes a flat licence. What would you ask before you trust their 30% review rate?" Ask for their measured accuracy on *your* documents, with your reviewers, in a paid pilot.
- "Your build is cheaper over a year. Why might you still recommend buying?" Time to value, the team's skills, maintenance risk, and whether claims intake is core to how the insurer competes.
- "Token prices drop by half next year. How does your recommendation change?" Here, barely: API spend is under 2% of the build option's run cost.
