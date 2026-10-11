import copy

BASE = {"kind": "llm", "call_id": "x1", "attempt": 0, "trace_id": "t-1", "request_id": "req_A", "tenant": "northwind-news",
        "route": "tag", "model": "claude-haiku-5-5", "effort": "medium", "max_tokens": 2000, "stream": False,
        "start_ms": 100, "total_ms": 900, "status": "ok", "input_tokens": 300, "cache_read_input_tokens": 1500,
        "cache_creation_input_tokens": 200, "output_tokens": 80, "stop_reason": "end_turn",
        "prompt_text": "Tag this article: (customer text)"}


def rec(**kw):
    r = copy.deepcopy(BASE)
    r.update(kw)
    return r


def test_llm_span_shape_and_required_attributes():
    """A chat span is named 'chat <model>', is a CLIENT span, and carries the required GenAI attributes"""
    s = llm_span(rec())
    assert s is not None, "llm_span returned None"
    assert s["name"] == "chat claude-haiku-5-5", f"span name is '{{operation}} {{request model}}', got {s['name']!r}"
    assert s["kind"] == "CLIENT" and s["status"] == "OK"
    assert (s["start_ms"], s["end_ms"]) == (100, 1000), "end = start + total_ms"
    a = s["attributes"]
    assert a["gen_ai.operation.name"] == "chat" and a["gen_ai.provider.name"] == "anthropic"
    assert a["gen_ai.request.model"] == "claude-haiku-5-5" and a["gen_ai.response.model"] == "claude-haiku-5-5", \
        "response model defaults to the requested model when model_served is missing"
    assert a["gen_ai.request.max_tokens"] == 2000 and a["gen_ai.request.reasoning.level"] == "medium"
    assert a["gen_ai.request.stream"] is False and a["server.address"] == "api.anthropic.com"
    assert a["lumenfold.request_id"] == "req_A", "keep the request id: support needs it, under your own namespace"


def test_usage_follows_the_convention():
    """gen_ai.usage.input_tokens includes cached tokens; cache reads and writes are reported separately"""
    a = llm_span(rec())["attributes"]
    assert a["gen_ai.usage.input_tokens"] == 2000, \
        "the convention's input total includes cache reads and writes: 300 + 1,500 + 200 = 2,000"
    assert a["gen_ai.usage.cache_read.input_tokens"] == 1500
    assert a["gen_ai.usage.cache_write.input_tokens"] == 200
    assert a["gen_ai.usage.output_tokens"] == 80
    assert a["gen_ai.response.finish_reasons"] == ["end_turn"], "finish reasons is a list"


def test_no_content_and_optional_fields():
    """Prompt text never reaches the span; effort and TTFT appear only when they apply"""
    s = llm_span(rec(effort=None, stream=True, ttft_ms=250))
    assert "Tag this article" not in repr(s), "never export prompt or response text to the tracing backend"
    assert "gen_ai.request.reasoning.level" not in s["attributes"], "no effort sent: leave the attribute out"
    assert s["attributes"]["gen_ai.response.time_to_first_chunk"] == 0.25, "TTFT is in seconds, for streaming calls"
    assert "gen_ai.response.time_to_first_chunk" not in llm_span(rec(ttft_ms=250))["attributes"], \
        "a non-streaming call has no first chunk"


def test_errors_and_refusals():
    """HTTP errors set ERROR and error.type; a refusal is a normal response with its finish reason"""
    e = llm_span(rec(status="error", error_type="rate_limit_error"))
    assert e["status"] == "ERROR" and e["attributes"]["error.type"] == "rate_limit_error"
    assert "gen_ai.usage.input_tokens" not in e["attributes"], "a failed call has no usage to report"
    r = llm_span(rec(stop_reason="refusal"))
    assert r["status"] == "OK", "a refusal arrives as HTTP 200: it's a finish reason, not a span error"
    assert r["attributes"]["gen_ai.response.finish_reasons"] == ["refusal"]


def test_tool_span():
    """Tool executions become INTERNAL 'execute_tool <name>' spans"""
    t = tool_span({"kind": "tool", "trace_id": "t-1", "tenant": "northwind-news", "tool_name": "lookup_taxonomy",
                   "tool_use_id": "toolu_1", "start_ms": 50, "total_ms": 20, "status": "error", "error_type": "timeout"})
    assert t["name"] == "execute_tool lookup_taxonomy" and t["kind"] == "INTERNAL"
    assert t["attributes"]["gen_ai.operation.name"] == "execute_tool"
    assert t["attributes"]["gen_ai.tool.name"] == "lookup_taxonomy" and t["attributes"]["gen_ai.tool.call.id"] == "toolu_1"
    assert t["status"] == "ERROR" and t["attributes"]["error.type"] == "timeout" and t["end_ms"] == 70


def test_retries_become_one_span():
    """Retries of one logical call merge into one span that covers every attempt"""
    recs = [rec(attempt=1, start_ms=700, total_ms=1000, request_id="req_B", stream=True, ttft_ms=300),
            rec(attempt=0, start_ms=100, total_ms=150, status="error", error_type="overloaded_error", request_id="req_A",
                stream=True)]
    spans = to_spans(recs)
    assert spans is not None and len(spans) == 1, f"two attempts of call x1 are one logical operation; got {spans}"
    s = spans[0]
    assert (s["start_ms"], s["end_ms"]) == (100, 1700), "the span runs from the first attempt's start to the last one's end"
    assert s["status"] == "OK" and s["attributes"]["lumenfold.request_id"] == "req_B", "the final attempt decides"
    assert s["attributes"]["lumenfold.attempts"] == 2
    assert s["attributes"]["gen_ai.response.time_to_first_chunk"] == 0.9, \
        "the user waited 600 ms for the failed attempt plus 300 ms: TTFT is measured from the first attempt"


def test_to_spans_orders_and_validates():
    """to_spans() sorts by start time and rejects unknown record kinds"""
    recs = [rec(call_id="b", start_ms=500), rec(call_id="a", start_ms=10),
            {"kind": "tool", "trace_id": "t-1", "tenant": "n", "tool_name": "x", "tool_use_id": "toolu_2",
             "start_ms": 200, "total_ms": 5, "status": "ok"}]
    got = [(s["start_ms"], s["kind"]) for s in to_spans(recs)]
    assert got == [(10, "CLIENT"), (200, "INTERNAL"), (500, "CLIENT")], f"got {got}"
    try:
        to_spans([{"kind": "metric"}])
    except ValueError:
        return
    raise AssertionError("an unknown record kind should raise ValueError")


def test_cache_hit_rate():
    """cache_hit_rate() divides cache reads by total input tokens over successful chat spans"""
    spans = to_spans([rec(call_id="a"), rec(call_id="b", input_tokens=2000, cache_read_input_tokens=0,
                                             cache_creation_input_tokens=0),
                      rec(call_id="c", status="error", error_type="api_error")])
    assert cache_hit_rate(spans) == 0.375, "1,500 cached of 4,000 total input tokens"
    assert cache_hit_rate([]) is None
