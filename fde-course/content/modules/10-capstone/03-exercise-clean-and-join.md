---
title: "Exercise: Clean and Join NorthStar's Data"
type: exercise
minutes: 40
hints:
  - "`parse_date`: try each format in `DATE_FORMATS` with `datetime.strptime(raw.strip(), fmt)` inside `try/except ValueError`, and return `.strftime(\"%Y-%m-%d\")` for the first that works."
  - "`normalize_carrier`: `re.sub(r\"[^a-z0-9 ]\", \"\", raw.lower()).split()`, pop trailing words in `COMPANY_SUFFIXES`, join with no spaces, then `CARRIER_KEYS.get(key)`."
  - "`clean_shipments`: `csv.DictReader(io.StringIO(csv_text))` handles the quoted commas in city names. Check duplicates (by normalized ID) before anything else."
  - "`latest_events`: ISO timestamps compare correctly as strings, so keep an event when `e[\"ts\"] > latest[sid][\"ts\"]`."
  - "`build_queue`: skip codes not in `northstar.EXCEPTION_CODES`; an exception with no matching shipment is an orphan. Sort with `key=lambda q: (q[\"sla_hours\"], -q[\"value_usd\"])`."
---

NorthStar's team warned you the export was "a bit messy." It is: three date formats, ten spellings of three carriers, duplicate rows, blank weights, dollar signs in numbers, lowercase IDs with spaces, and carrier events for shipments that don't exist. Before any model work, you'll turn it into a trustworthy **exception queue**, plus a data-quality report you can show their team.

Data: `northstar.SHIPMENTS_CSV` (raw text), `northstar.CARRIER_EVENTS` (raw list) and `northstar.CUSTOMERS`. `DATE_FORMATS`, `CARRIER_KEYS` and `COMPANY_SUFFIXES` are given.

## Your task

**1. Small cleaners:**
- `parse_date(raw)`: try each of `DATE_FORMATS` (`2026-04-02`, `04/02/2026`, `Apr 2 2026`) and return `"YYYY-MM-DD"`, or `None` if none match.
- `normalize_id(raw)`: remove all whitespace and uppercase it (`" ns - 2001 "` → `"NS-2001"`).
- `normalize_carrier(raw)`: lowercase, remove everything except letters, digits and spaces, drop trailing company suffixes (`inc`, `llc`, `co`, `corp`), join the words with no spaces, and look the result up in `CARRIER_KEYS`. Unknown carriers return `None`.
- `parse_money(raw)`: `"$12,800.00"` → `12800.0`.

**2. `clean_shipments(csv_text)`** returns `(shipments, issues)`:
- `shipments` maps each normalized ID to a dict with `shipment_id`, `customer_id`, `carrier` (canonical), `origin`, `destination`, `ship_date`, `promised_date` (ISO), `weight_kg` (float or `None` if blank) and `value_usd` (float).
- A repeated ID is a duplicate: count it and skip it. A row with an unparseable date is excluded.
- `issues` is `{"rows": n, "duplicates": n, "bad_dates": [ids], "missing_weight": [ids], "unknown_carrier": [ids]}`. Rows with unknown carriers are still kept.

**3. `latest_events(events)`** returns `{normalized_id: {"code", "ts", "detail"}}` with each shipment's most recent event (the raw list isn't in time order).

**4. `build_queue(shipments, latest, customers)`** returns `(queue, orphans)`:
- One queue entry per shipment whose latest code is in `northstar.EXCEPTION_CODES`: `shipment_id`, `customer` (name), `tier`, `sla_hours`, `code`, `detail`, `carrier`, `value_usd` and `event_ts`.
- Sort by `sla_hours` (most urgent first), then by `value_usd`, highest first.
- `orphans`: sorted IDs of exception events with no matching shipment.

Press **Run** to see the data-quality report and the queue, then **Submit**. Your cleaned data should match `northstar.clean_data()` exactly; the later exercises use that clean version.
