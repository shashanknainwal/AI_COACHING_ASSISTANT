---
title: "Observability for LLM Systems"
type: reading
minutes: 6
---

> **By the end of this lesson you will be able to:**
> - Choose what to record for every Claude call, and what never to record
> - Set alerts that catch real problems without noise
> - Watch quality in production, not only uptime

When Jordan Lee messages "triage feels slow today," you need an answer in minutes, from data. It comes from what you chose to record before anything broke.

## Three signals

| Signal | What it is | Answers |
|---|---|---|
| **Logs** | One structured JSON record per event | What happened to *this* request? |
| **Metrics** | Aggregates over time (counts, rates, percentiles) | Is the system healthy overall? Getting worse? |
| **Traces** | Timed steps of one request across calls | Where did *this* request spend its time? |

Start from a metric (p95 alert), move to traces and logs, end at a cause.

## Structured logs

```json
{"ts": 1773004803.2, "level": "info", "service": "triage", "event": "llm_call", "request_id": "req-7f3a",
 "model": "claude-sonnet-5-5", "input_tokens": 212, "cache_read_tokens": 3000, "output_tokens": 118,
 "stop_reason": "end_turn", "latency_ms": 840, "cost_usd": 0.001904, "version": "v1.7.3"}
```

- **Your request ID and the deployed version on every line**, plus the API's `request-id` response header (exposed by the SDK) for provider support cases. The incident exercise depends on the version field.
- **Levels:** `error` = failed, `warning` = degraded but served (truncation, refusal, fallback), `info` = normal.

## What to record for every Claude call

Model, effort, max_tokens, prompt **version**; tokens (input, output, cache reads and writes); latency and time to first token; stop reason; cost; errors by type (429 rate limit, 529 overloaded, other 5xx, timeouts). For agents: each tool call's name, duration and outcome.

**Don't log prompts or responses by default**: they hold customer data, and logs spread widely. Log metadata, redact free text, and keep any agreed conversation records in a separate, access-controlled store with a retention period.

## Metrics that matter

| Signal | LLM version |
|---|---|
| **Traffic** | Requests and tokens per minute |
| **Errors** | Rate by type; refusal rate; fallback rate |
| **Latency** | p50 **and** p95/p99; time to first token |
| **Saturation** | Distance from rate limits; queue depth |
| **Cost** | Per hour and per request; cache hit rate |
| **Quality** | Escalations, thumbs-down, sampled judge scores, `max_tokens` truncations |

Watch **tail latency**: a flat median can hide one customer in twenty waiting ten seconds.

**Alert on cache hit rate.** A timestamp or request ID at the start of the system prompt silently breaks caching: cost and latency jump, and you can hit rate limits, because on the Claude API cache reads don't count toward input-token rate limits on most models but uncached input does.

## Alerts people trust

A page must be **actionable and urgent**; otherwise it's a panel or a ticket. Alert on **symptoms customers feel**, require a **minimum request count** (1 failure in 3 requests at 3 a.m. isn't an incident), use **windows** ("error rate above 5% for 10 minutes"), set **severities** (page vs ticket), **link a runbook** (lesson 10), and delete alerts nobody acts on.

## Quality in production

Fast and error-free can still be wrong. Add sampled grading (Module 8), behavioral signals (overrides, escalations, repeat contacts) and drift checks against your eval set.

> **Key takeaways**
> - Log metadata for every call (version, tokens incl. cache, latency, stop reason, cost, error type, request IDs), not prompts or responses.
> - Track tail latency, error types, cache hit rate, cost and quality.
> - Page only on customer-facing symptoms, with minimum volumes and windows.
