---
title: "Exercise: The 50,000-Ticket Backfill, Done for Real"
type: exercise
minutes: 40
hints:
  - "Pass 1: `for chunk in pd.read_csv(path, usecols=[\"ticket_id\", \"attempt\"], chunksize=chunksize):` then `chunk.groupby(\"ticket_id\")[\"attempt\"].max()` and merge into a dict, keeping the larger value."
  - "Pass 2: read with `dtype={\"category\": str}, keep_default_na=False` so an empty category stays `\"\"` instead of NaN. Keep the latest rows with `chunk[chunk[\"attempt\"] == chunk[\"ticket_id\"].map(latest)]`."
  - "Add helper columns with `chunk.assign(category=..., tickets=1, refusals=(chunk[\"stop_reason\"] == \"refusal\").astype(int))`, then `groupby([\"month\", \"category\"])[[...]].sum()` and append to a list."
  - "Combine the partial tables with `pd.concat(parts).groupby(level=[\"month\", \"category\"]).sum().sort_index()`. Sums of sums are still sums. Compute `cost_usd` once, after combining."
  - "In `report`, `table.groupby(level=\"month\")[\"tickets\"].sum()` gives tickets per month. For the earliest tie, take `s[s == s.max()].index.min()`."
---

Sana Iqbal again. The overnight backfill finished: 50,000 historical support tickets classified so our routing rules can be retrained. The job wrote one row per model call to `/data/backfill_results.csv`. Before I tell our COO it worked, I need three numbers I trust: tickets by month and category, the refusal rate, and what it cost, including what the retries cost us.

One complication. About 3% of tickets hit `max_tokens` on the first try. The job re-ran those at the end with a higher limit and appended the new rows to the bottom of the file. So a ticket can appear twice, far apart, and only its latest attempt counts.

## Why chunks, at only 50,000 rows

Honestly, this file fits in memory. The real one next quarter is every ticket since 2016, and the analytics VM you'll get has 4 GB of RAM. So you'll practise the pattern here, where you can check it: read the file in chunks, aggregate each chunk, and combine the partial results. Sums and counts combine across chunks. **Deduplication doesn't**: a ticket's two attempts can be in different chunks. That's why this takes two passes: the first finds each ticket's latest attempt, reading only two columns; the second aggregates.

This is the module's one pandas exercise. The first run loads pandas into the browser, which takes several seconds.

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

Use `pd.read_csv(..., chunksize=chunksize)` for every read (call it as `pd.read_csv`; the tests watch it).

**1. `latest_attempts(path, chunksize)`** returns a dict of `ticket_id` to its highest `attempt`. Read only the `ticket_id` and `attempt` columns (`usecols`).

**2. `aggregate(path, chunksize)`** returns a DataFrame:
- indexed by `["month", "category"]`, sorted;
- with the columns `COLUMNS`: `tickets`, `refusals` (rows whose `stop_reason` is `"refusal"`), `input_tokens`, `output_tokens` and `cost_usd`;
- counting **only each ticket's latest attempt**;
- with an empty category shown as `"(none)"`.

The result must not depend on the chunk size.

**3. `retry_overhead(path, chunksize)`** returns the dollars spent on attempts that a later attempt replaced.

**4. `report(table)`** returns:

```python
{"tickets": 50000, "refusal_rate": 0.0124, "cost_usd": 14.37,
 "busiest_month": "2025-11", "top_category": "billing"}
```

`refusal_rate` is rounded to 4 places and `cost_usd` to 2. `busiest_month` has the most tickets, and the earliest month wins a tie. `top_category` has the most tickets, ignoring `"(none)"`, and the first name alphabetically wins a tie.

Press **Run** to see the first rows of the table and the report.

## What you'd tell Sana

Lead with the numbers, then the caveats: "50,000 tickets classified for $14.37, plus $0.44 of re-runs. 1.24% were declined. Those are in the '(none)' rows, and I'm sampling them by hand to see whether they're legitimate fraud-related tickets the classifier tripped on (lesson 08 is about that). November 2025 was the busiest month." The refusal rate is small, but it isn't zero, and in a bank the declined tickets are the ones someone will ask about.

> **FDE tip:** Keep the raw per-call file. When someone questions a number in three weeks, the answer is a re-run of this script on that file, not a memory of what the dashboard said.
