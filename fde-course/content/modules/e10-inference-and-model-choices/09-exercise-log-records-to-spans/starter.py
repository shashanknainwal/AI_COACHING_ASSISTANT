"""Map Lumenfold's per-call log records onto OpenTelemetry GenAI-style spans."""

PROVIDER = "anthropic"
SERVER = "api.anthropic.com"
APP = "lumenfold"   # namespace for attributes the GenAI conventions don't define


def llm_span(rec):
    """One Claude call (one attempt) -> a span dict."""
    # TODO
    pass


def tool_span(rec):
    """One tool execution -> a span dict."""
    # TODO
    pass


def to_spans(records):
    """All records -> spans sorted by (start_ms, name). Retries of one logical call become ONE span."""
    # TODO
    pass


def cache_hit_rate(spans):
    """Share of input tokens served from cache across successful chat spans (4 dp), or None."""
    # TODO
    pass


# --- Try it out (not graded) ---
RECORDS = [
    {"kind": "llm", "call_id": "c1", "attempt": 0, "trace_id": "t-77", "request_id": "req_01A", "tenant": "harbor-weekly",
     "route": "summarise", "model": "claude-sonnet-5-5", "effort": "low", "max_tokens": 4000, "stream": True,
     "start_ms": 0, "total_ms": 120, "status": "error", "error_type": "overloaded_error",
     "prompt_text": "Summarise: (customer article text)"},
    {"kind": "llm", "call_id": "c1", "attempt": 1, "trace_id": "t-77", "request_id": "req_01B", "tenant": "harbor-weekly",
     "route": "summarise", "model": "claude-sonnet-5-5", "model_served": "claude-sonnet-5-5", "effort": "low",
     "max_tokens": 4000, "stream": True, "start_ms": 900, "total_ms": 2100, "ttft_ms": 420, "status": "ok",
     "input_tokens": 1200, "cache_read_input_tokens": 6000, "cache_creation_input_tokens": 0, "output_tokens": 310,
     "stop_reason": "tool_use", "prompt_text": "Summarise: (customer article text)"},
    {"kind": "tool", "trace_id": "t-77", "tenant": "harbor-weekly", "tool_name": "fetch_related", "tool_use_id": "toolu_9",
     "start_ms": 3010, "total_ms": 85, "status": "ok"},
]
spans = to_spans(RECORDS)
if spans:
    for s in spans:
        print(s["name"], s["kind"], s["status"], s["start_ms"], "->", s["end_ms"])
        for k, v in sorted(s["attributes"].items()):
            print("   ", k, "=", v)
    print("cache hit rate:", cache_hit_rate(spans))
