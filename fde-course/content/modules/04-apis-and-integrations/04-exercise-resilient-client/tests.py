import requests
import fde_clock
from requests import _sim

_n = [0]


def _fresh(failures, ok=None):
    """Register a new endpoint that fails as listed, then returns `ok`."""
    _n[0] += 1
    path = f"/v1/test/{_n[0]}"
    body = ok if ok is not None else {"ok": True, "n": _n[0]}
    _sim.route("GET", path, _sim.flaky(lambda req: body, failures))
    _sim.calls.clear()
    fde_clock.sleeps.clear()
    return f"{BASE}{path}", path


def _session():
    return requests.Session()


def test_backoff_delay():
    """backoff_delay() doubles from base and respects the cap"""
    got = [backoff_delay(a) for a in range(1, 8)]
    assert got == [1, 2, 4, 8, 16, 30, 30], f"expected [1, 2, 4, 8, 16, 30, 30], got {got}"
    assert backoff_delay(3, base=0.5, cap=10) == 2.0, "base=0.5, attempt 3 -> 2.0"


def test_retry_after_seconds():
    """retry_after_seconds() parses numbers and ignores missing or date values"""
    assert retry_after_seconds(_sim.respond(429, headers={"Retry-After": "7"})) == 7.0
    assert retry_after_seconds(_sim.respond(503)) is None, "missing header -> None"
    assert retry_after_seconds(_sim.respond(503, headers={"Retry-After": "Wed, 21 Oct 2026 07:28:00 GMT"})) is None, "HTTP-date -> None"


def test_success_first_try():
    """A healthy endpoint: one request, no sleeping, JSON returned"""
    url, path = _fresh([], ok={"id": "S1"})
    got = get_with_retries(_session(), url)
    assert got == {"id": "S1"}, f"expected the JSON body, got {got!r}"
    assert len(_sim.requests_to(path)) == 1 and fde_clock.sleeps == [], f"calls={len(_sim.requests_to(path))}, sleeps={fde_clock.sleeps}"


def test_retries_5xx_with_backoff():
    """503, 502 then success: 3 requests, sleeps of 1s and 2s"""
    url, path = _fresh([503, 502])
    get_with_retries(_session(), url)
    assert len(_sim.requests_to(path)) == 3, f"expected 3 requests, got {len(_sim.requests_to(path))}"
    assert fde_clock.sleeps == [1, 2], f"expected sleeps [1, 2], got {fde_clock.sleeps}"


def test_honors_retry_after():
    """429 with Retry-After: 7 waits 7s, not the backoff delay"""
    url, path = _fresh([(429, {"Retry-After": "7"}), 500])
    get_with_retries(_session(), url)
    assert fde_clock.sleeps == [7.0, 2], f"expected [7.0, 2] (Retry-After, then backoff for attempt 2), got {fde_clock.sleeps}"


def test_retries_timeouts_and_connection_errors():
    """Timeouts and connection errors are retried with backoff"""
    url, path = _fresh(["timeout", "connection"])
    get_with_retries(_session(), url)
    assert len(_sim.requests_to(path)) == 3 and fde_clock.sleeps == [1, 2], f"calls={len(_sim.requests_to(path))}, sleeps={fde_clock.sleeps}"


def test_permanent_errors_not_retried():
    """404 raises HTTPError immediately: one request, no sleep"""
    url, path = _fresh([404])
    try:
        get_with_retries(_session(), url)
    except requests.HTTPError as e:
        assert e.response.status_code == 404
    else:
        raise AssertionError("a 404 should raise requests.HTTPError")
    assert len(_sim.requests_to(path)) == 1 and fde_clock.sleeps == [], "never retry a 404"


def test_gives_up_after_max_attempts():
    """Five 503s: five requests, four sleeps, then HTTPError"""
    url, path = _fresh([503] * 5)
    try:
        get_with_retries(_session(), url)
    except requests.HTTPError as e:
        assert e.response.status_code == 503
    else:
        raise AssertionError("after max_attempts the last error should be raised")
    assert len(_sim.requests_to(path)) == 5, f"expected 5 requests, got {len(_sim.requests_to(path))}"
    assert fde_clock.sleeps == [1, 2, 4, 8], f"no sleep after the final attempt; expected [1, 2, 4, 8], got {fde_clock.sleeps}"


def test_final_timeout_is_raised():
    """If every attempt times out, the Timeout is raised"""
    url, path = _fresh(["timeout"] * 3)
    try:
        get_with_retries(_session(), url, max_attempts=3)
    except requests.Timeout:
        pass
    else:
        raise AssertionError("expected requests.Timeout after 3 timed-out attempts")
    assert fde_clock.sleeps == [1, 2], f"got {fde_clock.sleeps}"


def test_timeout_and_params_on_every_request():
    """Every attempt passes timeout=TIMEOUT and the params"""
    url, path = _fresh([503])
    get_with_retries(_session(), url, params={"fields": "status"})
    calls = _sim.requests_to(path)
    assert len(calls) == 2, f"one 503 then success is 2 requests; got {len(calls)}"
    assert all(c.timeout == TIMEOUT for c in calls), f"timeouts sent: {[c.timeout for c in calls]}"
    assert all(c.params.get("fields") == "status" for c in calls), "pass params on every attempt"
