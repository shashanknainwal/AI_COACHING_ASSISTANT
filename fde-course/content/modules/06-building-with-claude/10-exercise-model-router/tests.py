import anthropic
from anthropic import _sim


def _fresh():
    _sim.calls.clear()
    _sim._queue.clear()


def test_choose_defaults_and_copy():
    """choose() returns a copy of the task's route"""
    r = choose("extract", 5000)
    assert r == {"model": "claude-opus-5-5", "effort": "medium", "max_tokens": 16000}, f"got {r}"
    r["effort"] = "max"
    assert ROUTES["extract"]["effort"] == "medium", "return a copy; don't modify ROUTES"


def test_choose_fast_path():
    """Tight latency budgets send classification to Haiku 5.5 at low effort"""
    assert choose("classify", 300, 500) == {"model": "claude-haiku-5-5", "effort": "low", "max_tokens": 2048}
    assert choose("classify", 300, 1000)["model"] == "claude-sonnet-5-5", "1000 ms is not under the 1000 ms threshold"
    assert choose("chat", 300, 200)["model"] == "claude-opus-5-5", "the fast path is only for classify"


def test_choose_context_limits():
    """Haiku 5.5 has a 1M window too; inputs over 1M tokens raise for every model"""
    assert choose("classify", 300_000, 500)["model"] == "claude-haiku-5-5", \
        "Haiku 5.5 accepts 1M tokens: no need to move a 300K prompt to Sonnet"
    for task, tokens, budget in [("chat", 1_200_000, None), ("classify", 2_000_000, 500)]:
        try:
            choose(task, tokens, budget)
        except ValueError as e:
            assert str(e) == "input too large", f"message: {str(e)!r}"
        else:
            raise AssertionError(f"{tokens} tokens should raise ValueError('input too large')")


def test_choose_unknown_task():
    """Unknown tasks raise ValueError"""
    try:
        choose("poetry", 10)
    except ValueError as e:
        assert str(e) == "unknown task: poetry"
    else:
        raise AssertionError("expected ValueError for an unknown task")


def test_build_params():
    """build_params() adds output_config only when the route sets an effort"""
    p = build_params({"model": "claude-haiku-5-5", "effort": "low", "max_tokens": 2048}, "S", "U")
    assert p == {"model": "claude-haiku-5-5", "max_tokens": 2048, "system": "S",
                 "messages": [{"role": "user", "content": "U"}], "output_config": {"effort": "low"}}, f"got {p}"
    p = build_params({"model": "claude-sonnet-5-5", "effort": None, "max_tokens": 16000}, "S", "U")
    assert "output_config" not in p, "effort None means 'use the model's default': leave output_config out"


def test_estimate_cost():
    """estimate_cost() uses the route's prices, including Haiku 5.5's long-prompt rate"""
    haiku = {"model": "claude-haiku-5-5", "effort": "low", "max_tokens": 1}
    assert estimate_cost(haiku, 300, 200) == 0.00013, f"got {estimate_cost(haiku, 300, 200)}"
    assert estimate_cost(haiku, 100_000, 200) == 0.0101, "exactly 100K tokens is still the standard rate"
    assert estimate_cost(haiku, 150_000, 200) == 0.0755, \
        f"over 100K prompt tokens the whole request bills at $0.50/$2.50; got {estimate_cost(haiku, 150_000, 200)}"
    assert estimate_cost({"model": "claude-opus-5-5", "effort": "low", "max_tokens": 1}, 250_000, 200) == 1.004


def test_run_routes_to_haiku_with_effort():
    """run() calls Haiku 5.5 with effort low on the fast path"""
    _fresh()
    got = run(anthropic.Anthropic(), "classify", "S", "charged twice", 300, 500)
    assert got == {"text": "[answered by claude-haiku-5-5]", "model": "claude-haiku-5-5", "fallback_used": False}, f"got {got}"
    assert _sim.last_request().get("output_config") == {"effort": "low"}, "Haiku 5.5 supports effort: send low"


def test_run_falls_back_when_overloaded():
    """When Opus stays overloaded through the SDK's retries, run() falls back to Sonnet once"""
    _fresh()
    _sim.queue(_sim.overloaded(), _sim.overloaded(), _sim.overloaded())   # 1 attempt + 2 SDK retries
    got = run(anthropic.Anthropic(), "chat", "S", "hi", 100)
    assert got == {"text": "[answered by claude-sonnet-5-5]", "model": "claude-sonnet-5-5", "fallback_used": True}, f"got {got}"
    assert _sim.last_request()["output_config"] == {"effort": "low"}, "keep the route's effort on the fallback model"


def test_run_without_fallback_reraises():
    """Sonnet has no fallback, so the error is raised"""
    _fresh()
    _sim.queue(_sim.server_error(), _sim.server_error(), _sim.server_error())
    try:
        run(anthropic.Anthropic(), "classify", "S", "x", 100)
    except anthropic.InternalServerError:
        pass
    else:
        raise AssertionError("with no fallback model, re-raise the error")
