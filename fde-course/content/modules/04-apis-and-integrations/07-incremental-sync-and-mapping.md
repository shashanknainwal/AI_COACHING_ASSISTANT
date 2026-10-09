---
title: "Incremental Sync Jobs and Schema Mapping"
type: reading
minutes: 3
---

> **By the end of this lesson you will be able to:**
> - Implement a watermark for incremental sync safely
> - Make a sync idempotent so re-running never creates duplicates
> - Map records between schemas with explicit rules, and skip bad records without stopping

Webhooks can be missed, so Leah's integration also needs a sync job: every 10 minutes, get Northwind shipments that changed, translate them into the ERP's format, and upsert them. When an ERP user says "a shipment is missing", this job's numbers are what you check first.

## Full vs. incremental

| | Full sync | Incremental sync |
|---|---|---|
| Fetches | Everything | Changes since last run |
| Cost | Grows with total data | Grows with changes |
| Catches deletes? | Yes (missing = deleted) | Only if the source exposes them |

Start full while data is small. Many teams run incremental all day plus a weekly full **reconciliation**.

## Watermarks

The **watermark** is how far the job got, usually the latest `updated_at` seen:

```
run 1: fetch updated_since=1970-01-01 → newest updated_at seen: 2026-03-10T08:25Z → save watermark
run 2: fetch updated_since=2026-03-10T08:25Z → ...
```

1. **Advance it from the data, not the clock.** Use the max `updated_at` received. Server clocks disagree, and records committed during the job can fall into a gap.
2. **Save it only after the batch is written.** A crash re-fetches instead of skipping.
3. **Fetch with an overlap**: `updated_since = watermark − 5 minutes` catches same-second and late-committed records. Harmless if writes are idempotent.
4. **Never move it backward.** An empty run keeps the old one.

## Idempotent writes: upsert

```
key = record["external_id"]
if key not in target:          → created
elif target[key] != record:    → updated
else:                          → unchanged
```

Run the same sync twice: the second run reports zero created, zero updated. That's what lets you re-run a failed job at 2 a.m. without thinking.

## Schema mapping

| Northwind (source) | ERP (target) | Transformation |
|---|---|---|
| `id` | `external_id` | rename |
| `status_code`: `PU`, `IT`, `DL`, `EX` | `status`: `picked_up`, `in_transit`, `delivered`, `exception` | lookup table |
| `weight_lbs` | `weight_kg` | × 0.45359237, round to 1 decimal |
| `charge_cents` (integer) | `charge` (dollars) | ÷ 100, round to 2 decimals |
| `consignee.name` | `customer_name` | flatten |
| `consignee.city` | `city` | flatten |
| `updated_at` | `source_updated_at` | rename |

- **Explicit**: one rule per field, so you can point at the line that made a weight 340.2.
- **Fail loudly on the unknown**: status `ZZ` raises for that record. It usually means the source added a value someone must map.
- **Units in names** (`weight_kg`, `charge_cents`) prevent pounds-vs-kilograms bugs.
- **Tested** on real records, including weird ones.

## Bad records don't stop the job

```python
for record in changes:
    try:
        mapped = map_record(record)
    except ValueError as e:
        errors.append((record.get("id"), str(e)))
        continue
    upsert(mapped)
```

Report errors with examples and alert on the error *rate*: a jump from 0.1% to 30% means something changed upstream.

## What a good sync reports

```
sync northwind→erp  2026-03-10T08:30Z
  fetched 12 (updated_since 2026-03-10T08:20Z, 5 min overlap)
  created 3, updated 2, unchanged 6, skipped 1
  errors: SHP-1011 unknown status ZZ
  watermark 2026-03-10T08:28:41Z → saved
```

**Deletes:** incremental syncs only see records that exist. If the source hard-deletes, you need a deleted-records endpoint, **tombstones** (`deleted: true`), or the full reconciliation. Ask during discovery.

> **Key takeaways**
> - Watermark from the data, saved after success, with an overlap, never backward.
> - Upserts make syncs idempotent.
> - Mapping is explicit, keeps units in names, fails loudly on unknown values.
> - Skip and report bad records; watch the error rate.
