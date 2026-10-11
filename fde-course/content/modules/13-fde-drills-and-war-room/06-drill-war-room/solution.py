from collections import Counter

LOGS = "/tmp/relay_incident/logs"


def _field(line, name):
    for part in line.split():
        if part.startswith(name + "="):
            return part.split("=", 1)[1]
    return None


# Level 1: stop the bleeding with a settings override, not a code change.
# CHANGELOG + config: 2.4.0 turned on fast_retry, which ignores Retry-After.
def stabilise():
    return {"fast_retry": False}


# Level 2: facts from the raw logs.
with open(LOGS + "/erp_audit.log") as f:
    _invoices = Counter(_field(l, "event") for l in f if "invoice_created" in l)
with open(LOGS + "/relay.log") as f:
    _dead = sorted({_field(l, "event") for l in f if " dead_letter " in l})

ROOT_CAUSE = {
    "file": "relay/keys.py",
    "function": "idempotency_key",
    "introduced_in": "2.4.0",
    "duplicated_events": sorted(e for e, n in _invoices.items() if n > 1),
    "dead_lettered": _dead,
}


# Level 3: the patch and the regression check.
def fixed_idempotency_key(event, attempt):
    """One key per event, the same on every attempt."""
    return event["id"]


def check_idempotency_key(key_fn):
    a = {"id": "evt_1", "customer": "acme", "amount": 500}
    b = {"id": "evt_2", "customer": "acme", "amount": 500}
    assert key_fn(a, 1) == key_fn(a, 2) == key_fn(a, 6), "a retry must reuse the key"
    assert key_fn(a, 1) != key_fn(b, 1), "different events must get different keys"


# Level 4: the update for Petra's channel.
STATUS_UPDATE = """Incident update, 09:45 UTC. Relay 2.4.0 was deployed at 09:12.
Impact: the client's ERP created 8 duplicate invoices for 8 orders (list sent to finance),
and 16 order events were dead-lettered after a 429 retry storm.
Mitigation: fast_retry is disabled by settings override; no new duplicates or dead letters since.
Root cause: 2.4.0 put the attempt number in the idempotency key, so the ERP treated every retry as a new order.
Fix: a patch restores one key per event, with a regression test; it ships after review.
Next: finance voids the duplicates; we check which dead-lettered events were already invoiced before replaying any.
Next update 10:30 UTC."""


if __name__ == "__main__":
    print(stabilise())
    print(ROOT_CAUSE)
