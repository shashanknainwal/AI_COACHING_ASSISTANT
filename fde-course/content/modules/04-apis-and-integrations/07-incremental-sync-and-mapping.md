---
title: "Incremental Sync Jobs and Schema Mapping"
type: reading
minutes: 17
---

> **By the end of this lesson you will be able to:**
> - Choose between full and incremental sync, and implement a watermark safely
> - Make a sync job idempotent so re-running it never creates duplicates
> - Map records between two schemas with explicit, testable rules
> - Handle bad records without stopping the whole job

## The job behind most integrations

Webhooks are fast but can be missed. The workhorse of most integrations is a **sync job**: a scheduled process that pulls changes from a source system and writes them to a target. For Northwind, every 10 minutes: "get shipments that changed, translate them into the ERP's format, and upsert them."

## Full vs. incremental

| | Full sync | Incremental sync |
|---|---|---|
| What it fetches | Everything, every time | Only records changed since last run |
| Simple? | Very | Needs a watermark |
| Cost | Grows with total data | Grows with changes |
| Catches deletes? | Yes (missing = deleted) | Only if the source exposes deletes |

Start with a full sync when data is small. Switch to incremental once a full sync takes too long or hits rate limits. Many teams run incremental syncs all day and a full **reconciliation** sync weekly, to catch anything incremental missed.

## Watermarks

An incremental sync remembers how far it got: the **watermark** (also called a high-water mark or cursor). Usually it's the latest `updated_at` value seen:

```
run 1: fetch updated_since=1970-01-01 → newest updated_at seen: 2026-03-10T08:25Z → save watermark
run 2: fetch updated_since=2026-03-10T08:25Z → ...
```

Rules that prevent missed records:

1. **Advance the watermark from the data, not the clock.** Use the maximum `updated_at` you actually received, not "the time the job ran." Clocks on different servers disagree, and records written during your job could fall into a gap.
2. **Save the watermark only after the batch is written successfully.** If the job crashes halfway, the next run re-fetches from the old watermark instead of skipping records.
3. **Fetch with an overlap.** Ask for `updated_since = watermark − 5 minutes`. Records updated in the same second as the watermark, or committed late by the source, get picked up. The cost is re-fetching a few records, which is harmless if your writes are idempotent.
4. **Never let the watermark move backward.** If a run returns nothing, keep the old one.

## Idempotent writes: upsert

Because of overlaps and retries, the same record will arrive more than once. Your write must be an **upsert**: insert if new, update if it exists, keyed by the source system's ID.

```
key = record["external_id"]
if key not in target:          → created
elif target[key] != record:    → updated
else:                          → unchanged (count it, but no write needed)
```

Run the same sync twice and the second run should report zero created and zero updated. That property, **idempotency**, is what lets you safely re-run a failed job at 2 a.m. without thinking.

## Schema mapping

The source and target never agree on field names, types, or vocabularies:

| Northwind (source) | ERP (target) | Transformation |
|---|---|---|
| `id` | `external_id` | rename |
| `status_code`: `PU`, `IT`, `DL`, `EX` | `status`: `picked_up`, `in_transit`, `delivered`, `exception` | lookup table |
| `weight_lbs` | `weight_kg` | × 0.45359237, round to 1 decimal |
| `charge_cents` (integer) | `charge` (dollars) | ÷ 100, round to 2 decimals |
| `consignee.name` | `customer_name` | flatten a nested field |
| `consignee.city` | `city` | flatten |
| `updated_at` | `source_updated_at` | rename |

Good mapping code:

- **Is explicit.** One function or table per field; no clever magic. When the customer asks "why is this weight 340.2?", you can point at the line.
- **Fails loudly on the unknown.** A status code that isn't in your lookup table (`ZZ`) should raise an error for that record, not silently map to `None` or a default. Unknown codes usually mean the source added a new value, and someone needs to decide how to map it.
- **Keeps units in names** (`weight_kg`, `charge_cents`). It prevents the classic pounds-vs-kilograms bug.
- **Is tested** with a few real records, including the weird ones.

## Bad records shouldn't stop the job

One malformed record out of 10,000 shouldn't block the other 9,999. Process records individually, catch mapping errors, **skip and record** the bad ones, and keep going:

```python
for record in changes:
    try:
        mapped = map_record(record)
    except ValueError as e:
        errors.append((record.get("id"), str(e)))
        continue
    upsert(mapped)
```

Then report the errors (count plus examples) in the job's summary and alert if the error *rate* is high. A sudden jump from 0.1% to 30% errors means something changed upstream.

## What a good sync job reports

```
sync northwind→erp  2026-03-10T08:30Z
  fetched 12 (updated_since 2026-03-10T08:20Z, 5 min overlap)
  created 3, updated 2, unchanged 6, skipped 1
  errors: SHP-1011 unknown status ZZ
  watermark 2026-03-10T08:28:41Z → saved
```

These numbers are what you'll look at when someone says "the ERP is missing a shipment." In the next exercise you'll build a sync job that produces exactly this summary.

## A note on deletes

Incremental syncs only see records that still exist. If the source hard-deletes records, you need either a "deleted records" endpoint, **tombstones** (records marked `deleted: true` instead of removed), or the periodic full reconciliation. Ask about deletes during discovery; it's one of the most commonly forgotten requirements.

> **Key takeaways**
> - Incremental sync uses a watermark: advance it from the data, save it after success, fetch with an overlap, never move it backward.
> - Upserts make syncs idempotent: re-running produces no duplicates and no spurious updates.
> - Mapping should be explicit, keep units in names, and fail loudly on unknown values.
> - Skip and report bad records instead of stopping the job; watch the error rate.
