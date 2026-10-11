# Writes Marram's order-relay service and the incident logs to the virtual filesystem.
# It runs before your code on every Run and Submit, so the files always start clean.
import importlib as _importlib
import os as _os
import sys as _sys

ROOT = "/tmp/relay_incident"
SERVICE = ROOT + "/service"
LOGS = ROOT + "/logs"

_RELAY_FILES = {
    "relay/__init__.py": '''"""Marram order relay: delivers order events to a client's ERP."""
''',
    "relay/config.py": '''VERSION = "2.4.0"

SETTINGS = {
    "max_attempts": 6,
    "base_delay": 1,        # seconds
    "fast_retry": True,     # new in 2.4.0, on by default
    "log_payloads": False,
}
''',
    "relay/keys.py": '''def idempotency_key(event, attempt):
    """The Idempotency-Key header sent to the ERP for this delivery attempt."""
    # 2.4.0: include the attempt number so traces can tell retries apart.
    return f"{event['id']}-{attempt}"
''',
    "relay/backoff.py": '''def next_delay(attempt, retry_after, settings):
    """Seconds to wait before the next attempt."""
    if settings["fast_retry"]:
        return 0  # 2.4.0: retry at once; the ERP is usually fine
    if retry_after is not None:
        return max(retry_after, settings["base_delay"])
    return settings["base_delay"] * 2 ** (attempt - 1)
''',
    "relay/erp.py": '''class FakeERP:
    """A stand-in for the client's ERP, faithful to how it behaves under load.

    Per one-second window: the first 3 requests are handled normally. Requests 4-5
    are committed but the connection drops before the reply (status 504). Later
    requests get 429 with Retry-After: 1. A key the ERP has seen before returns 200
    and creates nothing.
    """

    def __init__(self, audit=None):
        self.window = None
        self.n = 0
        self.keys = {}
        self.invoices = []   # (time_ms, event_id, key)
        self.audit = audit

    def post(self, key, event, now_ms):
        w = now_ms // 1000
        if w != self.window:
            self.window, self.n = w, 0
        self.n += 1
        if self.n > 5:
            return 429, 1, 20
        if key in self.keys:
            status = 200
        else:
            self.keys[key] = event["id"]
            self.invoices.append((now_ms, event["id"], key))
            if self.audit:
                self.audit(now_ms, f"invoice_created invoice=INV-{50000 + len(self.invoices)} event={event['id']} idem_key={key}")
            status = 201
        if self.n > 3:
            return 504, None, 300
        return status, None, 60
''',
    "relay/worker.py": '''from relay import backoff, keys


def _log(log, now, level, text):
    if log:
        log(now, level, text)


def deliver_all(events, erp, settings, log=None):
    """Deliver events one at a time, retrying failures. Returns stats."""
    now = 0
    stats = {"delivered": 0, "dead_letter": [], "status_counts": {}}
    for event in events:
        attempt = 1
        while True:
            key = keys.idempotency_key(event, attempt)
            status, retry_after, latency = erp.post(key, event, now)
            now += latency
            stats["status_counts"][status] = stats["status_counts"].get(status, 0) + 1
            level = "INFO" if status in (200, 201) else "WARN"
            _log(log, now, level, f"deliver event={event['id']} attempt={attempt} key={key} status={status} latency_ms={latency}")
            if status in (200, 201):
                stats["delivered"] += 1
                break
            if attempt >= settings["max_attempts"]:
                stats["dead_letter"].append(event["id"])
                _log(log, now, "ERROR", f"dead_letter event={event['id']} attempts={attempt} last_status={status}")
                break
            now += int(backoff.next_delay(attempt, retry_after, settings) * 1000)
            attempt += 1
    stats["end_ms"] = now
    return stats
''',
    "relay/sample_events.py": '''# The 40 order events from the incident window, captured for replay.
EVENTS = [
    {"id": f"evt_{1001 + i}", "customer": ["acme", "borealis", "cinder", "dune"][i % 4], "amount": 500 + 37 * i}
    for i in range(40)
]
''',
    "CHANGELOG.md": '''# Changelog

## 2.4.0 (2026-10-09)
- New `fast_retry` setting, on by default: retry failed deliveries at once instead of waiting.
- Idempotency keys now include the attempt number, so traces can tell retries apart.
- Upgrade log formatter.

## 2.3.1 (2026-09-30)
- Fix: honour Retry-After on 429.
''',
    "README.md": '''# relay

Delivers order events to the client's ERP. Settings live in relay/config.py and can be
overridden at deploy time without a code change (the on-call runbook calls this a
"settings override"). Replay a captured window with relay.worker.deliver_all.
''',
}


def _write_all():
    for rel, text in _RELAY_FILES.items():
        path = _os.path.join(SERVICE, rel)
        _os.makedirs(_os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)


def _purge():
    for name in [m for m in _sys.modules if m == "relay" or m.startswith("relay.")]:
        del _sys.modules[name]
    _importlib.invalidate_caches()


def _stamp(ms, base_s=9 * 3600 + 12 * 60 + 30):
    s = base_s + ms // 1000
    return f"2026-10-09T{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}Z"


def _write_logs():
    relay_lines = [
        "2026-10-09T08:58:40Z db WARN slow query orders_by_customer 1840ms",
        "2026-10-09T09:05:12Z relay[2.3.1] INFO deliver event=evt_0991 attempt=1 key=evt_0991 status=201 latency_ms=60",
        "2026-10-09T09:05:13Z relay[2.3.1] WARN deliver event=evt_0992 attempt=1 key=evt_0992 status=504 latency_ms=300",
        "2026-10-09T09:05:15Z relay[2.3.1] INFO deliver event=evt_0992 attempt=2 key=evt_0992 status=200 latency_ms=60",
        "2026-10-09T09:09:47Z relay[2.3.1] INFO deliver event=evt_0993 attempt=1 key=evt_0993 status=201 latency_ms=60",
        "2026-10-09T09:12:04Z deploy INFO relay 2.3.1 -> 2.4.0 (pipeline run 8812, change MR-4471)",
        "2026-10-09T09:12:30Z relay[2.4.0] INFO worker started backlog=40",
    ]
    audit_lines = [
        "2026-10-09T09:05:12Z erp-audit invoice_created invoice=INV-49998 event=evt_0991 idem_key=evt_0991",
        "2026-10-09T09:05:13Z erp-audit invoice_created invoice=INV-49999 event=evt_0992 idem_key=evt_0992",
        "2026-10-09T09:09:47Z erp-audit invoice_created invoice=INV-50000 event=evt_0993 idem_key=evt_0993",
    ]
    _sys.path.insert(0, SERVICE)
    import relay.config
    import relay.erp
    import relay.sample_events
    import relay.worker

    erp = relay.erp.FakeERP(audit=lambda ms, text: audit_lines.append(f"{_stamp(ms)} erp-audit {text}"))
    relay.worker.deliver_all(
        relay.sample_events.EVENTS, erp, dict(relay.config.SETTINGS),
        log=lambda ms, level, text: relay_lines.append(f"{_stamp(ms)} relay[2.4.0] {level} {text}"),
    )
    relay_lines.append("2026-10-09T09:13:05Z alert CRITICAL relay dead_letter_queue depth above 10")
    _os.makedirs(LOGS, exist_ok=True)
    with open(LOGS + "/relay.log", "w") as f:
        f.write("\n".join(relay_lines) + "\n")
    with open(LOGS + "/erp_audit.log", "w") as f:
        f.write("\n".join(audit_lines) + "\n")
    _purge()


_purge()
_write_all()
if SERVICE in _sys.path:
    _sys.path.remove(SERVICE)
_write_logs()
if SERVICE not in _sys.path:
    _sys.path.insert(0, SERVICE)
