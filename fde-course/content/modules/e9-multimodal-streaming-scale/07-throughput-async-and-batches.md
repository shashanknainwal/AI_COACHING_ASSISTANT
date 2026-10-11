---
title: "Throughput at Scale: Async Clients, Rate Limits and Batches"
type: reading
minutes: 16
---

> **By the end of this lesson** you'll be able to choose between synchronous calls, an async worker pool and the Message Batches API for a backlog, size concurrency from a throughput target, handle 429s without making them worse, and run a batch job end to end, including where Batches isn't available.

## The backfill question

Every customer eventually says some version of: "We have 50,000 old tickets (or 120,000 archived purchase orders). Can we run them all through this by Monday?" Tallowmere wants three years of order-desk emails labelled by intent to train its routing rules. Three ways to do it:

| Approach | Latency per item | Cost | Use when |
|---|---|---|---|
| Synchronous loop | Seconds each, one at a time | Standard price | Never for a backlog. 50,000 x 3 s is 42 hours |
| **Async worker pool** | Seconds each, N at a time | Standard price | The answers are needed within minutes or hours, the work has follow-up steps (tool loops), or Batches isn't available on the customer's platform |
| **Message Batches API** | Most batches finish in under an hour; up to 24 hours | **50% off** every token | Nobody is waiting on any single answer |

## Async with a bounded pool

The Python SDK has `AsyncAnthropic` with the same methods as the sync client, awaited:

```python
import asyncio
import anthropic

client = anthropic.AsyncAnthropic(max_retries=0)    # this code owns retries, see below
limit = asyncio.Semaphore(16)

async def classify(email):
    async with limit:                                # at most 16 requests in flight
        resp = await client.messages.create(
            model="claude-haiku-5-5",
            max_tokens=1024,                         # thinking counts toward max_tokens
            output_config={"effort": "low"},
            messages=[{"role": "user", "content": email}],
        )
    return next(b.text for b in resp.content if b.type == "text")

async def main(emails):
    return await asyncio.gather(*(classify(e) for e in emails))

labels = asyncio.run(main(emails))
```

For heavy async workloads the SDK docs suggest the aiohttp backend (`anthropic[aiohttp]`, `DefaultAioHttpClient`). The pattern above is what matters: **`gather` creates the work, the semaphore caps how much of it runs at once.** An unbounded `gather` over 50,000 items opens 50,000 requests and gets a wall of 429s.

**Sizing the pool.** Throughput is roughly concurrency divided by latency (Little's law). To finish 50,000 items in one hour you need about 14 requests per second. At about 3 seconds per request (including thinking at `effort: "low"`) that's about 42 in flight. Then check that against your organization's **rate limits**: requests per minute and input and output tokens per minute, per model, which depend on your usage tier. Look them up in the Console; don't guess them in a design review.

## 429s without a retry storm

A 429 `rate_limit_error` means you exceeded requests or tokens per minute. The response carries a `retry-after` header with the seconds to wait (Official, error docs). The SDK retries 429, 408, 409 and 5xx with exponential backoff by default (`max_retries=2`).

At scale, decide who owns retries:

- **One retry layer.** If your pool retries and the SDK also retries, one failure can become nine calls. Set `max_retries=0` on the client when your code retries, or keep the SDK's retries and don't add your own.
- **Honour `retry-after`.** It's the server telling you when capacity returns. Fall back to exponential backoff with jitter when it's absent.
- **Release your slot while you wait.** A task that sleeps inside the semaphore blocks a healthy request from running.
- **Never retry a 400.** A bad request is bad every time. Record it and move on.
- **Cap attempts** and report what failed with its request ID, rather than looping forever.

A fixed-rhythm retry from many workers (everyone sleeps 1 second, everyone retries together) is how a brief overload becomes an outage. E5's resilient client covers the single-request version; the next exercise is the pool version.

## Message Batches, end to end

```python
batch = client.messages.batches.create(requests=[
    {"custom_id": "email-000123",
     "params": {"model": "claude-haiku-5-5", "max_tokens": 1024,
                "output_config": {"effort": "low"},
                "messages": [{"role": "user", "content": email_text}]}},
    # ... up to 100,000 requests
])
while client.messages.batches.retrieve(batch.id).processing_status != "ended":
    time.sleep(60)
for result in client.messages.batches.results(batch.id):
    ...  # result.custom_id, result.result.type
```

Facts to know (Official, batch processing docs, checked 2026-10-11):

- **Size:** up to 100,000 requests or 256 MB per batch, whichever comes first.
- **Timing:** most batches finish within an hour. Results are available when every request has finished or after 24 hours, whichever is first. Requests not processed within 24 hours **expire**. Results stay downloadable for 29 days.
- **Price:** 50% of standard prices on all usage. Batch and caching discounts stack, but cache hits inside a batch are best-effort (the docs cite 30% to 98%); the 1-hour cache TTL helps because batches can outlast 5 minutes.
- **Results come back in any order.** Match them with `custom_id` (1 to 64 characters, letters, digits, `-` and `_` only). Don't use raw business IDs like `PO#4471/2`; map them.
- **Four result types:** `succeeded`, `errored`, `canceled`, `expired`. You aren't billed for errored, canceled or expired requests. For `errored`, `result.error.error.type` tells you whether to fix the request (`invalid_request_error`) or simply retry it (server errors).
- **Validation is asynchronous.** A malformed `params` object comes back as an errored result when the whole batch ends, not at create time. Test the request shape with one normal Messages call first.
- **Not allowed in a batch:** `stream: true`, `speed` (fast mode), `max_tokens: 0`, and the server-side `fallbacks` parameter (a batch item with it comes back errored).
- **Mixed requests are fine.** Vision, PDFs, tools, system prompts and multi-turn conversations can all be batched; each request runs independently, so there's no tool loop inside a batch.

**Availability:** Message Batches runs on the Claude API and Claude Platform on AWS. It is **not available on Amazon Bedrock, Google Vertex AI or Microsoft Foundry**. A customer on one of those platforms gets the async pool, not the discount. Say this early in a design discussion: it can change the cost estimate by half.

## Worked example: the backfill bill

Tallowmere's 50,000 emails on Claude Haiku 5.5 with `output_config={"effort": "low"}`. Per email: 1,500 input tokens, about 300 thinking tokens (assumed at low effort; measure yours) and 50 tokens of label, so 350 output tokens billed.

| | Input (75M tokens) | Output (17.5M tokens) | Total |
|---|---|---|---|
| Standard ($0.10 / $0.50 per MTok) | $7.50 | $8.75 | **$16.25** |
| Batch ($0.05 / $0.25 per MTok) | $3.75 | $4.38 | **$8.13** |

Note what dominates: output, and most of the output is thinking. Setting effort explicitly matters more than the batch discount here.

## How this comes up in interviews

"Process a big backlog" is a common follow-up in design rounds (Reported, see E6). Strong answers give a number (requests per second, concurrency, hours, dollars), say who retries, and name the platform constraint. Practice prompts in the style of those rounds:

- "Label 2 million support tickets by Friday. Walk me through throughput, rate limits, failure handling and cost."
- "The customer runs everything through Amazon Bedrock. What changes in your plan?"

> **Key takeaways**
>
> - Backlog with nobody waiting: Message Batches at half price. Needs answers soon, has tool loops, or runs on Bedrock, Vertex or Foundry: an async pool.
> - `gather` creates the work; a semaphore caps it. Size concurrency from throughput times latency, then check it against per-model rate limits.
> - One retry layer, honour `retry-after`, release the slot while waiting, never retry 400s, cap attempts.
> - Batches: 100,000 requests or 256 MB, up to 24 hours, results for 29 days, any order, matched by a valid `custom_id`. Errored items tell you whether to fix or retry.
> - Set `effort` explicitly in any cost estimate: thinking tokens are output tokens.
