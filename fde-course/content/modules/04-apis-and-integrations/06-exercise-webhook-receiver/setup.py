# Builds a realistic burst of webhook deliveries, signed the way Northwind signs them.
import hashlib as _hashlib
import hmac as _hmac
import json as _json

_SECRET = "whsec_northwind_demo"
_NOW = 1773130300


def _northwind_sign(timestamp, body, secret=_SECRET):
    return _hmac.new(secret.encode(), f"{timestamp}.{body}".encode(), _hashlib.sha256).hexdigest()


def _delivery(event, ts=_NOW - 5, secret=_SECRET, tamper=False):
    body = _json.dumps(event)
    sig = _northwind_sign(ts, body, secret)
    if tamper:
        body = body.replace("in_transit", "delivered")
    return {"X-Northwind-Timestamp": str(ts), "X-Northwind-Signature": sig}, body


def _evt(eid, shipment, status, at, etype="shipment.updated"):
    return {"id": eid, "type": etype, "occurred_at": at, "data": {"shipment_id": shipment, "status": status}}


BURST = [
    ("normal update", *_delivery(_evt("evt_1", "SHP-1003", "in_transit", "2026-03-10T08:00:00Z"))),
    ("newer update", *_delivery(_evt("evt_2", "SHP-1003", "delivered", "2026-03-10T08:15:00Z"))),
    ("duplicate delivery", *_delivery(_evt("evt_2", "SHP-1003", "delivered", "2026-03-10T08:15:00Z"))),
    ("late, older event", *_delivery(_evt("evt_0", "SHP-1003", "picked_up", "2026-03-10T07:30:00Z"))),
    ("other event type", *_delivery(_evt("evt_3", "SHP-1004", "n/a", "2026-03-10T08:20:00Z", etype="invoice.created"))),
    ("forged (wrong secret)", *_delivery(_evt("evt_4", "SHP-1005", "delivered", "2026-03-10T08:21:00Z"), secret="guess")),
    ("tampered body", *_delivery(_evt("evt_5", "SHP-1006", "in_transit", "2026-03-10T08:22:00Z"), tamper=True)),
    ("replayed (1 hour old)", *_delivery(_evt("evt_6", "SHP-1007", "delivered", "2026-03-10T07:00:00Z"), ts=_NOW - 3600)),
    ("new shipment", *_delivery(_evt("evt_7", "SHP-1008", "exception", "2026-03-10T08:25:00Z"))),
]
