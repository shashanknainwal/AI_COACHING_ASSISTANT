---
title: "Exercise: A Webhook Receiver That Can't Be Fooled"
type: exercise
minutes: 30
hints:
  - "`sign`: `hmac.new(secret.encode(), f\"{timestamp}.{body}\".encode(), hashlib.sha256).hexdigest()`."
  - "`verify_signature`: convert the timestamp with `int(timestamp)` inside a try/except (return False on `ValueError` or `TypeError`), check `abs(now - ts) <= tolerance`, then `hmac.compare_digest(sign(...), signature)`."
  - "In `handle_webhook`, read the headers with `.get(...)` so a missing header gives None, which then fails verification."
  - "Verify **before** `json.loads`. Parse inside `try/except ValueError` and return `(400, \"bad payload\")` on failure."
  - "Order of checks after parsing: duplicate event id → record the id → ignored type → stale → applied."
  - "Stale check: `current = store.get(shipment_id)`; if `current` and `current[\"updated_at\"] >= event[\"occurred_at\"]`, it's stale."
---

Northwind will push shipment updates to the retailer's integration as webhooks. You're writing the handler. It must reject forged and replayed requests, survive duplicate deliveries, and never let a late, older event overwrite newer data.

## The request

```python
headers = {
    "X-Northwind-Timestamp": "1773130000",            # Unix seconds, as a string
    "X-Northwind-Signature": "5f2c9a...",             # hex HMAC-SHA256
}
body = '{"id": "evt_8812", "type": "shipment.updated", "occurred_at": "2026-03-10T08:15:00Z", "data": {"shipment_id": "SHP-1003", "status": "delivered"}}'
```

The signature is the hex HMAC-SHA256, keyed with the shared secret, of the message `f"{timestamp}.{body}"`.

## Your task

**1. `sign(secret, timestamp, body)`** returns that hex signature.

**2. `verify_signature(secret, timestamp, body, signature, now, tolerance=300)`** returns `True` only if:
- `timestamp` converts to an integer (otherwise `False`),
- it's within `tolerance` seconds of `now` (in either direction), and
- `signature` matches `sign(...)`, compared with `hmac.compare_digest`.

**3. `handle_webhook(headers, body, secret, now, store, seen_events)`** returns a tuple `(status_code, message)` and updates `store` and `seen_events` in place:

| Check, in order | Result |
|---|---|
| Signature invalid (or headers missing) | `(401, "invalid signature")` |
| Body isn't valid JSON | `(400, "bad payload")` |
| Event `id` already in `seen_events` | `(200, "duplicate")` |
| *(otherwise, add the id to `seen_events`)* | |
| `type` isn't `"shipment.updated"` | `(200, "ignored")` |
| `store` already has this shipment with `updated_at` ≥ the event's `occurred_at` | `(200, "stale")` |
| Otherwise set `store[shipment_id] = {"status": ..., "updated_at": occurred_at}` | `(200, "applied")` |

Press **Run** to replay a realistic burst of webhooks (including a forgery, a replay, a duplicate, and an out-of-order event), then **Submit**.
