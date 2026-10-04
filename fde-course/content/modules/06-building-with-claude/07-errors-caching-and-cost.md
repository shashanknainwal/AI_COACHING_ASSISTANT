---
title: "Errors, Refusals, Prompt Caching, and Cost"
type: reading
minutes: 18
---

> **By the end of this lesson you will be able to:**
> - Configure the SDK's built-in retries and timeouts, and handle what's left over
> - Catch API errors in the right order and turn them into clear outcomes
> - Handle refusals and truncation as normal outcomes, not crashes
> - Use prompt caching correctly, verify it's working, and compute the real cost of a call

## What the SDK already does for you

The official Anthropic SDK **automatically retries** connection errors, timeouts, rate limits (429) and server errors (5xx) with exponential backoff, honoring the `retry-after` header when present. By default it retries **2 times**. You configure it, rather than writing your own retry loop:

```python
client = anthropic.Anthropic(max_retries=3, timeout=60.0)    # for every request

# or per request:
client.with_options(max_retries=0, timeout=10.0).messages.create(...)
```

Choose the numbers based on context. A user waiting in a chat window wants a quick, clear failure (few retries, short timeout). A nightly batch job can afford more patience.

(You built your own retry loop for a customer's API in Module 4. For the Claude API, use the SDK's; it already does the right thing.)

## Errors that survive the retries

When retries are exhausted, or the error isn't retryable, the SDK raises a typed exception. Catch them **most specific first**:

```python
try:
    response = client.messages.create(...)
except anthropic.RateLimitError:          # 429 after retries: back off, queue, or tell the user to wait
    ...
except anthropic.BadRequestError as e:    # 400: your request is wrong (bad parameter, invalid schema)
    ...
except anthropic.AuthenticationError:     # 401: bad or missing API key
    ...
except anthropic.APIStatusError as e:     # any other HTTP error; e.status_code tells you which
    ...
except anthropic.APIConnectionError:      # network problems (after retries)
    ...
```

`RateLimitError`, `BadRequestError` and `AuthenticationError` are all subclasses of `APIStatusError`, so if you catch `APIStatusError` first, the specific handlers never run. Never match on error message text; use the types.

| Error | Retry? | What to do |
|---|---|---|
| `BadRequestError` (400) | No | It's a bug in your request. Log it with the request ID and fix it |
| `AuthenticationError` (401) | No | Alert: the key is wrong, expired, or missing |
| `RateLimitError` (429) | Already retried | Queue the work, slow down, or ask for higher limits |
| 5xx / overloaded (529) | Already retried | Degrade gracefully; try again later or use a fallback model |
| `APIConnectionError` | Already retried | Check network; degrade gracefully |

**Log the request ID** with every error (`e.request_id`) and every response (`response._request_id`). It's the fastest way to get help debugging a specific request.

## Refusals and truncation are outcomes, not exceptions

Two situations return a normal HTTP 200 response that still isn't a usable answer:

- **`stop_reason == "refusal"`**: Claude's safety systems declined the request. `response.stop_details.category` gives a machine-readable reason when one is available. Show a polite, product-appropriate message; don't retry the same request in a loop.
- **`stop_reason == "max_tokens"`**: the output was cut off. Don't show a half-sentence as if it were complete. Raise `max_tokens`, ask for a shorter output, or (for long generations) stream.

For production systems on Claude Opus 5.5, the API also offers **server-side fallbacks** (a beta feature): if a request is refused, the API can re-run it on a fallback model within the same call. It's worth knowing about; read the current documentation before using it, since beta features evolve.

## Prompt caching

Every request resends your system prompt, examples, and conversation history. For a support assistant with a 3,000-token system prompt handling 10,000 conversations a day, that repeated prefix is most of your bill.

**Prompt caching** lets the API reuse the processing of a repeated prefix. The rules:

- **It's a prefix match.** The cache covers everything up to a marked point, in order: tools, then system, then messages. **Any change before that point**, even one character, means a cache miss for everything after it.
- **Mark what to cache** with `cache_control`. Either on a system block:

```python
system=[{"type": "text", "text": LONG_SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}]
```

  or with top-level automatic caching (`cache_control={"type": "ephemeral"}` on the request), which caches up to the last cacheable block, convenient for growing conversations.
- **There's a minimum size.** Short prefixes (under roughly 1,000-4,000 tokens, depending on the model) silently aren't cached.
- **Caches expire.** The default lifetime is about 5 minutes after last use (a 1-hour option exists).
- **Put stable content first, volatile content last.** A timestamp or user name at the top of the system prompt destroys caching for everything after it.

### Verify it's actually working

Check `usage` on consecutive requests:

```python
print(response.usage.cache_creation_input_tokens)  # written to the cache this time
print(response.usage.cache_read_input_tokens)      # served from the cache this time
print(response.usage.input_tokens)                 # processed normally
```

The first request **writes** the cache; later requests with the same prefix **read** it. If `cache_read_input_tokens` stays at zero, something in your prefix is changing between requests (a timestamp, a random ID, unsorted JSON, a different tool order).

## The real cost of a call

With caching, a request's input is split into three parts, each with its own price:

```
cost = (input_tokens         × input price
      + cache_creation_tokens × cache-write price
      + cache_read_tokens     × cache-read price
      + output_tokens         × output price) ÷ 1,000,000
```

Prices per million tokens for Claude Opus 5.5:

| Token type | Price |
|---|---|
| Input (uncached) | $4.00 |
| Cache write (5-minute) | $5.00 (1.25 × input) |
| Cache read | $0.20 |
| Output (includes thinking) | $20.00 |

Cache reads are 20 times cheaper than uncached input, so for a long, stable system prompt reused across many requests, caching cuts input cost dramatically after the first request. Prices change over time and differ by model, so keep them in one table in your code, not scattered through it.

Two more cost tools:

- **`client.messages.count_tokens(...)`** tells you how many input tokens a request will use before you send it.
- **Output tokens include thinking.** Lower `effort` reduces both latency and output cost for tasks that don't need deep reasoning.

> **Key takeaways**
> - Configure the SDK's built-in retries and timeouts (`max_retries`, `timeout`, `with_options`) instead of writing your own loop.
> - Catch errors most specific first, never by message text, and log request IDs.
> - Treat refusal and max_tokens as normal outcomes with clear handling.
> - Prompt caching is a prefix match: mark stable content, keep volatile content last, verify with usage, and price all four token types.
