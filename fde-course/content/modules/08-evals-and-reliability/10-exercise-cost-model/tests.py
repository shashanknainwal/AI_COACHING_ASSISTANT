import anthropic
from anthropic import _sim
from fde_datasets import brightway


class U:
    def __init__(self, input_tokens=0, output_tokens=0, cache_creation_input_tokens=0, cache_read_input_tokens=0):
        self.input_tokens, self.output_tokens = input_tokens, output_tokens
        self.cache_creation_input_tokens, self.cache_read_input_tokens = cache_creation_input_tokens, cache_read_input_tokens


def _fresh():
    _sim.calls.clear()
    _sim._queue.clear()
    _sim._cache.clear()


def test_request_cost():
    """request_cost() prices all four token types per model"""
    u = U(input_tokens=200, output_tokens=120, cache_creation_input_tokens=3000)
    assert request_cost("claude-sonnet-5-5", u) == 0.0091, f"got {request_cost('claude-sonnet-5-5', u)}"
    u = U(input_tokens=200, output_tokens=120, cache_read_input_tokens=3000)
    assert request_cost("claude-sonnet-5-5", u) == 0.0019
    assert request_cost("claude-opus-5-5", U(input_tokens=1_000_000)) == 4.0
    assert request_cost("claude-haiku-4-5", U(output_tokens=1000, cache_read_input_tokens=10_000)) == 0.006


def test_request_cost_batch_and_unknown():
    """Batch halves the cost; unknown models raise ValueError"""
    u = U(input_tokens=1000, output_tokens=500)
    assert request_cost("claude-opus-5-5", u, batch=True) == 0.007
    try:
        request_cost("gpt-9", u)
    except ValueError as e:
        assert str(e) == "no prices for gpt-9", f"message: {e}"
    else:
        raise AssertionError("unknown models should raise ValueError")


def test_measure():
    """measure() runs every ticket and prices the real usage"""
    _fresh()
    c = anthropic.Anthropic()
    expected = 0.0
    for t in brightway.EVAL_TICKETS:
        u = triage_cached(c, t["text"]).usage
        expected += (u.input_tokens * 2 + u.cache_creation_input_tokens * 2.5 + u.cache_read_input_tokens * 0.1
                     + u.output_tokens * 10) / 1e6
    _fresh()
    got = measure(c, brightway.EVAL_TICKETS)
    assert set(got) == {"requests", "total_cost", "per_request", "cache_hit_rate"}, f"keys: {set(got)}"
    assert got["requests"] == 20 and len(_sim.calls) == 20, "one request per ticket"
    assert abs(got["total_cost"] - expected) < 2e-5, f"total {got['total_cost']} vs {expected:.6f}"
    assert abs(got["per_request"] - expected / 20) < 2e-6
    assert got["cache_hit_rate"] == 0.95, "the first request writes the cache; the other 19 read it"


def test_monthly_cost():
    """monthly_cost() projects cost with caching, batching and days"""
    assert monthly_cost("claude-sonnet-5-5", 5000, 3200, 120) == 1140.0
    assert monthly_cost("claude-sonnet-5-5", 5000, 3200, 120, cached_tokens=3000, cache_hit_rate=0.95) == 339.0
    assert monthly_cost("claude-sonnet-5-5", 5000, 3200, 120, cached_tokens=3000, cache_hit_rate=0.95, batch=True) == 169.5
    assert monthly_cost("claude-opus-5-5", 1000, 2000, 500, days=1) == 18.0
    assert monthly_cost("claude-haiku-4-5", 100, 5000, 100, cached_tokens=5000, cache_hit_rate=0.0) == 20.25, \
        "a 0% hit rate pays the cache-write price on every request"


def test_cheapest_passing():
    """cheapest_passing() picks the lowest-cost option that meets the quality bar"""
    opts = [
        {"name": "big", "pass_rate": 0.95, "params": {"model": "claude-opus-5-5", "requests_per_day": 1000,
                                                      "input_tokens": 2000, "output_tokens": 300}},
        {"name": "mid", "pass_rate": 0.92, "params": {"model": "claude-sonnet-5-5", "requests_per_day": 1000,
                                                      "input_tokens": 2000, "output_tokens": 300}},
        {"name": "small", "pass_rate": 0.80, "params": {"model": "claude-haiku-4-5", "requests_per_day": 1000,
                                                        "input_tokens": 2000, "output_tokens": 300}},
    ]
    assert cheapest_passing(opts, 0.92) == {"choice": {"name": "mid", "monthly_cost": 210.0}, "rejected": ["small"]}
    assert cheapest_passing(opts, 0.95) == {"choice": {"name": "big", "monthly_cost": 420.0}, "rejected": ["mid", "small"]}
    assert cheapest_passing(opts, 0.99) == {"choice": None, "rejected": ["big", "mid", "small"]}
