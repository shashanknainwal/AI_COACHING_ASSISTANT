---
title: "Observability for LLM Systems"
type: reading
minutes: 16
---

> **By the end of this lesson you will be able to:**
> - Use logs, metrics and traces together to answer "what is happening, and why?"
> - Choose what to record for every Claude call, and what never to record
> - Build a dashboard and alerts that catch real problems without paging people for noise
> - Watch quality in production, not only uptime

## The three pillars

| Signal | What it is | Answers |
|---|---|---|
| **Logs** | One structured record per event (JSON lines) | What happened to *this* request? |
| **Metrics** | Numbers aggregated over time (counts, rates, percentiles) | Is the system healthy *overall*? Is it getting worse? |
| **Traces** | The timed steps of one request across services and calls | Where did *this* request spend its time? |

You'll usually start from a metric (the alert fires: p95 latency is up), move to traces and logs (which requests are slow, and what do they have in common?), and finish with a cause.

## Structured logs

Write logs as JSON objects with consistent field names, not prose:

```json
{"ts": 1773004803.2, "level": "info", "service": "triage", "event": "llm_call", "request_id": "req-7f3a",
 "model": "claude-sonnet-5-5", "input_tokens": 212, "cache_read_tokens": 3000, "output_tokens": 118,
 "stop_reason": "end_turn", "latency_ms": 840, "cost_usd": 0.001904, "version": "v1.7.3"}
```

- **A request ID on every line**, passed through every service and call, so one request's story can be reassembled. Also record the API's own request ID (the `request-id` response header, available in the SDK) for support conversations with the provider.
- **The deployed version on every line.** When something changes, you can compare versions directly (you'll do exactly this in the incident exercise).
- **Levels that mean something:** `error` for failed requests, `warning` for degraded but served (truncated output, refusal, fallback used), `info` for normal events.

## What to record for every Claude call

- Model and parameters that matter (effort, max_tokens), and the prompt **version**.
- Token usage: input, output, cache reads and cache writes.
- Latency (and, for streaming, time to first token).
- Stop reason: `end_turn`, `max_tokens`, `refusal`, `tool_use`.
- Cost, computed from usage.
- Errors by type: rate limits (429), overloaded (529), server errors (5xx), timeouts, connection errors.
- For agents: each tool call's name, duration and outcome, and the number of steps.

### What not to record

**By default, don't log prompts or responses.** They contain customer data: names, emails, order details, sometimes health or financial information. Logs are copied widely and kept a long time. Instead:

- Log **metadata** (sizes, tokens, categories, IDs).
- **Redact** personal data from any free text you do log (emails, phone numbers, card numbers).
- If the customer needs conversation records for quality review, store them **separately**, with access control, a retention period and their explicit agreement, not in the general log stream.

## Metrics that matter

The classic "golden signals" for any service, plus LLM-specific ones:

| Signal | LLM-specific version |
|---|---|
| **Traffic** | Requests per minute; tokens per minute (rate limits are often token-based) |
| **Errors** | Error rate by type; refusal rate; fallback rate |
| **Latency** | p50 **and** p95/p99; time to first token for streaming |
| **Saturation** | Distance from rate limits; queue depth |
| **Cost** | Cost per hour and per request; cache hit rate |
| **Quality** | Escalation rate, user thumbs-down, sampled judge scores, `max_tokens` truncations |

Always look at **tail latency** (p95, p99), not just averages or medians. A median can stay flat while one in twenty customers waits ten seconds.

**Cache hit rate deserves its own alert.** A deploy that accidentally puts something variable (a timestamp, a request ID) at the start of the system prompt silently breaks caching: cost jumps, latency rises, and on the Claude API it can also push you into rate limits, because cache reads don't count toward input-token rate limits on most models but uncached input does.

## Alerts people trust

Every alert should be **actionable** and **urgent**. If not, it's a dashboard panel or a ticket, not a page.

- **Alert on symptoms customers feel** (errors, latency, failed tickets), not on every internal cause.
- **Require enough data:** a 33% error rate from 3 requests at 3 a.m. is not an incident. Set a minimum request count.
- **Use windows:** "error rate above 5% for 10 minutes," not a single bad minute.
- **Severity levels:** *page* (wake someone now) vs *ticket* (fix this week).
- **Link a runbook** from every alert: what it means, what to check, how to mitigate (lesson 10).
- **Review alerts regularly:** delete the ones nobody acts on. Alert fatigue makes people ignore the alert that matters.

## Watching quality in production

Uptime isn't enough for LLM features: a system can be fast, error-free and wrong. Add:

- **Sampled grading:** a daily sample of outputs graded by a calibrated judge or a person (Module 8).
- **Behavioral signals:** human overrides (an agent re-routes the ticket), escalations, customer complaints, repeat contacts.
- **Drift checks:** the category mix, input lengths and languages shift over time; compare against the eval set and add new cases.

> **Key takeaways**
> - Metrics tell you something is wrong; traces and structured logs tell you where and why.
> - Log every Claude call's model, prompt version, tokens (including cache), latency, stop reason, cost, errors and request IDs, with the deployed version on every line.
> - Don't log prompts and responses by default; redact personal data in any free text.
> - Track tail latency, error types, cache hit rate, cost and quality signals; alert on customer-facing symptoms with minimum volumes, windows, severities and runbooks.
