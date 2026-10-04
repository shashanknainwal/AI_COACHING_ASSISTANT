import anthropic
import fde_clock
from anthropic import _sim


def _fresh():
    _sim.calls.clear()
    _sim._queue.clear()
    _sim._cache.clear()
    fde_clock.sleeps.clear()


def _call(*queued):
    _fresh()
    _sim.queue(*queued)
    return call_claude(make_client(), "Short policy.", "Question?")


def test_make_client():
    """make_client() configures 3 retries and a 60s timeout"""
    c = make_client()
    assert isinstance(c, anthropic.Anthropic), "return an anthropic.Anthropic client"
    assert c.max_retries == 3 and c.timeout == 60.0, f"max_retries={c.max_retries}, timeout={c.timeout}"


def test_cached_system():
    """cached_system() marks the system prompt for caching"""
    assert cached_system("abc") == [{"type": "text", "text": "abc", "cache_control": {"type": "ephemeral"}}]


def test_ok_call():
    """A normal call returns status ok with text, request ID and usage"""
    _fresh()
    r = call_claude(make_client(), "Policy.", "What's the cutoff?")
    assert r["status"] == "ok" and r["text"] == "Wire cutoff is 4pm Eastern on business days.", f"got {r}"
    assert r["request_id"].startswith("req_") and r["usage"].output_tokens > 0
    req = _sim.last_request()
    assert req["system"] == cached_system("Policy.") and req["messages"] == [{"role": "user", "content": "What's the cutoff?"}]
    assert req["model"] == "claude-opus-5-5" and req["max_tokens"] == 4096


def test_transient_errors_are_retried_by_the_sdk():
    """Two server errors then success: the SDK retries, the result is ok"""
    r = _call(_sim.server_error(), _sim.overloaded())
    assert r["status"] == "ok", f"got {r['status']}"
    assert len(_sim.calls) == 3, f"expected 3 attempts (2 retries), got {len(_sim.calls)}"


def test_rate_limited_after_retries():
    """Rate limits on all 4 attempts give status rate_limited, not an exception"""
    r = _call(*[_sim.rate_limit(retry_after=2) for _ in range(4)])
    assert r == {"status": "rate_limited", "text": None, "request_id": r["request_id"], "usage": None}, f"got {r}"
    assert len(_sim.calls) == 4, f"with max_retries=3 the SDK makes 4 attempts; got {len(_sim.calls)}"
    assert fde_clock.sleeps == [2.0, 2.0, 2.0], f"the SDK honors retry-after between attempts; sleeps={fde_clock.sleeps}"


def test_error_statuses():
    """Each error type maps to the right status, checked most specific first"""
    cases = [
        (anthropic.BadRequestError("bad param"), "bad_request", 1),
        (anthropic.AuthenticationError("bad key"), "auth_error", 1),
        (anthropic.NotFoundError("no such model"), "api_error", 1),
    ]
    for exc, status, attempts in cases:
        r = _call(exc)
        assert r["status"] == status, f"{type(exc).__name__} should give {status!r}, got {r['status']!r}"
        assert len(_sim.calls) == attempts, f"{type(exc).__name__} must not be retried"
        assert r["request_id"] == "req_sim_0001", "include the error's request_id"
    r = _call(*[_sim.server_error() for _ in range(4)])
    assert r["status"] == "server_error", f"5xx after retries should be server_error, got {r['status']}"
    r = _call(*[_sim.connection_error() for _ in range(4)])
    assert r["status"] == "connection_error", f"got {r['status']}"


def test_refused_and_truncated():
    """Refusals and truncation are statuses, not exceptions"""
    r = _call(_sim.refusal())
    assert r["status"] == "refused" and r["text"] is None and r["usage"] is not None, f"got {r}"
    r = _call(_sim.message(_sim.text("The cutoff is"), stop_reason="max_tokens"))
    assert r["status"] == "truncated" and r["text"] == "The cutoff is", f"got {r}"


def test_cost_math():
    """cost() prices all four token types"""
    u = anthropic.Usage(input_tokens=1000, output_tokens=500, cache_creation_input_tokens=20000, cache_read_input_tokens=0)
    assert cost(u) == 0.114, f"1000*4 + 20000*5 + 500*20 = 114,000 per million = 0.114; got {cost(u)}"
    u = anthropic.Usage(input_tokens=1000, output_tokens=500, cache_creation_input_tokens=0, cache_read_input_tokens=20000)
    assert cost(u) == 0.018, f"got {cost(u)}"
    assert cost(u, model="claude-sonnet-5-5") == 0.011, f"Sonnet prices: got {cost(u, model='claude-sonnet-5-5')}"


def test_caching_works_end_to_end():
    """The second call with the same long system prompt reads from the cache and costs less"""
    _fresh()
    client = make_client()
    first = call_claude(client, POLICY_MANUAL, "Q1")
    second = call_claude(client, POLICY_MANUAL, "Q2")
    assert first["usage"].cache_creation_input_tokens > 0, "the first call should write the cache (is cache_control set?)"
    assert second["usage"].cache_read_input_tokens > 0, "the second call should read the cache"
    assert cost(second["usage"]) < cost(first["usage"]) / 5, "a cache hit should be much cheaper"
