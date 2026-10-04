from fde_datasets import incident


def _parsed():
    return parse_lines(incident.LOG_LINES)


def test_parse_lines_small():
    """parse_lines() keeps JSON objects with ts and event, sorted, and counts the rest"""
    lines = ['{"ts": "2026-01-01T10:00:05Z", "event": "b"}', "not json", '{"ts": "2026-01-01T10:00:01Z", "event": "a"}',
             "", "[1, 2]", '{"event": "no ts"}', '{"ts": "2026-01-01T10:00:0']
    records, skipped = parse_lines(lines)
    assert [r["event"] for r in records] == ["a", "b"], "sort by ts"
    assert skipped == 5, f"skipped {skipped}"


def test_parse_lines_real():
    """parse_lines() handles the incident logs"""
    records, skipped = _parsed()
    assert len(records) == 668 and skipped == 4, f"{len(records)} records, {skipped} skipped"
    assert records[0]["event"] == "deploy" and records[0]["version"] == "v1.7.3", "the oldest record comes first"


def test_request_timeline():
    """request_timeline() tells one request's story"""
    records, _ = _parsed()
    assert request_timeline(records, "req-1166") == [
        "14:25:24 llm_error RateLimitError (attempt 1)",
        "14:25:26 llm_error RateLimitError (attempt 2)",
        "14:25:27 http_request 503",
    ], f"got {request_timeline(records, 'req-1166')}"
    assert request_timeline(records, "req-1000") == ["13:30:04 llm_call 1441ms", "13:30:05 http_request 200"]
    assert request_timeline(records, "req-nope") == []


def test_by_version():
    """by_version() compares the two releases"""
    records, _ = _parsed()
    got = by_version(records)
    assert got == {
        "v1.7.3": {"calls": 180, "errors": 0, "cache_hit_rate": 0.933, "cache_write_rate": 0.067,
                   "avg_cost_usd": 0.00266, "avg_latency_ms": 974},
        "v1.8.0": {"calls": 119, "errors": 51, "cache_hit_rate": 0.0, "cache_write_rate": 1.0,
                   "avg_cost_usd": 0.0091, "avg_latency_ms": 1434},
    }, f"got {got}"


def test_incident_summary():
    """incident_summary() extracts the facts for the report"""
    records, _ = _parsed()
    got = incident_summary(records)
    assert got == {"bad_version": "v1.8.0", "deployed_at": "14:00:00", "rolled_back_at": "14:45:00",
                   "first_error_at": "14:20:24", "failed_requests": 16, "extra_cost_usd": 0.7664}, f"got {got}"


def test_root_cause():
    """ROOT_CAUSE matches what the data shows"""
    assert ROOT_CAUSE in CAUSES, "set ROOT_CAUSE to one of the CAUSES keys"
    assert ROOT_CAUSE == "prompt_prefix_changes_every_request", \
        "Look again: errors are 429s (not 5xx), traffic is flat, and v1.8.0 writes the cache on every call."
