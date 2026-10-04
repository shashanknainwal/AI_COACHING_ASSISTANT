import hashlib
import hmac
import json

SECRET = "whsec_northwind_demo"   # in real code: os.environ["NORTHWIND_WEBHOOK_SECRET"]
NOW = 1773130300                  # "current" Unix time for this exercise


def sign(secret, timestamp, body):
    """Hex HMAC-SHA256 of f"{timestamp}.{body}" keyed with secret."""
    # TODO
    pass


def verify_signature(secret, timestamp, body, signature, now, tolerance=300):
    """True only for a fresh timestamp and a matching signature."""
    # TODO
    pass


def handle_webhook(headers, body, secret, now, store, seen_events):
    """Return (status_code, message); update store and seen_events in place."""
    # TODO
    pass


# --- Try it out (not graded) ---
store, seen = {}, set()
for label, headers, body in BURST:
    result = handle_webhook(headers, body, SECRET, NOW, store, seen)
    print(f"{label:<24} -> {result}")
print("\nFinal state:", store)
