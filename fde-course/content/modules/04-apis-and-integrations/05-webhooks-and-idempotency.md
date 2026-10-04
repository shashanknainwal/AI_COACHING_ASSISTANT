---
title: "Webhooks, Signatures, and Idempotent Processing"
type: reading
minutes: 16
---

> **By the end of this lesson you will be able to:**
> - Choose between polling and webhooks for a given integration
> - Verify webhook signatures with HMAC, and reject replayed requests
> - Process events that arrive twice or out of order without corrupting data
> - Design a webhook endpoint that stays fast and reliable under load

## Polling vs. webhooks

There are two ways to learn that something changed in another system:

- **Polling:** you ask on a schedule. "Any shipments updated since 10:00?" Simple, and you control the pace. But you're always a little behind, and most requests return nothing new.
- **Webhooks:** the other system calls *you* when something happens. Near real-time and efficient. But now you're running a public endpoint that receives traffic you don't control.

| | Polling | Webhooks |
|---|---|---|
| Freshness | Minutes behind | Seconds |
| Complexity | Low | Higher: public endpoint, security, retries |
| Missed changes | Easy to catch up (query by time) | Possible if your endpoint was down |
| Load | Constant, mostly wasted | Proportional to real changes |

Most robust integrations use **both**: webhooks for speed, plus a periodic poll (the next lesson's incremental sync) to catch anything missed while your endpoint was down.

## What a webhook looks like

Northwind sends an HTTP POST to a URL you give them whenever a shipment changes:

```http
POST /webhooks/northwind
X-Northwind-Timestamp: 1773130000
X-Northwind-Signature: 5f2c9a...e81
Content-Type: application/json

{"id": "evt_8812", "type": "shipment.updated", "occurred_at": "2026-03-10T08:15:00Z",
 "data": {"shipment_id": "SHP-1003", "status": "delivered"}}
```

Your endpoint must answer quickly with a 2xx status. If it doesn't (an error, or a timeout), Northwind **retries**, possibly several times over hours.

## Rule 1: verify the signature before trusting anything

Your webhook URL is public. Anyone who discovers it can POST fake events ("SHP-1003 delivered!"). Senders prevent this by **signing** each request with a secret shared only with you.

The most common scheme is **HMAC-SHA256** over the timestamp and the raw body:

```python
import hashlib
import hmac

def sign(secret, timestamp, body):
    message = f"{timestamp}.{body}".encode()
    return hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()

expected = sign(secret, timestamp, raw_body)
valid = hmac.compare_digest(expected, received_signature)
```

Three details that matter:

- **Sign the raw body**, exactly as received. If you parse the JSON and re-serialize it, spacing or key order may change and the signature won't match.
- **Use `hmac.compare_digest`**, not `==`. A normal string comparison stops at the first different character, and an attacker can measure that timing difference to guess a valid signature one character at a time. `compare_digest` takes the same time regardless.
- **Check the timestamp.** Reject requests older than about 5 minutes. Otherwise an attacker who captures one valid request can **replay** it later, and the signature will still be valid. Including the timestamp in the signed message means it can't be changed without breaking the signature.

Exact header names and formats vary by sender (Stripe, GitHub, and Shopify each do it slightly differently), so follow the sender's documentation. The principles are always the same.

## Rule 2: expect duplicates

Webhook delivery is almost always **at-least-once**. If your endpoint processed an event but the response was lost, the sender retries, and you get the same event again. If you blindly apply it twice, you might send a customer two "delivered" emails or double-count something.

The fix is **idempotent processing**: record each event ID you've handled, and skip any ID you've already seen.

```python
if event["id"] in processed_ids:
    return 200, "duplicate"      # still return 2xx so the sender stops retrying
processed_ids.add(event["id"])
```

In production, `processed_ids` lives in a database table with a unique constraint on the event ID, so it survives restarts and works across multiple servers.

## Rule 3: expect events out of order

Network delays and retries mean events can arrive in a different order than they happened:

```
08:00  shipment.updated  SHP-1003 → in_transit   (delayed, arrives second)
08:15  shipment.updated  SHP-1003 → delivered    (arrives first)
```

If you apply events in arrival order, SHP-1003 ends up "in_transit," which is wrong. Protect against this by comparing timestamps (or version numbers): **only apply an event if it's newer than what you already have.** Otherwise, mark it **stale** and ignore it.

ISO 8601 timestamps in the same format and time zone (`2026-03-10T08:15:00Z`) sort correctly as plain strings, which makes this check a one-liner. If formats might differ, parse them into datetimes first.

## Rule 4: respond fast, process later

Senders usually time out after a few seconds. If your endpoint calls the ERP, waits for Claude, and writes to three databases before answering, you'll time out under load, and the sender will retry, which adds even more load.

The standard pattern:

```
receive → verify signature → store the raw event in a queue/table → return 200
                                          │
                     background worker ───┘→ dedupe → order check → apply
```

In the exercise you'll do the processing inline to keep things simple, but in production, separate receiving from processing.

## The status codes you return matter

| Situation | Return | Why |
|---|---|---|
| Bad or missing signature | 401 | Don't process; the sender (or attacker) shouldn't retry forever |
| Malformed body | 400 | It won't get better on retry |
| Duplicate event | 200 | You already handled it; stop retries |
| Event type you don't care about | 200 | Acknowledge so it isn't retried |
| Stale (older than current state) | 200 | Handled correctly by ignoring it |
| Your database is down | 500 | You *want* the sender to retry later |

> **Key takeaways**
> - Use webhooks for speed and a periodic poll as a safety net.
> - Verify an HMAC signature over the timestamp and raw body with `compare_digest`, and reject old timestamps.
> - Delivery is at-least-once: dedupe by event ID. Events can arrive out of order: apply only newer ones.
> - Acknowledge quickly with the right status code; process heavy work in the background.
