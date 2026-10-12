"""Map Lumenfold's per-call log records onto OpenTelemetry GenAI-style spans."""

PROVIDER = "anthropic"
SERVER = "api.anthropic.com"
APP = "lumenfold"   # namespace for attributes the GenAI conventions don't define


def llm_span(rec):
    """One Claude call (one attempt) -> a span dict."""
    usage_in = (rec.get("input_tokens", 0) + rec.get("cache_read_input_tokens", 0)
                + rec.get("cache_creation_input_tokens", 0))
    a = {
        "gen_ai.operation.name": "chat",
        "gen_ai.provider.name": PROVIDER,
        "gen_ai.request.model": rec["model"],
        "gen_ai.request.max_tokens": rec["max_tokens"],
        "gen_ai.request.stream": bool(rec.get("stream", False)),
        "server.address": SERVER,
        f"{APP}.request_id": rec["request_id"],
        f"{APP}.tenant": rec["tenant"],
        f"{APP}.route": rec["route"],
    }
    if rec.get("effort") is not None:
        a["gen_ai.request.reasoning.level"] = rec["effort"]
    if rec["status"] == "ok":
        a["gen_ai.response.model"] = rec.get("model_served", rec["model"])
        a["gen_ai.usage.input_tokens"] = usage_in
        a["gen_ai.usage.cache_read.input_tokens"] = rec.get("cache_read_input_tokens", 0)
        a["gen_ai.usage.cache_write.input_tokens"] = rec.get("cache_creation_input_tokens", 0)
        a["gen_ai.usage.output_tokens"] = rec.get("output_tokens", 0)
        a["gen_ai.response.finish_reasons"] = [rec["stop_reason"]]
        if rec.get("stream") and rec.get("ttft_ms") is not None:
            a["gen_ai.response.time_to_first_chunk"] = rec["ttft_ms"] / 1000
        status = "OK"
    else:
        a["error.type"] = rec["error_type"]
        status = "ERROR"
    return {"name": f"chat {rec['model']}", "kind": "CLIENT", "trace_id": rec["trace_id"],
            "start_ms": rec["start_ms"], "end_ms": rec["start_ms"] + rec["total_ms"],
            "status": status, "attributes": a}


def tool_span(rec):
    """One tool execution -> a span dict."""
    a = {"gen_ai.operation.name": "execute_tool", "gen_ai.tool.name": rec["tool_name"],
         "gen_ai.tool.call.id": rec["tool_use_id"], f"{APP}.tenant": rec["tenant"]}
    if rec["status"] != "ok":
        a["error.type"] = rec["error_type"]
    return {"name": f"execute_tool {rec['tool_name']}", "kind": "INTERNAL", "trace_id": rec["trace_id"],
            "start_ms": rec["start_ms"], "end_ms": rec["start_ms"] + rec["total_ms"],
            "status": "OK" if rec["status"] == "ok" else "ERROR", "attributes": a}


def to_spans(records):
    """All records -> spans sorted by (start_ms, name). Retries of one logical call become ONE span."""
    spans, calls = [], {}
    for rec in records:
        if rec["kind"] == "tool":
            spans.append(tool_span(rec))
        elif rec["kind"] == "llm":
            calls.setdefault(rec["call_id"], []).append(rec)
        else:
            raise ValueError(f"unknown record kind: {rec['kind']}")
    for attempts in calls.values():
        attempts = sorted(attempts, key=lambda r: r["attempt"])
        span = llm_span(attempts[-1])                 # the final attempt decides the outcome
        span["start_ms"] = attempts[0]["start_ms"]     # the span covers every retry
        span["end_ms"] = max(r["start_ms"] + r["total_ms"] for r in attempts)
        span["attributes"][f"{APP}.attempts"] = len(attempts)
        ttft = "gen_ai.response.time_to_first_chunk"
        if ttft in span["attributes"]:               # the user also waited through the failed attempts
            offset = attempts[-1]["start_ms"] - attempts[0]["start_ms"]
            span["attributes"][ttft] = round((offset + attempts[-1]["ttft_ms"]) / 1000, 3)
        spans.append(span)
    return sorted(spans, key=lambda s: (s["start_ms"], s["name"]))


def cache_hit_rate(spans):
    """Share of input tokens served from cache across successful chat spans (4 dp), or None."""
    total = read = 0
    for s in spans:
        a = s["attributes"]
        if s["kind"] == "CLIENT" and "gen_ai.usage.input_tokens" in a:
            total += a["gen_ai.usage.input_tokens"]
            read += a["gen_ai.usage.cache_read.input_tokens"]
    return round(read / total, 4) if total else None


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
