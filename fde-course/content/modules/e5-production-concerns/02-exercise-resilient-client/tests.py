import anthropic
import fde_clock
from anthropic import _sim

PARAMS = {
    "model": "claude-opus-5-5",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "Extract the invoice fields."}],
}
ONE = lambda: 1.0  # noqa: E731 - rand() that always returns the top of the jitter range


class _SpyClient:
    """Wraps the simulated client and records every with_options(...) call."""

    def __init__(self):
        self._inner = anthropic.Anthropic()
        self.messages = self._inner.messages
        self.options = []

    def with_options(self, **kwargs):
        self.options.append(kwargs)
        return self._inner.with_options(**kwargs)


def _fresh():
    _sim.calls.clear()
    _sim._queue.clear()
    fde_clock.reset()
    return _SpyClient()


def _rate_limit(seconds, rid):
    return anthropic.RateLimitError("Error code: 429", headers={"retry-after": str(seconds)}, request_id=rid)


def test_is_retryable():
    """is_retryable() separates transient errors from ones a retry can't fix"""
    yes = [
        anthropic.RateLimitError("429"),
        anthropic.InternalServerError("500"),
        anthropic.OverloadedError("529"),
        anthropic.APIStatusError("408", status_code=408),
        anthropic.APIStatusError("409", status_code=409),
        anthropic.APIStatusError("503", status_code=503),
        anthropic.APIConnectionError(),
        anthropic.APITimeoutError(),
    ]
    no = [
        anthropic.BadRequestError("400"),
        anthropic.AuthenticationError("401"),
        anthropic.PermissionDeniedError("403"),
        anthropic.NotFoundError("404"),
        anthropic.APIStatusError("413", status_code=413),
        ValueError("a bug in our own code"),
    ]
    for exc in yes:
        assert is_retryable(exc) is True, f"{type(exc).__name__} ({getattr(exc, 'status_code', '-')}) should be retryable"
    for exc in no:
        assert is_retryable(exc) is False, f"{type(exc).__name__} ({getattr(exc, 'status_code', '-')}) should not be retried"


def test_retry_after_seconds():
    """retry_after_seconds() reads the header and ignores values it can't trust"""
    assert retry_after_seconds(_rate_limit(7, "r")) == 7.0, "read exc.response.headers.get(\"retry-after\") and return it as a float"
    assert retry_after_seconds(_rate_limit("1.5", "r")) == 1.5, "fractional seconds are allowed"
    assert retry_after_seconds(anthropic.RateLimitError("429")) is None, "no header: None"
    assert retry_after_seconds(_rate_limit("soon", "r")) is None, "unparseable header: None"
    assert retry_after_seconds(_rate_limit(-3, "r")) is None, "negative header: None"
    assert retry_after_seconds(anthropic.APIConnectionError()) is None, "connection errors have no response: None"


def test_backoff_delay():
    """backoff_delay() doubles from base, caps, applies full jitter and defers to retry-after"""
    got = [backoff_delay(n, rand=ONE) for n in range(6)]
    assert got == [1.0, 2.0, 4.0, 8.0, 16.0, 20.0], f"with rand()=1.0 expected 1, 2, 4, 8, 16, then the 20s cap; got {got}"
    assert backoff_delay(2, rand=lambda: 0.25) == 1.0, "full jitter: rand() * min(cap, base * 2**attempt)"
    assert backoff_delay(3, retry_after=7, rand=ONE) == 7.0, "retry-after wins over the computed backoff"
    assert backoff_delay(0, retry_after=0, rand=ONE) == 0.0, "retry-after of 0 means retry now (0 is not None)"
    assert backoff_delay(4, base=0.5, cap=3.0, rand=ONE) == 3.0, "respect the base and cap arguments"


def test_success_first_try():
    """A healthy call goes out once, with SDK retries off and the attempt timeout set"""
    client = _fresh()
    _sim.queue("ok")
    log = []
    response = call_with_retries(client, PARAMS, log=log)
    assert response is not None and response.content[0].text == "ok", "return the Message from messages.create"
    assert len(_sim.calls) == 1, f"expected 1 request, saw {len(_sim.calls)}"
    assert client.options and client.options[0].get("max_retries") == 0, \
        "call client.with_options(max_retries=0, ...) so the SDK's own retries don't multiply yours"
    assert abs(client.options[0].get("timeout", 0) - 30.0) < 0.01, f"first attempt timeout should be 30.0, got {client.options[0]}"
    assert log == [{"attempt": 1, "status": 200, "request_id": response._request_id, "wait": None}], f"log was {log}"
    assert fde_clock.sleeps == [], "no sleeping when nothing failed"


def test_retries_transient_errors_with_backoff():
    """Overloaded and 5xx errors are retried with exponential backoff, and every request id is logged"""
    client = _fresh()
    _sim.queue(anthropic.OverloadedError("529", request_id="req_A"),
               anthropic.InternalServerError("500", request_id="req_B"),
               "done")
    log = []
    response = call_with_retries(client, PARAMS, rand=ONE, log=log)
    assert response is not None and response.content[0].text == "done", "retry the 529 and the 500, then return the answer"
    assert len(_sim.calls) == 3, f"expected 3 attempts, saw {len(_sim.calls)}"
    assert fde_clock.sleeps == [1.0, 2.0], f"expected sleeps [1.0, 2.0], got {fde_clock.sleeps}"
    assert [e["status"] for e in log] == [529, 500, 200], f"statuses: {[e['status'] for e in log]}"
    assert [e["request_id"] for e in log][:2] == ["req_A", "req_B"], "log the request id of each failed attempt"
    assert [e["wait"] for e in log] == [1.0, 2.0, None], f"waits: {[e['wait'] for e in log]}"
    assert [e["attempt"] for e in log] == [1, 2, 3]


def test_honors_retry_after():
    """A 429 waits exactly as long as retry-after says"""
    client = _fresh()
    _sim.queue(_rate_limit(7, "req_R"), "done")
    log = []
    call_with_retries(client, PARAMS, rand=ONE, log=log)
    assert fde_clock.sleeps == [7.0], f"expected one 7s wait from retry-after, got {fde_clock.sleeps}"
    assert log[0] == {"attempt": 1, "status": 429, "request_id": "req_R", "wait": 7.0}, f"got {log[0]}"


def test_non_retryable_raises_immediately():
    """A 400 is raised on the first attempt, with no sleeping"""
    client = _fresh()
    _sim.queue(anthropic.BadRequestError("messages: Field required", request_id="req_400"))
    log = []
    try:
        call_with_retries(client, PARAMS, rand=ONE, log=log)
    except anthropic.BadRequestError:
        pass
    else:
        raise AssertionError("re-raise the BadRequestError so the caller sees it")
    assert len(_sim.calls) == 1 and fde_clock.sleeps == [], "never retry a 400"
    assert log == [{"attempt": 1, "status": 400, "request_id": "req_400", "wait": None}], f"log was {log}"


def test_gives_up_after_max_attempts():
    """After max_attempts transient failures, the last error is raised"""
    client = _fresh()
    _sim.queue(*[anthropic.OverloadedError("529", request_id=f"req_{i}") for i in range(4)])
    log = []
    try:
        call_with_retries(client, PARAMS, max_attempts=4, rand=ONE, log=log)
    except anthropic.APIStatusError as exc:
        assert exc.status_code == 529 and exc.request_id == "req_3", "raise the error from the last attempt"
    else:
        raise AssertionError("raise once every attempt has failed")
    assert len(_sim.calls) == 4, f"expected 4 attempts, saw {len(_sim.calls)}"
    assert fde_clock.sleeps == [1.0, 2.0, 4.0], f"no sleep after the final attempt; got {fde_clock.sleeps}"
    assert log[-1]["wait"] is None


def test_respects_deadline():
    """If waiting would pass the deadline, give up now instead of sleeping"""
    client = _fresh()
    _sim.queue(_rate_limit(20, "req_1"), _rate_limit(20, "req_2"), "too late")
    log = []
    try:
        call_with_retries(client, PARAMS, deadline_s=30.0, rand=ONE, log=log)
    except anthropic.RateLimitError as exc:
        assert exc.request_id == "req_2"
    else:
        raise AssertionError("a second 20s wait would end at 40s, past the 30s deadline: raise the RateLimitError")
    assert len(_sim.calls) == 2, f"expected 2 attempts, saw {len(_sim.calls)}"
    assert fde_clock.sleeps == [20.0], f"got {fde_clock.sleeps}"
    second_timeout = client.options[1].get("timeout", 0)
    assert abs(second_timeout - 10.0) < 0.05, \
        f"the second attempt only has about 10s of the 30s deadline left; its timeout should be ~10, got {second_timeout}"


def test_connection_errors_and_timeouts():
    """Timeouts and dropped connections are retried and logged by name"""
    client = _fresh()
    _sim.queue(anthropic.APITimeoutError(), anthropic.APIConnectionError(), "done")
    log = []
    call_with_retries(client, PARAMS, rand=ONE, log=log)
    assert [e["status"] for e in log] == ["timeout", "connection", 200], f"statuses: {[e['status'] for e in log]}"
    assert log[0]["request_id"] is None and log[1]["request_id"] is None, "no response, so no request id"
    assert fde_clock.sleeps == [1.0, 2.0]
