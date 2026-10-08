import math


def make_records():
    """Two hours of parsed log records from the triage service (given, deterministic)."""
    seed, records = 7, []

    def rand():
        nonlocal seed
        seed = (seed * 1103515245 + 12345) % 2**31
        return seed / 2**31

    for i in range(240):                      # one request every 30 seconds
        ts = 1_773_000_000 + i * 30
        degraded = i >= 160                   # something changes 80 minutes in
        if (rand() < 0.12) if degraded else (i % 50 == 7):
            records.append({"ts": ts, "event": "llm_error", "error_type": "RateLimitError", "latency_ms": int(200 + rand() * 300)})
            continue
        latency = int(500 + rand() * 900 + (rand() * 6000 if degraded and rand() < 0.3 else 0))
        hit = rand() < (0.95 if not degraded else 0.9)
        records.append({"ts": ts, "event": "llm_call", "latency_ms": latency, "cache_read_tokens": 3000 if hit else 0,
                        "cost_usd": 0.0019 if hit else 0.0091})
    return records


RECORDS = make_records()
START = RECORDS[0]["ts"]
ALERT_RULES = [
    {"name": "High error rate", "metric": "error_rate", "op": ">", "threshold": 0.05, "severity": "page", "min_requests": 20},
    {"name": "Slow responses", "metric": "p95_ms", "op": ">", "threshold": 3000, "severity": "page"},
    {"name": "Cache hit rate low", "metric": "cache_hit_rate", "op": "<", "threshold": 0.8, "severity": "ticket"},
    {"name": "Cost spike", "metric": "cost_usd", "op": ">", "threshold": 0.15, "severity": "ticket"},
]


def percentile(values, p):
    if not values:
        return None
    ordered = sorted(values)
    rank = max(1, math.ceil(p / 100 * len(ordered)))
    return ordered[rank - 1]


def window_metrics(records, start, end):
    window = [r for r in records if start <= r["ts"] < end]
    calls = [r for r in window if r["event"] == "llm_call"]
    errors = [r for r in window if r["event"] == "llm_error"]
    requests = len(calls) + len(errors)
    latencies = [r["latency_ms"] for r in calls]
    return {
        "requests": requests,
        "errors": len(errors),
        "error_rate": round(len(errors) / requests, 3) if requests else None,
        "p50_ms": percentile(latencies, 50),
        "p95_ms": percentile(latencies, 95),
        "cache_hit_rate": round(sum(1 for r in calls if r["cache_read_tokens"] > 0) / len(calls), 3) if calls else None,
        "cost_usd": round(sum(r["cost_usd"] for r in calls), 4),
    }


def evaluate_alerts(metrics, rules):
    alerts = []
    for rule in rules:
        value = metrics.get(rule["metric"])
        if value is None or metrics.get("requests", 0) < rule.get("min_requests", 0):
            continue
        firing = value > rule["threshold"] if rule["op"] == ">" else value < rule["threshold"]
        if firing:
            alerts.append(f"[{rule['severity']}] {rule['name']}: {rule['metric']} is {value} "
                          f"(threshold {rule['op']} {rule['threshold']})")
    return alerts


def scan(records, start, end, window_s, rules):
    firing = []
    for window_start in range(start, end, window_s):
        alerts = evaluate_alerts(window_metrics(records, window_start, window_start + window_s), rules)
        if alerts:
            firing.append({"window_start": window_start, "alerts": alerts})
    return firing


# --- Try it out (not graded) ---
for minute in range(0, 120, 15):
    m = window_metrics(RECORDS, START + minute * 60, START + (minute + 15) * 60)
    if m:
        print(f"min {minute:>3}-{minute + 15:<3} {m}")
results = scan(RECORDS, START, START + 7200, 900, ALERT_RULES)
if results:
    for r in results:
        print(f"\nwindow starting at minute {(r['window_start'] - START) // 60}:")
        for alert in r["alerts"]:
            print("  ", alert)
