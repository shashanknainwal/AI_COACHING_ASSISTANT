def _call(ts, latency, hit=True, cost=0.002):
    return {"ts": ts, "event": "llm_call", "latency_ms": latency, "cache_read_tokens": 3000 if hit else 0, "cost_usd": cost}


def _err(ts):
    return {"ts": ts, "event": "llm_error", "error_type": "RateLimitError", "latency_ms": 250}


def test_percentile():
    """percentile() uses the nearest-rank method"""
    values = [15, 20, 35, 40, 50]
    assert percentile(values, 50) == 35 and percentile(values, 30) == 20 and percentile(values, 100) == 50
    assert percentile(values, 0) == 15, "p0 is the smallest value"
    assert percentile(list(range(1, 101)), 95) == 95 and percentile(list(range(1, 21)), 95) == 19
    assert percentile([3, 1, 2], 50) == 2, "sort first"
    assert percentile([], 95) is None


def test_window_metrics_small():
    """window_metrics() computes every metric for one window"""
    recs = [_call(100, 800), _call(110, 1200, hit=False, cost=0.009), _err(120), _call(130, 900), _call(200, 99999)]
    got = window_metrics(recs, 100, 200)
    assert got == {"requests": 4, "errors": 1, "error_rate": 0.25, "p50_ms": 900, "p95_ms": 1200,
                   "cache_hit_rate": 0.667, "cost_usd": 0.013}, f"got {got}"


def test_window_metrics_empty():
    """An empty window gives zeros and None instead of crashing"""
    assert window_metrics([], 0, 60) == {"requests": 0, "errors": 0, "error_rate": None, "p50_ms": None, "p95_ms": None,
                                         "cache_hit_rate": None, "cost_usd": 0}
    only_errors = window_metrics([_err(5)], 0, 60)
    assert only_errors["error_rate"] == 1.0 and only_errors["p95_ms"] is None and only_errors["cache_hit_rate"] is None


def test_window_metrics_real_data():
    """window_metrics() on the service's records"""
    got = window_metrics(RECORDS, START + 75 * 60, START + 90 * 60)
    assert got == {"requests": 30, "errors": 5, "error_rate": 0.167, "p50_ms": 1194, "p95_ms": 4671,
                   "cache_hit_rate": 0.92, "cost_usd": 0.0619}, f"got {got}"


def test_evaluate_alerts():
    """evaluate_alerts() formats firing rules and skips missing or thin data"""
    metrics = {"requests": 30, "error_rate": 0.2, "p95_ms": 2000, "cache_hit_rate": 0.5, "cost_usd": 0.1}
    assert evaluate_alerts(metrics, ALERT_RULES) == [
        "[page] High error rate: error_rate is 0.2 (threshold > 0.05)",
        "[ticket] Cache hit rate low: cache_hit_rate is 0.5 (threshold < 0.8)",
    ]
    thin = dict(metrics, requests=3)
    assert evaluate_alerts(thin, ALERT_RULES) == ["[ticket] Cache hit rate low: cache_hit_rate is 0.5 (threshold < 0.8)"], \
        "the error-rate rule needs at least min_requests requests"
    assert evaluate_alerts({"requests": 0, "error_rate": None, "p95_ms": None, "cache_hit_rate": None, "cost_usd": 0}, ALERT_RULES) == []
    assert evaluate_alerts({"requests": 30, "p95_ms": 3000}, ALERT_RULES) == [], "the threshold itself doesn't fire"


def test_scan():
    """scan() finds the windows where the degradation shows"""
    got = scan(RECORDS, START, START + 7200, 900, ALERT_RULES)
    assert [(r["window_start"] - START) // 60 for r in got] == [75, 90, 105], f"windows: {[r['window_start'] for r in got]}"
    assert got[0]["alerts"] == ["[page] High error rate: error_rate is 0.167 (threshold > 0.05)",
                                "[page] Slow responses: p95_ms is 4671 (threshold > 3000)"]
