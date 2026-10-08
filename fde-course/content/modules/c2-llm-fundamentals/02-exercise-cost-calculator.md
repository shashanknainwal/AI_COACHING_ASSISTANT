---
title: "Exercise: Build a Cost Calculator"
type: exercise
minutes: 30
hints:
  - "Read each count with `usage.get(key) or 0`. That handles a missing key and a value of `None` in one step."
  - "Each token type has its own price: input_tokens uses `input`, output_tokens uses `output`, cache_read_input_tokens uses `cache_read`, cache_creation_input_tokens uses `cache_write`."
  - "Prices are per million tokens, so divide the summed `tokens x price` by 1,000,000 before rounding."
  - "Write a private helper that returns the unrounded cost. `request_cost` rounds it to 6 decimals; `monthly_cost` multiplies it by `requests_per_day * days` and only then rounds to 2."
---

Your interview coach, Nadia Okafor, runs mock design rounds, and she has noticed a pattern: candidates draw a good architecture, then freeze when she asks "so what does this cost a month?" Her fix is simple. Build the calculator yourself once, in code, and the arithmetic stops being scary.

You'll write the function you'd want in any LLM project: take the `usage` block an API response returns, plus a price table, and turn it into dollars. Then scale it to a month. The price table is passed in, never hard-coded, because prices change and interviewers like to change them mid-question.

## The inputs

`usage` mirrors the `usage` object on a Claude API response:

```python
usage = {
    "input_tokens": 1000,                  # uncached input, billed at the base input price
    "output_tokens": 400,                  # everything the model wrote, including thinking
    "cache_read_input_tokens": 20000,      # input served from the prompt cache
    "cache_creation_input_tokens": 0,      # input written to the cache on this request
}
```

`input_tokens` is only the uncached part. The total prompt is the sum of the three input fields. The two cache fields may be missing or `None`; treat either as 0.

`prices` is one model's row, in **dollars per million tokens**:

```python
prices = {"input": 2.00, "output": 10.00, "cache_read": 0.20, "cache_write": 2.50}
```

## Your task

**1. `request_cost(usage, prices)`** returns the cost of one request in dollars, rounded to **6** decimals:

```
(input_tokens x input + output_tokens x output
 + cache_read_input_tokens x cache_read
 + cache_creation_input_tokens x cache_write) / 1,000,000
```

**2. `monthly_cost(requests_per_day, usage, prices, days=30)`** returns the cost of `requests_per_day` identical requests for `days` days, rounded to **2** decimals. Round only the final total. Rounding each request first can be badly wrong for cheap, high-volume calls.

## Example

```python
sonnet = {"input": 2.00, "output": 10.00, "cache_read": 0.20, "cache_write": 2.50}

warm = {"input_tokens": 1000, "output_tokens": 400,
        "cache_read_input_tokens": 20000, "cache_creation_input_tokens": 0}
request_cost(warm, sonnet)            # -> 0.01   (0.004 cache read + 0.002 input + 0.004 output)

cold = {"input_tokens": 1000, "output_tokens": 400,
        "cache_read_input_tokens": 0, "cache_creation_input_tokens": 20000}
request_cost(cold, sonnet)            # -> 0.056  (the first request pays the cache write)

monthly_cost(50_000, warm, sonnet)    # -> 15000.0
```

Press **Run** to try the sample at the bottom of the file, then **Submit** to grade it.

> **Interview tip:** When you give a cost estimate, say the per-request number first, then the monthly total, then the biggest lever. "About a cent a request, $15K a month, and most of the input is cached already, so the next lever is output length."
