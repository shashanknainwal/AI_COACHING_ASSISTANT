import hashlib
import hmac
import json

SECRET = "whsec_northwind_demo"   # in real code: os.environ["NORTHWIND_WEBHOOK_SECRET"]
NOW = 1773130300                  # "current" Unix time for this exercise


def sign(secret, timestamp, body):
    return hmac.new(secret.encode(), f"{timestamp}.{body}".encode(), hashlib.sha256).hexdigest()


def verify_signature(secret, timestamp, body, signature, now, tolerance=300):
    try:
        ts = int(timestamp)
    except (TypeError, ValueError):
        return False
    if abs(now - ts) > tolerance or signature is None:
        return False
    return hmac.compare_digest(sign(secret, timestamp, body), signature)


def handle_webhook(headers, body, secret, now, store, seen_events):
    timestamp = headers.get("X-Northwind-Timestamp")
    signature = headers.get("X-Northwind-Signature")
    if not verify_signature(secret, timestamp, body, signature, now):
        return 401, "invalid signature"
    try:
        event = json.loads(body)
    except ValueError:
        return 400, "bad payload"
    if event["id"] in seen_events:
        return 200, "duplicate"
    seen_events.add(event["id"])
    if event["type"] != "shipment.updated":
        return 200, "ignored"
    shipment_id = event["data"]["shipment_id"]
    current = store.get(shipment_id)
    if current and current["updated_at"] >= event["occurred_at"]:
        return 200, "stale"
    store[shipment_id] = {"status": event["data"]["status"], "updated_at": event["occurred_at"]}
    return 200, "applied"


# --- Try it out (not graded) ---
store, seen = {}, set()
for label, headers, body in BURST:
    result = handle_webhook(headers, body, SECRET, NOW, store, seen)
    print(f"{label:<24} -> {result}")
print("\nFinal state:", store)
