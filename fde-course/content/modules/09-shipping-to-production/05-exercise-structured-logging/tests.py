import json
import anthropic
from anthropic import _sim


def _fresh():
    _sim.calls.clear()
    _sim._queue.clear()


def _ticks(*values):
    it = iter(values)
    return lambda: next(it)


def _params(content="Where is B-1001?", max_tokens=1024):
    return {"model": "claude-sonnet-5-5", "max_tokens": max_tokens, "messages": [{"role": "user", "content": content}]}


def test_redact():
    """redact() removes emails, card numbers and phone numbers, nothing else"""
    got = redact("maya.o+shop@example.co.uk paid with 4111 1111 1111 1111, call (415) 555-0134")
    assert got == "[email] paid with [card], call [phone]", f"got {got!r}"
    assert redact("card 4111-1111-1111-1111, phone 415.555.0134") == "card [card], phone [phone]"
    keep = "Order B-1001 for $1249.00, shipment SHP-1003, zip 94110"
    assert redact(keep) == keep, "order IDs, amounts and zip codes are not personal data"


def test_logger_line_format():
    """log() writes one JSON line with ts, level, service, event and fields"""
    logger = JsonLogger("triage", clock=lambda: 1700000000.12345)
    line = logger.log("info", "ticket_received", request_id="r1", channel="email", attempt=2)
    assert isinstance(line, str) and logger.lines == [line], "append the line to logger.lines and return it"
    assert json.loads(line) == {"ts": 1700000000.123, "level": "info", "service": "triage", "event": "ticket_received",
                                "request_id": "r1", "channel": "email", "attempt": 2}, f"got {line}"
    assert line == json.dumps(json.loads(line), sort_keys=True), "use sorted keys so lines are stable and diffable"


def test_logger_redacts_strings():
    """String fields are redacted before they're written"""
    logger = JsonLogger("triage", clock=lambda: 0)
    logger.log("info", "note", text="email me: a@b.com", count=4111111111111111)
    record = json.loads(logger.lines[0])
    assert record["text"] == "email me: [email]" and record["count"] == 4111111111111111, "only string values are redacted"


def test_logged_create_success():
    """logged_create() logs model, tokens, latency and cost, and returns the response"""
    _fresh()
    logger = JsonLogger("triage", clock=lambda: 5.0)
    response = logged_create(anthropic.Anthropic(max_retries=0), logger, "req-1", clock=_ticks(10.0, 10.84), **_params())
    assert response is not None and response.stop_reason == "end_turn", "return the response"
    assert len(logger.lines) == 1, "exactly one log line per call"
    rec = json.loads(logger.lines[0])
    u = response.usage
    assert rec == {"ts": 5.0, "level": "info", "service": "triage", "event": "llm_call", "request_id": "req-1",
                   "model": "claude-sonnet-5-5", "stop_reason": "end_turn", "input_tokens": u.input_tokens,
                   "output_tokens": u.output_tokens, "cache_read_tokens": 0, "cache_write_tokens": 0,
                   "latency_ms": 840, "cost_usd": call_cost("claude-sonnet-5-5", u)}, f"got {rec}"


def test_no_prompt_or_output_in_logs():
    """Prompt and response text never reach the logs"""
    _fresh()
    logger = JsonLogger("triage", clock=lambda: 0)
    secret = "My SSN is 123-45-6789 and I live at 12 Elm St"
    logged_create(anthropic.Anthropic(max_retries=0), logger, "req-2", clock=_ticks(0, 1), **_params(content=secret))
    assert "Elm St" not in logger.lines[0] and "order_status" not in logger.lines[0], \
        "log metadata (tokens, latency, cost), not the conversation"


def test_warning_on_truncation():
    """max_tokens and refusal stop reasons are logged as warnings"""
    _fresh()
    _sim.queue("x" * 400)
    logger = JsonLogger("triage", clock=lambda: 0)
    logged_create(anthropic.Anthropic(max_retries=0), logger, "req-3", clock=_ticks(0, 1), **_params(max_tokens=10))
    rec = json.loads(logger.lines[0])
    assert rec["stop_reason"] == "max_tokens" and rec["level"] == "warning", f"got {rec}"


def test_logged_create_error():
    """API errors are logged as llm_error and re-raised"""
    _fresh()
    _sim.queue(_sim.overloaded())
    logger = JsonLogger("triage", clock=lambda: 7.0)
    try:
        logged_create(anthropic.Anthropic(max_retries=0), logger, "req-4", clock=_ticks(1.0, 31.0), **_params())
    except anthropic.OverloadedError:
        pass
    else:
        raise AssertionError("re-raise the error so the caller can handle it")
    assert [json.loads(l) for l in logger.lines] == [{"ts": 7.0, "level": "error", "service": "triage", "event": "llm_error",
                                                      "request_id": "req-4", "model": "claude-sonnet-5-5",
                                                      "error_type": "OverloadedError", "latency_ms": 30000}], f"got {logger.lines}"
