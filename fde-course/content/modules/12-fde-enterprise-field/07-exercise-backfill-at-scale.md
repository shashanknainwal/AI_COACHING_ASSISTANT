---
title: "Exercise: The 50,000-Ticket Backfill, Done for Real"
type: exercise
minutes: 40
hints:
  - "`iter_chunks`: open the file, wrap it in `csv.DictReader`, then loop `chunk = list(islice(reader, chunksize))` until it comes back empty. Convert `INT_COLUMNS` to `int` in each row, then `yield chunk`."
  - "Pass 1 (`latest_attempts`): for every row in every chunk, keep the larger of `row[\"attempt\"]` and what's already stored for that ticket."
  - "Pass 2 (`aggregate`): skip rows whose attempt isn't the ticket's latest. A `defaultdict` of small dicts keyed by `(month, category or \"(none)\")` holds the running totals. Sums of chunk totals are still totals."
  - "Build the returned dict in `sorted(totals)` order and add `cost_usd` once per key at the end, with the given `cost()`."
  - "In `report`, sum tickets per month and per category (skipping `\"(none)\"`). For the earliest tie, `min(by_month, key=lambda m: (-by_month[m], m))`."
---

Sana Iqbal again. The overnight backfill finished: 50,000 historical support tickets classified so our routing rules can be retrained. The job wrote one row per model call to `/data/backfill_results.csv`. Before I tell our COO it worked, I need three numbers I trust: tickets by month and category, the refusal rate, and what it cost, including what the retries cost us.

One complication. About 3% of tickets hit `max_tokens` on the first try. The job re-ran those at the end with a higher limit and appended the new rows to the bottom of the file. So a ticket can appear twice, far apart, and only its latest attempt counts.

## Why chunks, at only 50,000 rows

Honestly, this file fits in memory. The real one next quarter is every ticket since 2016, and the analytics VM you'll get has 4 GB of RAM. So you'll practise the pattern here, where you can check it: stream the file in chunks, aggregate each chunk, and keep only small running totals, so memory doesn't grow with the input. Sums and counts combine across chunks. **Deduplication doesn't**: a ticket's two attempts can be in different chunks. That's why this takes two passes. The first pass finds each ticket's latest attempt, which is one small number per ticket. The second pass aggregates.

You'll use only the standard library (`csv`, `itertools`, `collections`). In production you'd likely use pandas, DuckDB or polars; the pattern is the same.

## The data

The rows below show the format; the values are examples.

```
ticket_id,attempt,month,category,stop_reason,input_tokens,output_tokens
T000001,1,2025-03,billing,end_turn,1432,188
T000002,1,2024-07,,max_tokens,2210,256      <- re-run later as attempt 2
T000003,1,2025-11,,refusal,980,0
...
T000002,2,2024-07,card,end_turn,2210,512
```

The job ran on Claude Haiku 5.5 with `effort: "low"`. `output_tokens` already includes thinking tokens, which are billed as output. `cost(input_tokens, output_tokens)` is given and uses Haiku 5.5's prices for prompts under 100K tokens: $0.10 input and $0.50 output per million tokens.

## Your task

**1. `iter_chunks(path, chunksize)`** is a **generator** that yields lists of at most `chunksize` rows. Each row is a dict from `csv.DictReader` with `attempt`, `input_tokens` and `output_tokens` converted to `int`. Every other function reads the file only through `iter_chunks` (the tests watch it).

**2. `latest_attempts(path, chunksize)`** returns a dict of `ticket_id` to its highest `attempt`.

**3. `aggregate(path, chunksize)`** returns a dict keyed by `(month, category)`, in sorted key order:

```python
{("2024-01", "(none)"): {"tickets": 13, "refusals": 13, "input_tokens": 19369, "output_tokens": 0, "cost_usd": 0.0019},
 ("2024-01", "billing"): {...}, ...}
```

- Count **only each ticket's latest attempt**.
- `refusals` counts rows whose `stop_reason` is `"refusal"`.
- An empty category becomes `"(none)"`.
- `cost_usd` comes from `cost()`.

The result must not depend on the chunk size.

**4. `retry_overhead(path, chunksize)`** returns the dollars spent on attempts that a later attempt replaced.

**5. `report(table)`** returns:

```python
{"tickets": 50000, "refusal_rate": 0.0124, "cost_usd": 14.37,
 "busiest_month": "2025-11", "top_category": "billing"}
```

`refusal_rate` is rounded to 4 places and `cost_usd` to 2. `busiest_month` has the most tickets, and the earliest month wins a tie. `top_category` has the most tickets, ignoring `"(none)"`, and the first name alphabetically wins a tie.

Press **Run** to see the first rows of the table and the report.

## What you'd tell Sana

Lead with the numbers, then the caveats: "50,000 tickets classified for $14.37, plus $0.44 of re-runs. 1.24% were declined. Those are in the '(none)' rows, and I'm sampling them by hand to see whether they're legitimate fraud-related tickets the classifier tripped on (lesson 08 is about that). November 2025 was the busiest month." The refusal rate is small, but it isn't zero, and in a bank the declined tickets are the ones someone will ask about.

> **FDE tip:** Keep the raw per-call file. When someone questions a number in three weeks, the answer is a re-run of this script on that file, not a memory of what the dashboard said.
