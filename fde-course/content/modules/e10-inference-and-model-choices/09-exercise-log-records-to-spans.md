---
title: "Exercise: Turn Call Logs into OpenTelemetry Spans"
type: exercise
minutes: 35
hints:
  - "`llm_span`: build the attribute dict first. `gen_ai.usage.input_tokens` is `input_tokens + cache_read_input_tokens + cache_creation_input_tokens`. Add usage, finish reasons and response model only when `status == \"ok\"`; add `error.type` otherwise."
  - "Optional attributes: `gen_ai.request.reasoning.level` only if `effort` is not None; `gen_ai.response.time_to_first_chunk` only if the call streamed and `ttft_ms` is present, converted to seconds. Never copy `prompt_text`."
  - "`tool_span`: the name is `execute_tool <tool_name>`, kind `INTERNAL`, and the tool call id comes from `tool_use_id`."
  - "`to_spans`: group llm records by `call_id`, sort each group by `attempt`, build the span from the LAST attempt, then set `start_ms` from the first attempt and `end_ms` from the latest end. For streaming TTFT, add the gap between the first and last attempt's start to the last attempt's `ttft_ms`."
  - "`cache_hit_rate`: sum `gen_ai.usage.cache_read.input_tokens` and `gen_ai.usage.input_tokens` over CLIENT spans that have usage. Return None when the total is 0."
---

Noor's platform team logs one structured record per Claude call and per tool call, using the schema from E5. Their SRE team runs everything else on OpenTelemetry and wants the LLM calls in the same traces. They want them as spans, with standard attribute names, so the shared dashboards work. Noor's rule: "No customer text leaves our boundary." Noor and Lumenfold are fictional.

You'll write the mapping. It's plain Python that turns log records into span dicts shaped like OTel spans, following the GenAI conventions from the last lesson. No OTel library is needed: in production you'd hand these same names and values to the OTel SDK's span API.

## Your task

**1. `llm_span(rec)`** turns one Claude call record (one attempt) into:

```python
{"name": "chat claude-sonnet-5-5", "kind": "CLIENT", "trace_id": ..., "start_ms": ..., "end_ms": start + total_ms,
 "status": "OK" or "ERROR", "attributes": {...}}
```

Always set these attributes:

- `gen_ai.operation.name` = `"chat"`
- `gen_ai.provider.name` = `"anthropic"`
- `gen_ai.request.model`, `gen_ai.request.max_tokens`, `gen_ai.request.stream`
- `server.address` = `"api.anthropic.com"`
- `lumenfold.request_id`, `lumenfold.tenant`, `lumenfold.route`

Set `gen_ai.request.reasoning.level` only when `effort` isn't `None`.

When `status == "ok"`, also set:

- `gen_ai.response.model` (`model_served`, defaulting to the requested model)
- `gen_ai.usage.input_tokens`: the **total**, including cache reads and writes
- `gen_ai.usage.cache_read.input_tokens`, `gen_ai.usage.cache_write.input_tokens`, `gen_ai.usage.output_tokens`
- `gen_ai.response.finish_reasons` = `[stop_reason]`
- `gen_ai.response.time_to_first_chunk` in seconds, for streaming calls with `ttft_ms`

Otherwise set `error.type` and `"ERROR"`. A `refusal` is a finish reason on a successful (HTTP 200) call, not an error. Never copy `prompt_text`.

**2. `tool_span(rec)`**: name `execute_tool <tool_name>`, kind `INTERNAL`, attributes `gen_ai.operation.name` = `"execute_tool"`, `gen_ai.tool.name`, `gen_ai.tool.call.id` (from `tool_use_id`), `lumenfold.tenant`, and `error.type` when it failed.

**3. `to_spans(records)`**: map every record. LLM records with the same `call_id` are retries of **one** logical call and become **one** span:

- It's built from the last attempt.
- It starts at the first attempt's start and ends at the latest end.
- It gets `lumenfold.attempts` = the number of attempts.
- Its time to first chunk is measured from the first attempt.

An unknown `kind` raises `ValueError`. Return the spans sorted by `(start_ms, name)`.

**4. `cache_hit_rate(spans)`**: cache reads divided by total input tokens over successful chat spans, rounded to 4 decimals, or `None` if there are none.

Press **Run** to see the demo trace (a failed attempt, a retry and a tool call), then **Submit**.

## Defend it

These are original practice questions in the style of a customer call:

- "Our dashboard says cache hit rate is 450%." Someone divided Claude's cache reads by Claude's `input_tokens`, which excludes cached tokens. The convention's total includes them.
- "Why not one span per attempt?" The conventions model the logical operation, which is what the user felt. Attempt detail goes in your own attribute, or in span events if you need each one.
- "Can we turn on prompt capture for debugging?" Only with the customer's sign-off, into a store inside their boundary with short retention. Never by default, and never for a ZDR customer without checking their agreement.
- "The conventions changed names last quarter." They're marked Development. Pin the version you emit and note it in the span's schema URL.
