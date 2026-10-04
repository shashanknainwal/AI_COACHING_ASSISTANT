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
    """Tight latency budgets send classification to the fast model without effort"""
    assert choose("classify", 300, 500) == {"model": "claude-haiku-4-5", "effort": None, "max_tokens": 1024}
    assert choose("classify", 300, 1000)["model"] == "claude-sonnet-5-5", "1000 ms is not under the 1000 ms threshold"
    assert choose("chat", 300, 200)["model"] == "claude-opus-5-5", "the fast path is only for classify"


def test_choose_context_limits():
    """Inputs too large for Haiku move to Sonnet; inputs too large for everything raise"""
    assert choose("classify", 300_000, 500) == {"model": "claude-sonnet-5-5", "effort": "low", "max_tokens": 1024}
    for task, tokens in [("chat", 1_200_000), ("classify", 2_000_000)]:
        try:
            choose(task, tokens)
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
    """build_params() adds output_config only when there's an effort"""
    p = build_params({"model": "claude-opus-5-5", "effort": "low", "max_tokens": 16000}, "S", "U")
    assert p == {"model": "claude-opus-5-5", "max_tokens": 16000, "system": "S",
                 "messages": [{"role": "user", "content": "U"}], "output_config": {"effort": "low"}}, f"got {p}"
    p = build_params({"model": "claude-haiku-4-5", "effort": None, "max_tokens": 1024}, "S", "U")
    assert "output_config" not in p, "Haiku rejects the effort parameter: leave output_config out"


def test_estimate_cost():
    """estimate_cost() uses the route's model prices"""
    assert estimate_cost({"model": "claude-haiku-4-5", "effort": None, "max_tokens": 1}, 300, 200) == 0.0013
    assert estimate_cost({"model": "claude-opus-5-5", "effort": "low", "max_tokens": 1}, 250_000, 200) == 1.004


def test_run_routes_and_haiku_works():
    """run() calls the chosen model with valid parameters (Haiku included)"""
    _fresh()
    got = run(anthropic.Anthropic(), "classify", "S", "charged twice", 300, 500)
    assert got == {"text": "[answered by claude-haiku-4-5]", "model": "claude-haiku-4-5", "fallback_used": False}, f"got {got}"
    assert "output_config" not in _sim.last_request(), "no effort for Haiku (the API would return a 400)"


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
