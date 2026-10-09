---
title: "Observability and Graceful Degradation"
type: reading
minutes: 20
---

> **By the end of this lesson** you'll be able to say exactly what to log for every Claude call and every agent run, choose the dashboards and alerts that catch silent failures, handle every `stop_reason` (refusals included), and lay out a degradation ladder for when the API is slow, rate-limited or down.

## How this comes up in interviews

The failure-modes stage of a design round is where many candidates run out of things to say (module E6 covers the round's structure). Project deep dives, reported at every lab in this course, often end with "how did you know it was working in production?" (Reported, see module C1). A strong answer is concrete: these fields, these alerts, this ladder of fallbacks, and the one silent failure you'd check for first.

The FDE track's lessons on observability, incidents and circuit breakers cover the basics and are optional background. This lesson focuses on what is specific to LLM calls and on defending the design.

## What to log for every call

One structured log line per API call. Each field answers a question you will be asked during an incident.

| Field | Source | Answers |
|---|---|---|
| `request_id` | `response._request_id`, or the error's request id | "Which call was it?" Support needs this to look at one request |
| `trace_id`, `task_id`, `route` | Your code | "Which user action and which feature?" |
| `model` (requested and served) | Your config, `response.model` | "Did a fallback serve this?" |
| `effort`, `max_tokens`, prompt version | Your config | "Did a config change cause this?" |
| `attempt`, `status` | Your retry wrapper | "Are we retrying our way through an incident?" |
| `ttft_ms`, `total_ms` | Your timer | Latency, split the way users feel it |
| `input_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, `output_tokens` | `response.usage` | Cost, cache health, answer length |
| `stop_reason`, `stop_details.category` | Response | Truncations, refusals, tool turns |
| `completed` | Your validator or grader | Cost per completed task, quality drift |

What **not** to log by default: raw prompts and outputs that contain customer data. Log hashes, lengths and ids, and keep full payloads in a short-retention, access-controlled store for debugging if the customer agrees to it.

For headers you can't get from the parsed object, such as the rate-limit headers, the Python SDK gives you the raw response:

```python
raw = client.messages.with_raw_response.create(**params)
limits = {k: v for k, v in raw.headers.items() if k.startswith("x-ratelimit-")}
message = raw.parse()   # the usual Message
```

## Tracing agents

An agent run is many calls and tool executions that serve one user request. Log each as a **span** under one `trace_id`:

- One span per model call (the fields above) and one per tool execution (tool name, latency, `is_error`, result size).
- Run-level fields: number of turns, total tokens and cost, final `stop_reason`, whether the task completed.
- Turn count is the agent's latency and cost multiplier. A rising average turn count after a prompt change is an early warning, even when every call succeeds.

A trace lets you answer "why did this one take 40 seconds?" in a minute: the trace shows six turns, one tool that took 12 seconds, and a retry on turn four.

## Dashboards and alerts

Build a dashboard per route, and alert on symptoms users or the business would notice:

| Signal | Why it matters | Example alert |
|---|---|---|
| p95 TTFT and total time | The latency budget | p95 TTFT over budget for 10 minutes |
| Error rate by status (429, 5xx, 529, timeouts) | Availability and rate limits | 5xx plus timeouts above 2% of calls |
| Retry rate | Hidden latency and load | Retries above 10% of calls |
| **Cache hit ratio**: `cache_read / (cache_read + cache_creation + input)` | The silent cost failure | Ratio falls by half after a deploy |
| `max_tokens` stop rate | Truncated, wasted answers | Above 1% on a route |
| Refusal rate by category | Policy false positives, or misuse | Doubles day over day |
| Spend per hour against budget | Runaway loops, traffic spikes | Burn rate would exhaust the daily budget early |
| Completion rate (validator or grader pass rate) | Quality | Drops below the launch bar |

The cache hit ratio deserves its own sentence in any interview answer. When someone adds a timestamp or a per-user field to the system prompt, every request still succeeds and nothing errors. Only the bill changes. Alert on the ratio, and keep a test that sends the same request twice and asserts `cache_read_input_tokens > 0` on the second.

## Handle every stop reason

A `200` response isn't a success until you've checked `stop_reason`:

| `stop_reason` | What to do |
|---|---|
| `end_turn` | Normal. Validate the output |
| `tool_use` | Run the tools and send all `tool_result` blocks back in one user message |
| `max_tokens` | The answer is cut off. Don't use it (and never run a truncated tool call). Count it as a failed attempt; fix the output spec or the limit |
| `pause_turn` | A server-side tool loop paused. Append the assistant turn and send the request again to continue |
| `stop_sequence` | Your custom stop sequence fired. Handle it as your design intended |
| `refusal` | The model or a safety classifier declined. Read on |

## Refusals and fallbacks

On current models, safety classifiers can decline a request. A decline is **not** an exception: it arrives as HTTP 200 with `stop_reason: "refusal"` and a `stop_details` object whose `category` names the policy area (`"cyber"`, `"bio"`, `"reasoning_extraction"` and others). Rules to state precisely:

- **Branch on `stop_reason`, not `stop_details`.** `stop_details` is informational and can be `null` even on a refusal.
- **Before or during output.** A decline before any output has empty `content`. A decline mid-stream leaves partial output; discard it rather than treating it as an answer. Refusals count against rate limits; how they are billed depends on the case, and the [refusals documentation](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback) explains it.
- **Opt into fallbacks.** On the Claude API, a server-side fallback re-runs a declined request on another model inside the same call:

```python
response = client.beta.messages.create(
    model="claude-opus-5-5",
    max_tokens=16000,
    betas=["server-side-fallback-2026-07-01"],
    fallbacks="default",                 # Anthropic picks the fallback model by refusal category
    messages=messages,
)
if response.stop_reason == "refusal":
    ...  # every model in the chain declined: show a safe message, log the category
fallback_ran = any(i.type == "fallback_message" for i in (response.usage.iterations or []))
```

What fallbacks don't do matters as much as what they do:

- They trigger on **policy declines only**. Rate limits, overloads and server errors on the requested model are returned as they are. Availability is still your code's job.
- `reasoning_extraction` declines aren't retried on a fallback model.
- If the fallback model is itself rate-limited or overloaded, you get the original refusal back, with `stop_details.recommended_model` as a hint. Size the fallback model's limits for your refusal volume.
- The fallback model runs without Opus 5.5's thinking blocks, and `response.model` names the model that answered. Log it, so quality metrics don't silently mix models.
- The parameter isn't available on the Batches API, Amazon Bedrock, Google Vertex AI or Microsoft Foundry; the SDKs offer a client-side refusal-fallback middleware for those platforms. Claude Haiku 5.5 has no server-side fallback.

## The degradation ladder

When the API is slow or failing, step down a ladder you designed in advance. Each rung trades some quality or freshness for availability:

1. **Bounded retries** with jitter, honoring `retry-after`, inside the caller's deadline (lesson 2).
2. **Another model** for routes where quality allows it. Opus 5.5, Sonnet 5.5 and Haiku 5.5 each have their own rate-limit pool, so a fallback model can have headroom when the primary has none. Expect a cold cache on the fallback.
3. **Defer**: queue the work and finish it later, possibly through the Batch API. Fine for extraction, wrong for chat.
4. **A cheaper answer**: a cached response, a rules-based classifier, a template.
5. **A human**: route to a person with everything gathered so far.

Two safeguards keep the ladder from making an outage worse:

- **A retry budget.** Cap retries at a share of total traffic (say 10%). During a real outage, unbounded retries multiply load on a service that is already struggling.
- **A circuit breaker per model and route.** After repeated dependency failures, stop calling for a cooldown and go straight to the next rung, then probe with a single request. Count API errors and timeouts only. A bug in your own parsing code should page you, not trip the breaker.

**Rate limits are different from outages.** A 429 means you hit your organization's rate limit (requests or tokens per minute). It isn't the same as a 529, which means the API is overloaded. The fixes for a 429 are mostly on your side: honor `retry-after`, read the `x-ratelimit-remaining-*` headers and slow down before you hit zero, shed or defer low-priority work first (batch jobs before interactive users), raise the cache hit rate (on the Claude API, cache reads don't count toward input-token limits on most models), and ask for a higher limit if the steady state needs it. Check [status.anthropic.com](https://status.anthropic.com) before assuming an incident is on Anthropic's side.

Mark every degraded result (`source: "fallback_model"`, `"rules"`, `"deferred"`) so you can measure how often each rung fires and reprocess later.

## Practice (say it out loud)

Original prompts in the style of a design round or project deep dive:

- "Your bill doubled last week and no alert fired. What happened, most likely, and what alert would have caught it?"
- "Opus 5.5 starts returning 529s at peak. Walk me through the next 15 minutes for an invoice-extraction service and for a live chat product. Why are the answers different?"
- "A customer in life sciences reports that some legitimate requests come back empty. How do you diagnose it from your logs, and what do you change?"
- "Draw the spans for one agent run that answers a vendor's question using three tools."

> **Key takeaways**
>
> - Log one structured line per call: request id, trace and route, requested and served model, attempt, TTFT and total time, all four usage meters, stop reason and refusal category, and whether the task completed.
> - Trace agent runs as spans under one id; turn count is the hidden multiplier.
> - Alert on symptoms, and always on the cache hit ratio: cache breakage is silent.
> - Check `stop_reason` before reading content. Refusals are HTTP 200; opt into fallbacks, but they never cover rate limits or outages.
> - Degrade down a planned ladder (retry, another model, defer, cheaper answer, human) with a retry budget and per-route circuit breakers, and mark degraded results.
