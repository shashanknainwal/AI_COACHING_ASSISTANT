---
title: "Using Claude on Messy Data (and When Not To)"
type: reading
minutes: 16
---

> **By the end of this lesson you will be able to:**
> - Decide which data problems need an LLM and which need ten lines of deterministic code
> - Use the "rules first, Claude second" pattern to cut cost and improve reliability
> - Batch many records into one request safely, and validate what comes back
> - Estimate the cost of an LLM data job before you run it

## The temptation

Once you've seen Claude clean up messy text, it's tempting to send it everything: dates, phone numbers, joins, totals. Resist. LLMs are the right tool for some data problems and the wrong tool for others.

| Use deterministic code | Use Claude |
|---|---|
| Parsing dates, money, phones (known formats) | Categorizing free-text tickets, notes, descriptions |
| Joining and reconciling on keys | Extracting fields from unstructured documents |
| Arithmetic, totals, statistics | Normalizing a long tail of messy values ("St. Louis Mo.", "STL") |
| Exact deduplication | Judging ambiguous duplicate pairs |
| Anything that must be 100% reproducible | Anything that needs reading comprehension |

The rule of thumb: **if you can write the rule, write the rule.** Code is free to run, instant, perfectly consistent, and easy to explain to an auditor. Use Claude for the parts that need judgment about language.

## Rules first, Claude second

Most real datasets have an easy majority and a hard tail. Cobalt's support tickets are a good example:

- "Please resend **invoice** 4471" → obviously *billing*
- "Where's my **tracking** number?" → obviously *shipping*
- "The valve we got last week hisses under pressure and the seal looks off" → needs reading

A keyword rule can label the first two instantly and for free. Only the third needs Claude. In practice, simple rules often handle 30-60% of records, so the LLM job shrinks proportionally, and the rule-labeled records are perfectly consistent.

```
tickets ──► keyword rules ──► labeled (free, instant)
               │
               └─► unmatched ──► Claude in batches ──► validate ──► labeled
```

Keep the rules conservative: a rule should only fire when it's almost never wrong. "refund" → billing is safe. "broken" → product defect is not ("my login is broken").

## Batching: many records per request

Sending one ticket per request repeats your system prompt and instructions every time. Sending ten tickets per request shares that overhead. The pattern:

1. Give each record a stable **index**.
2. Put several records in one prompt, each on its own numbered line.
3. Ask for structured output that echoes the index with each answer.
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

Why match by index? Because models occasionally skip an item, merge two, or reorder them. If you zip answers to inputs by position, one skipped item shifts every label after it, silently.

**Batch size trade-off:** bigger batches are cheaper per record, but a failure (a truncated response, a refusal) affects more records, and very long batches can reduce per-item attention. Batches of 10-50 short records are a common sweet spot. Measure on your data.

## Validate everything that comes back

Structured outputs guarantee the JSON *shape*. Your code still checks the *content*:

- **Every index you sent should come back.** Missing ones get a fallback label (`"other"`) and get logged.
- **Ignore indexes you didn't send.**
- **Categories must be in your list.** With an `enum` in the schema they will be, but check anyway if you ever relax the schema.
- **Check `stop_reason`.** If a batch is truncated or refused, fall back for that batch and retry it later. Don't let one bad batch crash a 50,000-record job.

## Estimating cost before you run

Always estimate before running an LLM job over customer data. The customer will ask, and a surprise bill is a terrible way to end a pilot.

For a batched job:

```
calls          = ceil(records / batch_size)
input tokens   = calls × overhead_per_call + records × tokens_per_record
output tokens  = records × output_tokens_per_record
cost           = input × input_price + output × output_price   (prices per token)
```

Example for 50,000 tickets on Claude Opus 5.5 ($4 per million input tokens, $20 per million output tokens), with 60 tokens per ticket, 400 tokens of instructions per call, and about 15 output tokens per ticket:

| Batch size | Calls | Input tokens | Output tokens | Cost |
|---|---|---|---|---|
| 1 | 50,000 | 23,000,000 | 750,000 | $107.00 |
| 25 | 2,000 | 3,800,000 | 750,000 | $30.20 |

Batching cuts the cost by about 70% here, and rules-first filtering cuts it further. Two more levers for big jobs:

- **The Message Batches API** processes requests asynchronously (results within 24 hours) at 50% of the normal price. Ideal for backfills that don't need instant answers.
- **Prompt caching** makes a long, repeated system prompt much cheaper on every call after the first.

## Evaluate before you trust

Before running a labeling job on all records, run it on a **labeled sample**: 100 tickets that you (or the customer) have categorized by hand. Compare. If Claude agrees with the humans 94% of the time, and the disagreements are genuinely ambiguous tickets, you're in good shape. If it's 70%, fix the category definitions or the prompt before spending money on the full run. Module 8 turns this into a proper evaluation harness.

> **Key takeaways**
> - If you can write the rule, write the rule; use Claude for language judgment.
> - Rules first, Claude second: conservative keyword rules handle the easy majority for free.
> - Batch records with stable indexes, match answers by index, and fall back safely on missing or failed items.
> - Estimate cost before running; batching, the Batches API, and prompt caching all reduce it.
