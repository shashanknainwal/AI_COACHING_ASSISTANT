"""Raw log lines from Brightway's triage service on the afternoon of an incident (Module 9).

LOG_LINES is a list of strings, exactly as they came out of the log pipeline:
mostly JSON, with a few lines that aren't.
"""

import json
from datetime import datetime, timedelta, timezone

_T0 = datetime(2026, 3, 10, 13, 30, tzinfo=timezone.utc)


def _iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _generate():
    seed = 42

    def rand():
        nonlocal seed
        seed = (seed * 1103515245 + 12345) % 2**31
        return seed / 2**31

    lines = [json.dumps({"ts": _iso(_T0 - timedelta(hours=20)), "level": "info", "event": "deploy", "version": "v1.7.3",
                         "change": "Tighten urgency rules for safety tickets"})]
    deploy_at, rollback_at = _T0 + timedelta(minutes=30), _T0 + timedelta(minutes=75)
    lines.append(json.dumps({"ts": _iso(deploy_at), "level": "info", "event": "deploy", "version": "v1.8.0",
                             "change": "Include the current date and time in the system prompt"}))
    lines.append(json.dumps({"ts": _iso(rollback_at), "level": "warning", "event": "deploy", "version": "v1.7.3",
                             "change": "Rollback of v1.8.0"}))
    last_write = None
    for i in range(315):                                  # one ticket every 20 seconds, 13:30-15:15
        t = _T0 + timedelta(seconds=20 * i + 3)
        version = "v1.8.0" if deploy_at <= t < rollback_at else "v1.7.3"
        rid = f"req-{1000 + i}"
        if version == "v1.8.0":
            write, read = 3000, 0                         # the prefix changes every request: always a cache write
        elif last_write is None or (t - last_write).total_seconds() >= 300:
            write, read, last_write = 3000, 0, t
        else:
            write, read = 0, 3000
        base_latency = int(700 + rand() * 500 + (450 if write else 0))
        limited = version == "v1.8.0" and t >= _T0 + timedelta(minutes=50) and rand() < 0.45
        events, status = [], 200
        if limited:
            events.append({"ts": _iso(t + timedelta(seconds=1)), "level": "error", "event": "llm_error", "request_id": rid,
                           "version": version, "error_type": "RateLimitError", "attempt": 1})
            if rand() < 0.5:
                events.append({"ts": _iso(t + timedelta(seconds=3)), "level": "error", "event": "llm_error", "request_id": rid,
                               "version": version, "error_type": "RateLimitError", "attempt": 2})
                status = 503
        if status == 200:
            cost = round((200 * 2 + write * 2.5 + read * 0.2 + 120 * 10) / 1e6, 6)
            events.append({"ts": _iso(t + timedelta(milliseconds=base_latency + (2500 if limited else 0))), "level": "info",
                           "event": "llm_call", "request_id": rid, "version": version, "model": "claude-sonnet-5-5",
                           "input_tokens": 200, "cache_write_tokens": write, "cache_read_tokens": read, "output_tokens": 120,
                           "latency_ms": base_latency, "cost_usd": cost})
        events.append({"ts": _iso(t + timedelta(seconds=4 if limited else 2)), "level": "info" if status == 200 else "error",
                       "event": "http_request", "request_id": rid, "path": "/v1/triage", "status": status})
        lines.extend(json.dumps(e) for e in events)
        if i == 80:
            lines.append("Traceback (most recent call last):")
        if i == 150:
            lines.append('{"ts": "2026-03-10T14:20:03Z", "level": "info", "event": "llm_ca')
        if i == 200:
            lines.append("")
        if i == 260:
            lines.append("[1, 2, 3]")
    return lines


LOG_LINES = _generate()
