---
title: "Exercise: Metrics and Alerts from Logs"
type: exercise
minutes: 30
hints:
  - "`percentile`: `ordered = sorted(values)`, `rank = max(1, math.ceil(p / 100 * len(ordered)))`, return `ordered[rank - 1]`."
  - "`window_metrics`: filter with `start <= r[\"ts\"] < end`, then split into `llm_call` and `llm_error` records. Latency and cache metrics use calls only."
  - "Guard every division: return `None` for a rate when its denominator is 0. `cost_usd` is `round(sum(...), 4)`, which is 0 for no calls."
  - "`evaluate_alerts`: skip a rule when the metric is `None` or `metrics.get(\"requests\", 0) < rule.get(\"min_requests\", 0)`. Compare with `>` or `<` from `rule[\"op\"]`."
  - "`scan`: `for window_start in range(start, end, window_s)`, compute the window's metrics and alerts, and keep windows with at least one alert."
---

Your structured logs from the last exercise are flowing. Now turn them into the numbers an on-call engineer watches, and into **alerts** that wake someone up only when something is really wrong.

`RECORDS` holds two hours of parsed log records from the triage service (`llm_call` and `llm_error` events, a request every 30 seconds). `START` is the first timestamp, and `ALERT_RULES` are given.

## Your task

**1. `percentile(values, p)`** uses the **nearest-rank** method: sort the values and return the one at rank `ceil(p/100 × n)` (rank 1 is the smallest; use rank 1 for p = 0). Return `None` for an empty list.

**2. `window_metrics(records, start, end)`** uses records with `start <= ts < end` and returns:

```python
{"requests": 30,         # llm_call + llm_error
 "errors": 5,            # llm_error
 "error_rate": 0.167,    # errors / requests, 3 decimals (None if no requests)
 "p50_ms": 1194,         # percentiles of llm_call latency_ms (None if no calls)
 "p95_ms": 4671,
 "cache_hit_rate": 0.92, # share of llm_call with cache_read_tokens > 0, 3 decimals (None if no calls)
 "cost_usd": 0.0786}     # sum of llm_call cost_usd, 4 decimals
```

**3. `evaluate_alerts(metrics, rules)`** returns one string per firing rule, in rule order:

```
[page] High error rate: error_rate is 0.167 (threshold > 0.05)
```

A rule fires when `metric > threshold` (op `">"`) or `metric < threshold` (op `"<"`). Skip a rule if its metric is `None`, or if the rule has `min_requests` and the window has fewer requests (a 1-in-3 error rate at 3 a.m. isn't an incident).

**4. `scan(records, start, end, window_s, rules)`** splits `[start, end)` into windows of `window_s` seconds and returns `[{"window_start": ..., "alerts": [...]}]` for windows where at least one alert fires.

Press **Run**. Compare p50 and p95 before and after minute 75: what would a dashboard showing only the median have missed? Then **Submit**.
