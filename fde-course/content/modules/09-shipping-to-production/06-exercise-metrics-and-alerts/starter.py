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
    """Nearest-rank percentile: the value at rank ceil(p/100 * n) in sorted order. None for no values."""
    # TODO
    pass


def window_metrics(records, start, end):
    """Metrics for records with start <= ts < end."""
    # TODO
    pass


def evaluate_alerts(metrics, rules):
    """Alert strings for every rule that fires."""
    # TODO
    pass


def scan(records, start, end, window_s, rules):
    """[{"window_start", "alerts"}] for each window (of window_s seconds) where any alert fires."""
    # TODO
    pass


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
