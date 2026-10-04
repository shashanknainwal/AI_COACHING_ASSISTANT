---
title: "Exercise: Build an Incremental Sync Job"
type: exercise
minutes: 35
hints:
  - "`map_record`: check required fields first: `for field in REQUIRED: if src.get(field) in (None, \"\"): raise ValueError(f\"missing {field}\")`. Then look up the status, raising `ValueError(f\"unknown status {code}\")` if it's not in `STATUS_MAP`."
  - "Nested fields: `src.get(\"consignee\") or {}` gives you a dict even when it's missing; then `.get(\"name\")`."
  - "`overlap_since`: `datetime.strptime(watermark, ISO) - timedelta(minutes=OVERLAP_MINUTES)`, then `.strftime(ISO)`."
  - "`fetch_changes` is the pagination loop from exercise 2, with `updated_since` added to the params."
  - "In `sync`, compute the new watermark as `max([watermark] + [r[\"updated_at\"] for r in changes])`. Same-format ISO strings compare correctly."
  - "For each record: map inside `try/except ValueError`; on error append `(record.get(\"id\"), str(e))` to errors and count it as skipped."
---

Time to connect Northwind to the retailer's ERP for real. Every 10 minutes a job will pull changed shipments from Northwind, translate them into the ERP's schema, and upsert them. It has to be idempotent, survive bad records, and never miss a change.

## The source API

```http
GET /v1/shipments?updated_since=2026-03-10T08:15:00Z&limit=50&cursor=...
```

returns `{"data": [...], "next_cursor": ...}` like exercise 2. A source record:

```python
{"id": "SHP-1003", "status_code": "DL", "weight_lbs": 750, "charge_cents": 41250,
 "consignee": {"name": "Brightway Retail", "city": "Dallas"}, "updated_at": "2026-03-10T08:15:00Z"}
```

## The target record (ERP)

```python
{"external_id": "SHP-1003", "status": "delivered", "weight_kg": 340.2, "charge": 412.5,
 "customer_name": "Brightway Retail", "city": "Dallas", "source_updated_at": "2026-03-10T08:15:00Z"}
```

## Your task

**1. `map_record(src)`** returns the target record:
- Raise `ValueError("missing <field>")` for the first field in `REQUIRED` that's absent, `None`, or `""`.
- `status` comes from `STATUS_MAP`; an unknown code raises `ValueError("unknown status <code>")`.
- `weight_kg = round(weight_lbs * LBS_TO_KG, 1)`; `charge = round(charge_cents / 100, 2)`.
- `customer_name` and `city` come from the nested `consignee` dict (use `None` if missing).

**2. `overlap_since(watermark)`** returns the watermark minus `OVERLAP_MINUTES`, in the same `ISO` format.

**3. `fetch_changes(session, watermark)`** fetches **all pages** of `GET {BASE}/v1/shipments` with params `updated_since=overlap_since(watermark)` and `limit=PAGE_SIZE` (plus `cursor` after the first page), `timeout=TIMEOUT`, and `raise_for_status()`. Returns all records.

**4. `sync(session, target, watermark)`** runs one sync and returns a summary:

```python
{"created": 3, "updated": 2, "unchanged": 6, "skipped": 1,
 "errors": [("SHP-1011", "unknown status ZZ")], "watermark": "2026-03-10T08:28:41Z"}
```

- `target` is a dict of `external_id → record`; upsert into it in place.
- **created**: new id. **updated**: existing id with a different record. **unchanged**: identical record.
- **skipped**: records whose mapping raised `ValueError`; add `(id, message)` to `errors`.
- **watermark**: the latest `updated_at` among the fetched records, or the old watermark if nothing was fetched or everything was older. It never moves backward.

Press **Run** to watch a first full sync, a no-op re-run, and an incremental run after new changes. Then **Submit**.
