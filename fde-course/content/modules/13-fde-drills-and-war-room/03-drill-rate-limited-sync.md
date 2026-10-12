---
title: "Drill: Rate-Limited Sync with Watermarks"
type: drill
minutes: 70
timeLimit: 70
levels:
  - "Incremental sync"
  - "Pages and rate limits"
  - "Backfill"
  - "Deletes and rewind"
hints:
  - "Make the sync key a tuple (updated_at, record_id) from Level 1. The watermark, the backfill cursor and its upper bound are all keys, and Python compares tuples the way the spec needs."
  - "Write one helper that makes a single API request: it checks the budget, records the request time, and returns the next page of keys after a cursor (with optional upper bound and since filter). Both the incremental sync and the backfill call it."
  - "Count a request as allowed when fewer than per_minute earlier requests have a time greater than timestamp - 60. Record the time even when the page comes back empty."
  - "Advance the watermark (or the backfill cursor) after each record you copy, not after the whole sync. A sync that runs out of budget halfway must keep its progress."
  - "A tombstone is just a source record with a deleted flag. Pull it like any other record; copying it means removing the destination entry."
---

Marram Commerce mirrors its biggest client's product catalogue into its own search index. The client's API is slow and strict: pages of a few records, a fixed number of requests per minute, and clocks that sometimes disagree. Petra Havel (fictional) puts it plainly: "Our nightly sync silently drops records. Nobody notices for a week."

This drill is about the bugs that hide in every incremental sync: ties on the watermark, partial progress, rate limits, late writes and deletes. It's an original problem in the progressive format (**Reported**; see module C3).

## The rules

- Implement a class called `SyncEngine`. Every method takes `timestamp` (an integer) as its first argument, and timestamps never decrease from one call to the next.
- The class plays two parts. `upsert` and `delete` write to the **source** (the client's API). `sync` copies from the source into the **destination** (your store), and `get` reads the destination.
- Press **Submit** to run the checks for the levels you can see. Hidden checks combine features from several levels.
- Hints and the tutor are off while the clock runs.

## Level 1: Incremental sync

A record's **key** is the pair `(updated_at, record_id)`. Keys sort by `updated_at`, then by `record_id`.

- `upsert(timestamp, record_id, updated_at, data)`: write a record to the source. If it exists, replace its `updated_at` and `data`. Return `True`. `updated_at` is an integer supplied by the caller and has nothing to do with `timestamp`.
- `sync(timestamp)`: pull every source record whose key is after the watermark, in key order. Copy each into the destination and move the watermark to its key. Return the number of records pulled.
- `get(timestamp, record_id)`: the record's data in the destination, or `None`.
- `watermark(timestamp)`: the watermark as a tuple. It starts at `(0, "")`.
- `count(timestamp)`: the number of records in the destination.

```python
s = SyncEngine()
s.upsert(1, "b", 100, "B")
s.sync(2)                 # 1, watermark (100, "b")
s.upsert(3, "c", 100, "C")
s.sync(4)                 # 1: (100, "c") is after (100, "b")
```

## Level 2: Pages and rate limits

- `set_limits(timestamp, page_size, per_minute)`: return `True`, or `False` if either value isn't a positive integer (keep the old limits).
- With limits set, `sync` makes **requests**. Each request returns up to `page_size` records after the watermark, in key order. Copy them and move the watermark after each record. Keep making requests while the previous page was full. A request that returns no records still counts.
- A request is allowed only if fewer than `per_minute` requests were made in the 60 seconds before it: count earlier requests whose time is greater than `timestamp - 60`. When a request isn't allowed, `sync` stops and returns what it pulled so far. Progress is kept.
- Before `set_limits` is called there are no limits: each `sync` makes exactly one request, which returns everything.
- `requests_made(timestamp)`: the total number of requests made so far.
- `lag(timestamp)`: the number of source records whose key is after the watermark.

## Level 3: Backfill

A record written with an old `updated_at` (a skewed clock, a bulk import) lands before the watermark. Incremental sync never sees it.

- `backfill(timestamp, since)`: start a backfill. It covers source records with `updated_at >= since` whose key is not after the watermark **at the moment the backfill starts**. Return `True`, or `False` if a backfill is already running. The backfill does no work in this call.
- Each `sync` call works on a running backfill first: it makes requests (same page size, same budget) over the backfill's range in key order, with its own cursor. When a backfill page isn't full, the backfill is finished, and the same `sync` call goes on with the incremental sync if budget remains.
- A backfill copies the current source data. It never moves the main watermark.
- `backfill_status(timestamp)`: `"running"` or `"idle"`.
- `sync` returns the records pulled by the backfill and the incremental sync together.

## Level 4: Deletes and rewind

- `delete(timestamp, record_id, updated_at)`: turn the source record into a **tombstone** with this `updated_at`. Return `True`, or `False` if the record doesn't exist or is already a tombstone. An `upsert` to a tombstone brings the record back.
- Tombstones are pulled like records, by the incremental sync and by backfills, and they move the watermark and cursors in the same way. Pulling a tombstone removes the record from the destination.
- `rewind(timestamp, updated_at)`: set the watermark to `(updated_at, "")` so the next syncs pull everything after it again. Return `True`, or `False` if that isn't before the current watermark. A running backfill keeps its own range and cursor.
