import anthropic
from anthropic import _sim


def _fresh():
    _sim.calls.clear()
    _sim._queue.clear()


class Clock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


def _client():
    return anthropic.Anthropic(max_retries=0)


def test_breaker_opens_after_threshold():
    """The breaker opens after failure_threshold consecutive failures"""
    b = CircuitBreaker(failure_threshold=3, cooldown_s=30, clock=Clock())
    assert b.allow() is True and b.state == "closed"
    b.record_failure(); b.record_failure()
    assert b.state == "closed" and b.allow() is True
    b.record_failure()
    assert b.state == "open" and b.allow() is False, "3 failures open the breaker"


def test_success_resets_the_count():
    """A success resets the failure count (failures must be consecutive)"""
    b = CircuitBreaker(failure_threshold=3, clock=Clock())
    b.record_failure(); b.record_failure(); b.record_success(); b.record_failure(); b.record_failure()
    assert b.state == "closed" and b.failures == 2


def test_half_open_after_cooldown():
    """After the cooldown, one trial is allowed; its result closes or reopens the breaker"""
    clock = Clock()
    b = CircuitBreaker(failure_threshold=2, cooldown_s=30, clock=clock)
    clock.now = 100
    b.record_failure(); b.record_failure()
    assert b.state == "open" and b.opened_at == 100
    clock.now = 129.9
    assert b.allow() is False and b.state == "open"
    clock.now = 130
    assert b.allow() is True and b.state == "half_open", "cooldown passed: half-open"
    b.record_failure()
    assert b.state == "open" and b.opened_at == 130, "a failed trial reopens immediately and restarts the cooldown"
    clock.now = 160
    assert b.allow() is True
    b.record_success()
    assert b.state == "closed" and b.failures == 0 and b.allow() is True


def test_triage_success():
    """triage() returns Claude's result tagged with source claude"""
    _fresh()
    b = CircuitBreaker(clock=Clock())
    got = triage(_client(), b, "Where is B-1001?", flags={"claude_triage": True})
    assert got == {"category": "order_status", "urgency": "normal", "source": "claude"}, f"got {got}"
    assert len(_sim.calls) == 1


def test_triage_falls_back_and_opens():
    """API errors fall back to rules; once open, Claude isn't called at all"""
    _fresh()
    _sim.queue(_sim.overloaded(), anthropic.APIConnectionError("connection reset"), _sim.rate_limit())
    b = CircuitBreaker(failure_threshold=3, clock=Clock())
    flags = {"claude_triage": True}
    sources = [triage(_client(), b, "I was charged twice", flags=flags)["source"] for _ in range(3)]
    assert sources == ["fallback"] * 3 and b.state == "open", f"sources {sources}, state {b.state}"
    got = triage(_client(), b, "I was charged twice", flags=flags)
    assert got == {"category": "billing", "urgency": "normal", "source": "circuit_open"}, f"got {got}"
    assert len(_sim.calls) == 3, "an open breaker must not call the API"


def test_non_api_errors_are_not_swallowed():
    """Bugs in your own code still raise; only anthropic.APIError falls back"""
    _fresh()
    _sim.queue("not json at all")
    try:
        triage(_client(), CircuitBreaker(clock=Clock()), "Where is it?", flags={"claude_triage": True})
    except ValueError:
        pass
    else:
        raise AssertionError("a JSON bug should surface, not be hidden by the fallback")


def test_kill_switch():
    """With the flag off, triage() uses rules and never calls Claude"""
    _fresh()
    got = triage(_client(), CircuitBreaker(clock=Clock()), "my vase arrived cracked", flags={"claude_triage": False})
    assert got == {"category": "damaged_item", "urgency": "normal", "source": "disabled"} and len(_sim.calls) == 0
    got = triage(_client(), CircuitBreaker(clock=Clock()), "my vase arrived cracked", flags={})
    assert got["source"] == "disabled", "a missing flag means off (fail safe)"
