import json


def test_sign_matches_northwind():
    """sign() produces the same signature as Northwind"""
    got = sign("s3cret", 1773130000, '{"a": 1}')
    want = _northwind_sign(1773130000, '{"a": 1}', secret="s3cret")
    assert got == want, f"expected {want}, got {got!r}"
    assert sign("s3cret", "1773130000", "x") == _northwind_sign("1773130000", "x", secret="s3cret"), "timestamp may be a string"


def test_verify_valid_and_tolerance():
    """verify_signature() accepts fresh valid signatures, within tolerance both ways"""
    body = '{"id": "e"}'
    for ts in (NOW, NOW - 300, NOW + 300):
        sig = _northwind_sign(ts, body)
        assert verify_signature(SECRET, str(ts), body, sig, NOW) is True, f"timestamp {ts - NOW:+}s should be accepted"


def test_verify_rejects():
    """verify_signature() rejects old timestamps, wrong signatures and junk timestamps"""
    body = '{"id": "e"}'
    old = NOW - 301
    assert verify_signature(SECRET, str(old), body, _northwind_sign(old, body), NOW) is False, "301s old should be rejected (replay)"
    assert verify_signature(SECRET, str(NOW), body, _northwind_sign(NOW, body, secret="other"), NOW) is False, "wrong secret"
    assert verify_signature(SECRET, str(NOW), body + " ", _northwind_sign(NOW, body), NOW) is False, "body changed after signing"
    assert verify_signature(SECRET, "yesterday", body, "abc", NOW) is False, "a non-integer timestamp should return False, not crash"
    assert verify_signature(SECRET, None, body, None, NOW) is False, "missing headers should return False"


def test_burst_results():
    """handle_webhook() returns the right result for every delivery in the burst"""
    store, seen = {}, set()
    got = [handle_webhook(h, b, SECRET, NOW, store, seen) for _, h, b in BURST]
    want = [(200, "applied"), (200, "applied"), (200, "duplicate"), (200, "stale"), (200, "ignored"),
            (401, "invalid signature"), (401, "invalid signature"), (401, "invalid signature"), (200, "applied")]
    for (label, _, _), g, w in zip(BURST, got, want):
        assert g == w, f"{label}: expected {w}, got {g}"


def test_final_state():
    """The store ends with the newest status per shipment"""
    store, seen = {}, set()
    for _, h, b in BURST:
        handle_webhook(h, b, SECRET, NOW, store, seen)
    assert store == {
        "SHP-1003": {"status": "delivered", "updated_at": "2026-03-10T08:15:00Z"},
        "SHP-1008": {"status": "exception", "updated_at": "2026-03-10T08:25:00Z"},
    }, f"got {store}"
    assert seen == {"evt_1", "evt_2", "evt_0", "evt_3", "evt_7"}, f"rejected (401) events must not be recorded as seen; got {sorted(seen)}"


def test_bad_payload():
    """A correctly signed body that isn't JSON gets (400, 'bad payload')"""
    body = "not json{"
    h = {"X-Northwind-Timestamp": str(NOW), "X-Northwind-Signature": _northwind_sign(NOW, body)}
    assert handle_webhook(h, body, SECRET, NOW, {}, set()) == (400, "bad payload")


def test_missing_headers():
    """Missing signature headers are rejected, not a crash"""
    assert handle_webhook({}, '{"id": "e"}', SECRET, NOW, {}, set()) == (401, "invalid signature")


def test_equal_timestamp_is_stale():
    """An event with the same occurred_at as the stored one is stale"""
    store = {"S": {"status": "delivered", "updated_at": "2026-03-10T08:00:00Z"}}
    h, b = _delivery(_evt("evt_x", "S", "in_transit", "2026-03-10T08:00:00Z"), ts=NOW)
    assert handle_webhook(h, b, SECRET, NOW, store, set()) == (200, "stale")
    assert store["S"]["status"] == "delivered", "a stale event must not change the store"
