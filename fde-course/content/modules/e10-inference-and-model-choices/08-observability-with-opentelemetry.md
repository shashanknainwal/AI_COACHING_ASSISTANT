---
title: "Observability: Mapping Your LLM Logs onto OpenTelemetry"
type: reading
minutes: 15
---

> **By the end of this lesson** you'll be able to map the per-call log schema from E5 onto OpenTelemetry's GenAI span conventions, describe the categories of tools a customer might plug those spans into without naming a favourite, and say what data-retention arrangements such as zero data retention change in the design.

## The customer question

"We run Datadog" (or Grafana, Honeycomb, New Relic, Splunk, an in-house stack). "How do we see the Claude calls in it?" Every enterprise customer asks this. The vendor-neutral answer is **OpenTelemetry** (OTel): instrument once with OTel, export to whichever backend the customer already pays for. Your job is to know which attributes go on which span, what never leaves the customer's boundary, and where the conventions are still moving.

## Spans in one paragraph

A **trace** is one user action, such as "summarise this article". It is a tree of **spans**. Each span is one timed operation with a name, a kind (`CLIENT` for a call to another service, `INTERNAL` for work inside your process), a start and end time, a status (`OK` or `ERROR`) and **attributes** (key-value pairs). OTel's **semantic conventions** fix the attribute names, so every backend can build the same dashboards.

## The GenAI conventions

OTel has semantic conventions for generative AI. They now live in their own repository (`open-telemetry/semantic-conventions-genai`), and they are marked **Development**, not stable. Attribute names have already changed once: older instrumentations emit `gen_ai.system`, and the current conventions use `gen_ai.provider.name`. Pin the convention version you emit, and check the current spec before you promise a customer specific names.

These are the names as of this writing:

**An inference span** (one call to Claude):

- Name: `{gen_ai.operation.name} {gen_ai.request.model}`, for example `chat claude-sonnet-5-5`. Kind: `CLIENT`.
- Required: `gen_ai.operation.name` (`chat`) and `gen_ai.provider.name` (`anthropic`; there are separate values such as `aws.bedrock` for the cloud platforms).
- `error.type` when the call failed.
- Recommended attributes for your log fields:

| E5 log field | GenAI attribute |
|---|---|
| model requested / served | `gen_ai.request.model` / `gen_ai.response.model` |
| `max_tokens`, `effort` | `gen_ai.request.max_tokens`, `gen_ai.request.reasoning.level` (the exact string you sent) |
| streaming flag | `gen_ai.request.stream` |
| `input_tokens` + cache reads + cache writes | `gen_ai.usage.input_tokens` (the total, **including** cached tokens) |
| `cache_read_input_tokens` | `gen_ai.usage.cache_read.input_tokens` |
| `cache_creation_input_tokens` | `gen_ai.usage.cache_write.input_tokens` |
| `output_tokens` (thinking included) | `gen_ai.usage.output_tokens` |
| `stop_reason` | `gen_ai.response.finish_reasons` (a list) |
| `ttft_ms` | `gen_ai.response.time_to_first_chunk` (in **seconds**, streaming only) |
| message id | `gen_ai.response.id` |

Two details trip people up:

1. **The input total differs from Anthropic's field.** In Claude's `usage`, `input_tokens` counts only the uncached tokens, with cache reads and writes reported separately. The OTel total is the sum of all three. Map it wrongly and every cache-hit-rate dashboard is wrong.
2. **One span per logical call, retries included.** The conventions say a span should cover the whole logical operation, including automatic retries. If your wrapper retries a 529 twice, that's one span lasting the whole time, with the final outcome. Record the attempt count in your own attribute. The user waited through the failed attempts, so measure time to first chunk from the first attempt.

**A tool execution span:** name `execute_tool {gen_ai.tool.name}`, kind `INTERNAL`, with `gen_ai.operation.name` = `execute_tool`, `gen_ai.tool.name` and `gen_ai.tool.call.id` (the `tool_use` block's id). There are also agent-level operations such as `invoke_agent`, so an agent run can be the parent of its model calls and tool calls.

**Your own fields** (tenant, route, prompt version, Anthropic's `request-id` header, the attempt count) go under your own namespace, for example `lumenfold.tenant`. Don't invent `gen_ai.*` names: a future version of the spec may define the same name with a different meaning.

## Content: off by default

The conventions define opt-in attributes for prompts and responses (`gen_ai.input.messages`, `gen_ai.output.messages`, `gen_ai.system_instructions`). Keep them **off** by default. Turning them on copies customer data into a third-party tracing backend, with that backend's retention, access controls and region. If content must be captured for debugging, store it in a short-retention, access-controlled store in the customer's boundary, and put only a reference or a hash on the span.

## Data retention and zero data retention (ZDR)

Some customers have arrangements with Anthropic about how long their API data is retained, including zero data retention. Three things follow for your design:

1. **Your telemetry must not undo it.** A ZDR customer who exports full prompts to a SaaS tracing tool has moved the retention problem, not solved it. Default to metadata-only spans, and get the customer's sign-off before capturing content anywhere.
2. **Some models require retention.** According to the skill's error-code reference, Fable 5, Fable 5.1, Mythos 5 and Mythos 5.1 require data retention of at least 30 days. An organisation or workspace set to ZDR, or to a shorter retention, gets `400 invalid_request_error` on **every** request to those models, even with a valid payload. When a ZDR customer reports "every Fable request 400s", check retention settings before debugging the request body.
3. **Retention terms belong to the agreement, not to you.** Don't tell a customer what their retention is. Ask, and confirm in their agreement and the current docs.

## Where the spans go: tool categories

Stay vendor-neutral. Name categories, and let the customer's existing contracts decide:

| Category | What it answers | Typical inputs |
|---|---|---|
| APM and tracing backends | "Which step of this request was slow? Which service failed?" | OTel traces, metrics |
| LLM observability and eval platforms | "Which prompt version regressed? What do graders say about yesterday's traffic?" | Traces with content (if allowed), eval scores, datasets |
| Log pipelines and SIEM | "Who called what, when? Was anything denied?" | Structured logs, audit events |
| Cost and usage reporting | "What did each team spend?" | Your per-call usage, plus the provider's usage reports |
| Product analytics | "Did users accept the answer?" | Feedback events joined by trace id |

For cost, there's also the provider's own view. The Admin API's usage and cost reports (an Admin API key is needed) group usage by model, workspace, API key and service tier. Per the skill, they don't cover Bedrock, Vertex or Foundry traffic and aren't available on Claude Platform on AWS. Reconcile your span-based totals against them rather than trusting either alone.

## A practical warning about instrumentation

Auto-instrumentation libraries hook into HTTP clients or SDKs. When the SDK changes underneath them, they can go quiet without an error. For example, the Python SDK's 1.x release moved its HTTP layer from `httpx` to `httpx2`, and the skill's upgrade notes warn that OTel instrumentation that patches `httpx` then silently stops seeing SDK traffic. After any SDK upgrade, check that spans still arrive. Better, emit the LLM spans yourself in the wrapper that already logs each call, as you'll do in the next exercise.

> **Key takeaways**
> - Instrument once with OpenTelemetry and export to the customer's existing backend. The GenAI conventions are still in Development, so pin a version and re-check names.
> - `gen_ai.usage.input_tokens` is the total including cached tokens, unlike Claude's `input_tokens`. Cache reads and writes have their own attributes.
> - One span per logical call, covering all retries. Tools get `execute_tool` spans. Your own fields go under your own namespace.
> - Content capture stays off by default. ZDR and retention arrangements must survive your telemetry pipeline.
> - Fable and Mythos models require 30-day retention. A ZDR organisation gets a 400 on every request to them.
