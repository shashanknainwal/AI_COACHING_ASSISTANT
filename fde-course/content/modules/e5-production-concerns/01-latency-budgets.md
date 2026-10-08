---
title: "Latency Budgets: Where the Seconds Go"
type: reading
minutes: 18
---

> **By the end of this lesson** you'll be able to split an LLM request's latency into parts you can measure, write a latency budget for a feature, pick the right lever for each part (streaming, effort, model, caching, output length, parallel calls), and report p50 and p95 the way a design interviewer expects.

## How this comes up in interviews

Latency is one of the first numbers a design interviewer asks you to commit to. Candidates describe system design rounds about LLM infrastructure at Anthropic and LLM deployment at OpenAI (Reported, see module E6), and Perplexity's AI design round is described as covering serving under latency limits and caching (Reported: [Design Gurus](https://www.designgurus.io/answers/detail/what-is-the-perplexity-interview-process-like-round-by-round), [Interview Query](https://www.interviewquery.com/prep-guides/perplexity-ai-software-engineer)). The weak answer is "we'll use a faster model." The strong answer names which part of the latency each change attacks, and how you'd measure it. That's what this lesson builds.

If you want a refresher on streaming basics first, the FDE track's "Streaming and Long Outputs" lesson covers the SDK helper. This lesson goes further: budgets, tails and tradeoffs.

## Four parts of one request

From the user's click to the last word on screen, a Claude-backed request spends time in four places:

| Part | What happens | Grows with |
|---|---|---|
| **Your code before the call** | Auth, retrieval, building the prompt, queueing | Retrieval fan-out, slow databases, your own rate limiter |
| **Time to first token (TTFT)** | The model reads the prompt. On models that think, it also reasons before the first visible word | Uncached input length, thinking depth (effort) |
| **Generation** | Tokens stream out one after another | Output tokens, including thinking tokens |
| **Your code after the call** | Parsing, validation, tool execution, post-processing | Tool round trips in an agent loop |

Two things here surprise people in interviews.

**Thinking sits inside TTFT for the user.** Claude Opus 5.5 always runs adaptive thinking; you control its depth with `output_config.effort`, and the default is `medium`. By default the thinking text isn't returned (`display` is `"omitted"`), so a streaming client sees thinking blocks with empty text and then the answer. To the user that looks like a pause before the first word. If you show progress, set `thinking={"type": "adaptive", "display": "summarized"}` and render the summary while the model reasons.

**Agent loops multiply everything.** A support agent that makes four tool calls pays TTFT and generation five times, plus four tool executions. "Fewer turns" is often the biggest latency win, and lower effort tends to produce fewer, more consolidated tool calls.

## Write the budget down

A latency budget assigns each part a share of the target, so you know which team owns a regression. Here's an illustrative budget for an invoice Q&A sidebar at Ledgerline (fictional), where an accounts-payable clerk asks "why was this invoice flagged?":

| Stage | p95 budget | Notes |
|---|---:|---|
| Gateway and auth | 50 ms | |
| Retrieve invoice, vendor record, policy chunks | 400 ms | Three lookups in parallel, not in sequence |
| Build prompt | 20 ms | Stable instructions first so they cache |
| Model: time to first visible token | 1,500 ms | Effort `low`, cached prefix |
| **First words on screen** | **≈2.0 s** | **The number the clerk feels** |
| Model: generation | 4,000 ms | Answer capped by an output spec of about 150 words |
| Validation and citations | 100 ms | |
| **Answer complete** | **≈6.1 s** | |

These numbers are made up for the example. Yours come from measurement. The structure is the point: two targets (first words, complete answer), a line per stage, and an owner for each line.

Agree early on **which latency you mean**. "Two seconds" for a chat product almost always means time to first token. For an API that returns JSON to another service, only total time counts, because nothing is shown until it's done.

## The levers, mapped to the part they move

| Lever | Moves | Cost of using it |
|---|---|---|
| **Streaming** | Perceived latency (first words appear early). Total time is unchanged | Client complexity; you must handle a stream that fails halfway |
| **Lower effort** | TTFT and generation (less thinking) | Possible quality loss on hard cases. Measure with your eval |
| **Smaller model** | TTFT and generation | Quality; a separate prompt cache and rate-limit pool |
| **Prompt caching** | TTFT on long, stable prefixes | Prompt structure discipline; a write premium on misses |
| **Output spec** | Generation | Prompt work. "Three bullets, under 60 words" is a latency feature |
| **Parallel calls** | Wall-clock time of independent steps | Rate-limit pressure; cache timing (below) |
| **Fast mode** | Generation speed | Premium price, research preview, Claude API only |
| **Precompute or batch** | Removes the wait entirely | Only works when nobody is waiting |

Some details worth knowing precisely:

- **Fast mode** runs Claude Opus 5.5 with up to 2.5x higher output tokens per second at $8 / $40 per million tokens (twice the standard $4 / $20). It's a research preview on the Claude API only, needs the `fast-mode-2026-02-01` beta header and `speed="fast"`, has its own rate limit, and switching speed invalidates the prompt cache.
- **Long outputs need streaming anyway.** The Python SDK refuses a non-streaming request it estimates will run past about ten minutes. Use `client.messages.stream(...)` and `get_final_message()` when you don't need the individual events.
- **Pre-warming the cache** removes the cold-cache TTFT penalty on the first real request: send a request with `max_tokens=0` at startup, with the same system prompt and the same thinking and effort settings as real traffic. It returns immediately and bills the cache write but no output. It can't be combined with `stream=True`.

## Measure TTFT in code

Measure the first **visible text**, not the first byte. With thinking omitted, the first events carry no text.

```python
import time
import anthropic

client = anthropic.Anthropic()

def answer(question, send):
    start = time.perf_counter()
    ttft = None
    with client.messages.stream(
        model="claude-opus-5-5",
        max_tokens=4096,
        output_config={"effort": "low"},
        system=STABLE_INSTRUCTIONS,            # same bytes every request, so it can cache
        messages=[{"role": "user", "content": question}],
    ) as stream:
        for text in stream.text_stream:
            if ttft is None:
                ttft = time.perf_counter() - start
            send(text)                         # forward to the browser as it arrives
        final = stream.get_final_message()
    total = time.perf_counter() - start
    return final, {"ttft_s": ttft, "total_s": total, "output_tokens": final.usage.output_tokens}
```

Log those three numbers with the request id (`final._request_id`) on every call. Output tokens matter because generation time scales with them: if total time doubled, check whether the answers got longer before blaming the API.

## Parallelize what's independent

If two calls don't depend on each other, run them at the same time. The wall-clock time becomes the slowest branch instead of the sum.

```python
import asyncio
import anthropic

client = anthropic.AsyncAnthropic()
limit = asyncio.Semaphore(8)           # stay inside your rate limits

async def classify(email):
    async with limit:
        return await client.messages.create(
            model="claude-haiku-5-5", max_tokens=256,
            messages=[{"role": "user", "content": email}],
        )

async def classify_all(emails):
    return await asyncio.gather(*(classify(e) for e in emails))
```

Three cautions to raise yourself in an interview:

1. **Fan-out widens the tail.** If each call is under its own p95 95% of the time, a request that waits for five calls is under on all five only 0.95⁵ ≈ 77% of the time. Nearly one request in four hits at least one slow call.
2. **Parallel requests don't share a fresh cache.** A cache entry becomes readable only after the first response begins streaming. Fire N identical-prefix requests at once and all N pay full price. Send one, wait for its first token, then fire the rest.
3. **Parallelism spends rate limit faster.** A semaphore caps concurrency; without one, a burst of 200 parallel calls turns into a burst of 429s.

## Percentiles, not averages

Latency distributions have long right tails: long answers, retries, cold caches. The mean hides them. Report **p50** (the typical request) and **p95** or **p99** (the bad days users remember).

```python
def percentile(values, p):
    """Nearest-rank percentile, p in (0, 100]."""
    ordered = sorted(values)
    k = max(1, round(p / 100 * len(ordered)))
    return ordered[k - 1]
```

Rules that keep the numbers honest:

- **Segment before you aggregate.** Per route, per model, per effort. A p95 across classification and long drafting means nothing.
- **Include retries and timeouts.** A request that succeeded on its third attempt took the time of all three. The SDK's own retries count too: with the default 2 retries, wall-clock time can reach the timeout times three.
- **Watch output length next to latency.** Plot p95 total time beside p95 output tokens. When they move together, the fix is the output spec, not the infrastructure.
- **Measure on real traffic.** One test request tells you nothing about p95.

## Practice (say it out loud)

Original prompts in the style of an LLM design round:

- "Your document Q&A has a p95 of 9 seconds and the product manager wants 3. You have one week. Walk me through what you measure first and the three changes you'd try, in order."
- "Your agent's p50 is fine but p99 is 40 seconds. What usually lives in that tail, and how would you prove it?"
- "Streaming is already on and users still say it feels slow. What's going on?" (Hint: thinking before the first visible word, a cold cache, or a long retrieval step before the call.)

> **Key takeaways**
>
> - Split latency into pre-call work, time to first token, generation and post-call work, and budget each part with an owner.
> - Thinking happens before the first visible word: effort is a latency lever, and summarized thinking can show progress.
> - Streaming fixes perceived latency only. Total time needs fewer tokens, less thinking, a smaller model, caching or fewer turns.
> - Parallelize independent calls, but cap concurrency, warm the cache with one request first, and expect fan-out to widen the tail.
> - Report p50 and p95 per route, including retries, next to output token counts.
