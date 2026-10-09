---
title: "Webhooks, Signatures, and Idempotent Processing"
type: reading
minutes: 3
---

> **By the end of this lesson you will be able to:**
> - Choose between polling and webhooks
> - Verify webhook signatures with HMAC and reject replays
> - Process duplicate and out-of-order events without corrupting data

Leah wants the ERP updated within seconds when a shipment is delivered, so Northwind will POST a webhook to your endpoint on every change. That endpoint is public, the sender retries, and events don't arrive in order. Get any of that wrong and a customer gets two "delivered" emails, or a delivered shipment flips back to "in transit".

## Polling vs. webhooks

| | Polling | Webhooks |
|---|---|---|
| Freshness | Minutes behind | Seconds |
| Complexity | Low | Public endpoint, security, retries |
| Missed changes | Easy to catch up by time | Possible if your endpoint was down |

Robust integrations use **both**: webhooks for speed, plus a periodic poll (next lesson) to catch what was missed.

## What a webhook looks like

```http
POST /webhooks/northwind
X-Northwind-Timestamp: 1773130000
X-Northwind-Signature: 5f2c9a...e81
Content-Type: application/json

{"id": "evt_8812", "type": "shipment.updated", "occurred_at": "2026-03-10T08:15:00Z",
 "data": {"shipment_id": "SHP-1003", "status": "delivered"}}
```

If you don't answer 2xx quickly, Northwind **retries**, possibly for hours.

## Rule 1: verify the signature first

Anyone who finds your URL can POST fake events. The sender signs each request with a shared secret, commonly **HMAC-SHA256** over the timestamp and raw body:

```python
import hashlib
import hmac

def sign(secret, timestamp, body):
    message = f"{timestamp}.{body}".encode()
    return hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()

expected = sign(secret, timestamp, raw_body)
valid = hmac.compare_digest(expected, received_signature)
```

- **Sign the raw body** as received; re-serialized JSON may differ.
- **Use `hmac.compare_digest`**, not `==`. A normal comparison stops at the first difference, and that timing leak lets an attacker guess a signature character by character.
- **Reject timestamps older than about 5 minutes**, so a captured request can't be **replayed**. The timestamp is inside the signed message, so it can't be altered.

Header names vary by sender; follow their docs.

## Rule 2: expect duplicates

Delivery is **at-least-once**. Record each event ID and skip ones you've seen:

```python
if event["id"] in processed_ids:
    return 200, "duplicate"      # still 2xx so the sender stops retrying
processed_ids.add(event["id"])
```

In production that's a table with a unique constraint on the event ID.

## Rule 3: expect events out of order

```
08:00  SHP-1003 → in_transit   (delayed, arrives second)
08:15  SHP-1003 → delivered    (arrives first)
```

**Apply an event only if it's newer than what you have**; otherwise mark it **stale**. ISO 8601 timestamps in the same format and zone sort correctly as strings; otherwise parse them first.

## Rule 4: respond fast, process later

```
receive → verify signature → store raw event in a queue/table → return 200
                                          │
                     background worker ───┘→ dedupe → order check → apply
```

Slow endpoints time out under load, which triggers retries, which adds load. (The exercise processes inline for simplicity.)

## Return the right status

| Situation | Return |
|---|---|
| Bad or missing signature | 401 |
| Malformed body | 400 |
| Duplicate, ignored type, or stale event | 200 |
| Your database is down | 500 (you want a retry) |

> **Key takeaways**
> - Webhooks for speed, a periodic poll as a safety net.
> - HMAC over timestamp and raw body, `compare_digest`, reject old timestamps.
> - Dedupe by event ID; apply only newer events.
> - Acknowledge fast with the right status; do heavy work in the background.
