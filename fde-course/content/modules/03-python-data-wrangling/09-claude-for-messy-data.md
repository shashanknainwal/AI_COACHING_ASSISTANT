---
title: "Using Claude on Messy Data (and When Not To)"
type: reading
minutes: 6
---

> **By the end of this lesson you will be able to:**
> - Decide which data problems need Claude and which need ten lines of code
> - Batch records into one request safely and validate what comes back
> - Estimate the cost of an LLM data job before you run it

Cobalt has 50,000 uncategorized support tickets and Owen wants to know where complaints come from. As CFO, he'll ask what it costs before you spend a dollar.

## If you can write the rule, write the rule

| Use deterministic code | Use Claude |
|---|---|
| Parsing dates, money, phones; joins; totals | Categorizing free-text tickets and notes |
| Exact deduplication | Judging ambiguous duplicate pairs |
| Anything that must be 100% reproducible | Extraction and long-tail normalization ("STL") |

Code is free, instant, consistent and auditable.

## Rules first, Claude second

"Resend **invoice** 4471" is obviously billing; "the valve hisses under pressure" needs reading.

```
tickets ──► keyword rules ──► labeled (free, instant)
               │
               └─► unmatched ──► Claude in batches ──► validate ──► labeled
```

Simple rules often handle 30–60% of records. Keep them conservative: "refund" → billing is safe; "broken" → product defect is not ("my login is broken").

## Batch with stable indexes

1. Give each record a stable **index**.
2. Put several records in one prompt, one per numbered line.
3. Ask for structured output that echoes the index.
4. Match answers back **by index**, never by position.

```text
Categorize each ticket into one category.

3. The valve we got last week hisses under pressure
7. Can someone call me about our contract renewal?
8. Box arrived soaked, two gauges cracked
```

```json
{"results": [
  {"index": 3, "category": "product defect"},
  {"index": 7, "category": "other"},
  {"index": 8, "category": "product defect"}
]}
```

Models occasionally skip or reorder items; zip by position and one skip silently shifts every later label. Batches of 10–50 short records are a common sweet spot.

## Validate what comes back

Structured outputs guarantee the JSON *shape*; your code checks the *content*:
- Every index you sent comes back; missing ones get a fallback (`"other"`) and a log line.
- Ignore indexes you didn't send.
- Categories must be in your list (an `enum` in the schema helps).
- Check `stop_reason`. A truncated or refused batch falls back and retries later; it never crashes the job.

## Estimate cost first

```
calls          = ceil(records / batch_size)
input tokens   = calls × overhead_per_call + records × tokens_per_record
output tokens  = records × output_tokens_per_record
cost           = input × input_price + output × output_price
```

50,000 tickets on Claude Opus 5.5 ($4 / $20 per million input / output tokens), 60 tokens per ticket, 400 tokens of instructions per call, 15 output tokens per ticket:

| Batch size | Calls | Input tokens | Output tokens | Cost |
|---|---|---|---|---|
| 1 | 50,000 | 23,000,000 | 750,000 | $107.00 |
| 25 | 2,000 | 3,800,000 | 750,000 | $30.20 |

Batching cuts about 70%; rules-first cuts more. For backfills, the **Message Batches API** runs asynchronously (results within 24 hours) at 50% of the normal price, and **prompt caching** makes a long repeated system prompt much cheaper after the first call.

## Evaluate on a sample before the full run

Run 100 hand-labeled tickets first. 94% agreement on genuinely ambiguous misses: go. 70%: fix the categories or prompt first.

> **Key takeaways**
> - Write the rule when you can; use Claude for language judgment.
> - Conservative rules first; Claude for the remainder, in batches matched by index.
> - Validate every batch and fall back safely.
> - Estimate cost before running; batching, the Batches API and caching reduce it.
