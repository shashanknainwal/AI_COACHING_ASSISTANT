---
title: "Exercise: Debug an Incident from Logs Alone"
type: exercise
minutes: 40
hints:
  - "`parse_lines`: wrap `json.loads(line)` in `try/except json.JSONDecodeError`; also skip results that aren't dicts or lack `\"ts\"` or `\"event\"`. Sort with `records.sort(key=lambda r: r[\"ts\"])` (ISO timestamps sort correctly as strings)."
  - "`request_timeline`: the time is `r[\"ts\"][11:19]`; add `f\" {error_type} (attempt {attempt})\"`, `f\" {latency_ms}ms\"` or `f\" {status}\"` depending on the event."
  - "`by_version`: group `llm_call` and `llm_error` records by `r[\"version\"]`. Rates and averages use only the `llm_call` records."
  - "`incident_summary`: the bad version has the most errors. Find its deploy in the time-ordered deploy events; the good version is the deploy just before it, and the rollback is the next deploy with a different version."
  - "`extra_cost_usd = (bad avg cost - good avg cost) × bad calls`, rounded to 4 decimals. `failed_requests` counts `http_request` events with `status >= 500`."
---

Tuesday, 14:52. Brightway's support lead posts in the shared channel: *"Ticket triage was really slow for the last hour and some tickets failed. Also, finance says the API bill jumped. What happened?"* The service was rolled back at 14:45 and looks healthy now. Opinions are already flying: "Anthropic had an outage," "it was a traffic spike."

You have the raw logs from 13:30 to 15:15 (`incident.LOG_LINES`, 672 lines, some of them not valid JSON). Find out what really happened, with evidence.

## Your task

**1. `parse_lines(lines)`** returns `(records, skipped)`: records are the lines that parse as JSON **objects** with `"ts"` and `"event"` keys, sorted by `ts`. `skipped` counts every other line.

**2. `request_timeline(records, request_id)`** returns one line per event of that request, in time order:

```
14:25:24 llm_error RateLimitError (attempt 1)
14:25:26 llm_error RateLimitError (attempt 2)
14:25:27 http_request 503
```

The time is characters 11-19 of `ts`. `llm_call` lines end with `"<latency_ms>ms"` (for example `13:30:04 llm_call 1441ms`). Other events show only the time and event name.

**3. `by_version(records)`** uses `llm_call` and `llm_error` events and returns, per `version`:

```python
{"calls": 180, "errors": 0, "cache_hit_rate": 0.933, "cache_write_rate": 0.067,
 "avg_cost_usd": 0.00266, "avg_latency_ms": 974}
```

`calls` counts `llm_call` events and `errors` counts `llm_error` events. The other values come from `llm_call` events: the share with `cache_read_tokens > 0`, the share with `cache_write_tokens > 0`, mean cost (6 decimals) and mean latency (whole ms).

**4. `incident_summary(records)`** returns:

```python
{"bad_version": "v1.8.0", "deployed_at": "14:00:00", "rolled_back_at": "14:45:00",
 "first_error_at": "14:20:24", "failed_requests": 16, "extra_cost_usd": 0.7664}
```

- `bad_version`: the version with the most errors.
- `deployed_at`: when it was deployed.
- `rolled_back_at`: the next deploy with a different version.
- `first_error_at`: the time of the first `llm_error`.
- `failed_requests`: `http_request` events with `status >= 500`.
- `extra_cost_usd`: (bad version's average cost − the previous version's) × the bad version's calls.

**5. `ROOT_CAUSE`**: set it to the key in `CAUSES` that the evidence supports.

Press **Run**, read the deploy notes and the per-version table, decide, then **Submit**.
