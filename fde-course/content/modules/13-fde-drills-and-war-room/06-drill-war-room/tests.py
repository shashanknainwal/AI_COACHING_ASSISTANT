import importlib as _il
import os as _os
import re as _re
import sys as _sys
from collections import Counter as _Counter

_SERVICE = "/tmp/relay_incident/service"
_LOGDIR = "/tmp/relay_incident/logs"


def _load():
    for name in [m for m in _sys.modules if m == "relay" or m.startswith("relay.")]:
        del _sys.modules[name]
    _il.invalidate_caches()
    if _SERVICE not in _sys.path:
        _sys.path.insert(0, _SERVICE)
    mods = {}
    for name in ("config", "keys", "backoff", "erp", "worker", "sample_events"):
        mods[name] = _il.import_module("relay." + name)
    return mods


def _replay(overrides=None, key_fn=None):
    m = _load()
    settings = dict(m["config"].SETTINGS)
    settings.update(overrides or {})
    if key_fn is not None:
        m["keys"].idempotency_key = key_fn
    erp = m["erp"].FakeERP()
    stats = m["worker"].deliver_all(m["sample_events"].EVENTS, erp, settings)
    dupes = sorted(e for e, n in _Counter(i for _, i, _ in erp.invoices).items() if n > 1)
    return stats, dupes, erp


def _truth():
    stats, dupes, erp = _replay()
    extra = len(erp.invoices) - len({i for _, i, _ in erp.invoices})
    return {"dupes": dupes, "dead": sorted(stats["dead_letter"]), "extra": extra}


def _status():
    text = STATUS_UPDATE
    assert isinstance(text, str) and text.strip(), "STATUS_UPDATE must be a non-empty string"
    return text


# Level 1: stabilise ------------------------------------------------------
def test_l1_override_uses_existing_settings():
    """stabilise() returns a dict that only overrides settings the service already has"""
    o = stabilise()
    assert isinstance(o, dict) and o, "return a non-empty dict of setting overrides"
    known = set(_load()["config"].SETTINGS)
    assert set(o) <= known, f"unknown settings: {sorted(set(o) - known)}; the service only reads {sorted(known)}"


def test_l1_no_dead_letters():
    """Replaying the incident window with your override dead-letters nothing"""
    stats, _, _ = _replay(stabilise())
    assert stats["dead_letter"] == [], f"{len(stats['dead_letter'])} events still dead-lettered"
    assert stats["delivered"] == 40


def test_l1_no_retry_storm():
    """With your override the ERP sees (almost) no 429s"""
    stats, _, _ = _replay(stabilise())
    n = stats["status_counts"].get(429, 0)
    assert n <= 5, f"the ERP still returned 429 {n} times; raising max_attempts hides the storm, it doesn't stop it"


def test_l1_service_code_untouched():
    """Stabilising is a settings change: the service files on disk are unchanged"""
    for rel, text in _RELAY_FILES.items():
        with open(_os.path.join(_SERVICE, rel)) as f:
            assert f.read() == text, f"{rel} was edited; stabilise with a settings override, patch in Level 3"


# Level 2: root cause -----------------------------------------------------
def test_l2_points_at_the_right_code():
    """ROOT_CAUSE names the file and function that cause the duplicates"""
    path = str(ROOT_CAUSE.get("file", "")).replace("\\", "/")
    assert path.endswith("relay/keys.py"), "which file decides what the ERP sees as 'the same order'?"
    assert ROOT_CAUSE.get("function") == "idempotency_key"


def test_l2_names_the_release():
    """ROOT_CAUSE names the release that introduced it"""
    assert ROOT_CAUSE.get("introduced_in") == "2.4.0"


def test_l2_duplicated_events_from_the_audit_log():
    """duplicated_events lists every event the ERP invoiced more than once, sorted"""
    got = ROOT_CAUSE.get("duplicated_events")
    want = _truth()["dupes"]
    assert got == want, f"expected {len(want)} event ids from erp_audit.log, got {got!r}"


def test_l2_dead_lettered_events_from_the_relay_log():
    """dead_lettered lists every event the relay gave up on, sorted"""
    got = ROOT_CAUSE.get("dead_lettered")
    want = _truth()["dead"]
    assert got == want, f"expected {len(want)} event ids from relay.log, got {got!r}"


# Level 3: patch with a test ----------------------------------------------
def test_l3_fixed_key_is_stable_and_distinct():
    """fixed_idempotency_key reuses one key per event and never shares it between events"""
    events = _load()["sample_events"].EVENTS
    keys = []
    for e in events:
        k = fixed_idempotency_key(e, 1)
        assert isinstance(k, str) and k, "return a non-empty string"
        assert all(fixed_idempotency_key(e, a) == k for a in range(2, 7)), f"retries of {e['id']} must reuse the key"
        keys.append(k)
    assert len(set(keys)) == len(keys), "two different events got the same key"


def test_l3_fix_alone_stops_duplicates():
    """With the patched key and the original settings, the ERP creates no duplicates"""
    _, dupes, _ = _replay(key_fn=fixed_idempotency_key)
    assert dupes == [], f"still duplicated: {dupes}"


def test_l3_fix_and_override_together():
    """Patch plus override: no duplicates and no dead letters"""
    stats, dupes, _ = _replay(stabilise(), key_fn=fixed_idempotency_key)
    assert dupes == [] and stats["dead_letter"] == []


def _check_result(fn):
    try:
        check_idempotency_key(fn)
        return "pass"
    except AssertionError:
        return "caught"
    except Exception as exc:  # noqa: BLE001
        return f"crashed: {type(exc).__name__}: {exc}"


def test_l3_check_passes_on_the_fix():
    """Your regression check passes on your fixed key"""
    assert _check_result(fixed_idempotency_key) == "pass", "check_idempotency_key must not fail on the fix"


def test_l3_check_catches_the_bug():
    """Your regression check fails (AssertionError) on the 2.4.0 key"""
    buggy = _load()["keys"].idempotency_key
    assert _check_result(buggy) == "caught", "call key_fn for the same event with two attempts and assert the keys match"


def test_l3_check_catches_collisions():
    """Your regression check fails on keys that collide across events"""
    assert _check_result(lambda e, a: "relay") == "caught", "a constant key passes your check"
    assert _check_result(lambda e, a: e["customer"]) == "caught", "use two events with the same customer and different ids"


# Level 4: status update --------------------------------------------------
def test_l4_length():
    """STATUS_UPDATE is a real update: 40 to 180 words"""
    n = len(_status().split())
    assert 40 <= n <= 180, f"{n} words; aim for a short paragraph or a few lines"


def test_l4_when_and_what():
    """It says when it started and which release"""
    t = _status()
    assert "09:12" in t, "say when it started (the deploy time in the logs)"
    assert "2.4.0" in t, "name the release"


def test_l4_impact_numbers():
    """It gives the duplicate and dead-letter counts from the logs"""
    t = _status().lower()
    truth = _truth()
    assert "duplicate" in t and _re.search(rf"\b{truth['extra']}\b", t), "state how many duplicate invoices were created"
    assert "dead" in t and _re.search(rf"\b{len(truth['dead'])}\b", t), "state how many events were dead-lettered"


def test_l4_mitigation():
    """It says what was done to stabilise"""
    t = _status().lower()
    assert "fast_retry" in t and _re.search(r"\b(off|disabled|false)\b", t), "say that fast_retry is off"


def test_l4_cause_and_fix():
    """It explains the cause in one line and the fix with its test"""
    t = _status().lower()
    assert "idempotency" in t and "attempt" in t, "explain that the idempotency key included the attempt number"
    assert _re.search(r"\b(fix|patch)", t) and "test" in t, "say there is a fix and a regression test"


def test_l4_next_update():
    """It commits to a next update time"""
    assert _re.search(r"next update[^.\n]*\b\d{1,2}:\d{2}", _status(), _re.I), "end with 'Next update HH:MM'"


def test_l4_no_false_comfort():
    """It doesn't claim there was no impact or that the cause is unknown"""
    t = _status().lower()
    assert not _re.search(r"no (customer )?impact", t), "there was customer impact"
    assert "unknown" not in t, "you know the root cause; say it"
