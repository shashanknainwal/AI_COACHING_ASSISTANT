---
title: "Exercise: Two Carrier Connectors Become One Configurable Connector"
type: exercise
minutes: 40
hints:
  - "`get_path`: start with `value = record`, then for each key in `path.split(\".\")` stop with `None` if `value` isn't a dict or `value.get(key) is None`."
  - "`apply_transform`: `name = spec.get(\"transform\", \"none\")`, then one `if` per transform. `dmy_to_iso` is `datetime.strptime(value, \"%d/%m/%Y %H:%M\").strftime(\"%Y-%m-%dT%H:%M:%SZ\")`."
  - "`validate_config`: pagination first, then loop over `config[\"fields\"].items()` in order (unknown target, then the transform checks), then the missing required fields in `TARGET_FIELDS` order."
  - "`map_record`: loop over `TARGET_FIELDS`, not over the config, so every target key exists. A field the config doesn't mention, or whose value is `None`, is `None`, or raises `ValueError(f\"missing {name}\")` if required."
  - "`fetch_all` cursor style: start with `params = {}` and stop when `next_field` is empty. Page style: start at 1 and stop when `has_more_field` is false. `POLAR_CONFIG` uses `wt_kg` with no transform, `amt_usd` with `to_float` and `last_event_ts` with `dmy_to_iso`."
---

Back in Module 4 you built a Northwind sync by hand, then mapped Polar Express with Claude's help. Since then the FDE team has written that kind of connector at three more customers, each a copy with small edits, each with its own bugs. Your engagement lead's request, after reading your field report: "Make it one connector. Adding a carrier should be a config file and a review, not a code change."

This is the other half of writing assets back to product. The field report argued for reusable code; this exercise produces some. Once one connector reads a config, you can package it as a library, a Skill or an MCP server (Module C7 covers both), and the next FDE starts from it instead of from a copy.

## The design

A carrier is described entirely by a config:

```python
NORTHWIND_CONFIG = {
    "name": "northwind",
    "pagination": {"type": "cursor", "param": "cursor", "items_field": "data", "next_field": "next_cursor"},
    "fields": {
        "external_id": {"path": "id"},
        "status": {"path": "status_code", "transform": "lookup", "table": {"PU": "picked_up", ...}},
        "weight_kg": {"path": "weight_lbs", "transform": "lbs_to_kg"},
        "customer_name": {"path": "consignee.name"},
        ...
    },
}
```

`fields` maps each target field (from `TARGET_FIELDS`) to a dotted `path` in the source record and an optional `transform`. Transforms come from a fixed list (`TRANSFORMS`). A config can choose them but never add code. That's what makes a config safe to review.

`setup.py` simulates both APIs as functions that take a params dict and return one page: `northwind_fetch` (cursor pages) and `polar_fetch` (`?page=N`, returning `{"shipments": [...], "has_more": bool}`).

## Your task

**1. `get_path(record, path)`** follows a dotted path like `"consignee.name"`. It returns `None` if any step is missing, `None`, or not a dict. A real falsy value such as `0` is returned as is.

**2. `apply_transform(value, spec)`** applies `spec["transform"]` (default `"none"`):

| Transform | Result |
|---|---|
| `none` | the value unchanged |
| `lookup` | `spec["table"][value]`, or `ValueError("unknown value <value>")` |
| `lbs_to_kg` | `round(value * LBS_TO_KG, 1)` |
| `cents_to_dollars` | `round(value / 100, 2)` |
| `to_float` | `round(float(value), 2)` |
| `dmy_to_iso` | `"10/03/2026 08:15"` becomes `"2026-03-10T08:15:00Z"` (day first; treated as UTC) |
| anything else | `ValueError("unknown transform <name>")` |

**3. `validate_config(config)`** returns a list of problems, in this order:
- `"unknown pagination type: <type>"` if it isn't `cursor` or `page`;
- then for each entry in `fields`, in order: `"unknown target field: <name>"`; `"<name>: unknown transform <t>"`; or `"<name>: lookup needs a table"`;
- then `"missing required field: <name>"` for each required target field the config doesn't map, in `TARGET_FIELDS` order.

**4. `map_record(src, config)`** returns a dict with **every** target field. A field the config doesn't map, or whose source value is `None`, is `None`; if that field is required, raise `ValueError("missing <name>")` instead. Transforms only run on values that aren't `None`.

**5. `fetch_all(fetch_page, config)`** returns every item across pages:
- **cursor**: first call with `{}`, then `{param: <next cursor>}` until `next_field` is empty;
- **page**: call with `{param: 1}`, `{param: 2}`, ... until `has_more_field` is false.

Items are under `items_field`.

**6. `run_connector(fetch_page, config)`** validates first (raise `ValueError` listing the problems, before any fetch), then fetches and maps everything. It returns `{"records": [...], "errors": [(source id, message), ...]}`, where the source id comes from the config's `external_id` path.

**7. `POLAR_CONFIG`.** Describe Polar Express in config. Its records look like this:

```python
{"trk_no": "PX-88213", "state": "OUT_FOR_DELIVERY", "wt_kg": 12.5, "amt_usd": "48.20",
 "recipient": "Brightway Retail", "dest_city": "Austin", "last_event_ts": "10/03/2026 08:15"}
```

Use pagination `{"type": "page", "param": "page", "items_field": "shipments", "has_more_field": "has_more"}`. Map `PICKED_UP` to `picked_up`, both `IN_TRANSIT` and `OUT_FOR_DELIVERY` to `in_transit`, `DELIVERED` to `delivered` and `EXCEPTION` to `exception`. Weight is already in kilograms, the charge is a string of dollars, and the timestamp is day-first.

Press **Run** to sync both carriers through the same code.

## What you just bought

Polar Express sent `HELD_AT_CUSTOMS`, a status nobody had seen. With one connector, that's a one-line config change, reviewed once, and every customer on Polar Express gets it. With five forks, it's five fixes, and the one somebody forgets becomes next month's incident. Two open questions to take back to the team: whether the day-first timestamps are really UTC (ask Polar Express, don't assume), and who owns the shared config repository.

> **FDE tip:** Generalize after the second or third copy, not the first. One customer is a project; two is a coincidence; three is a product.
