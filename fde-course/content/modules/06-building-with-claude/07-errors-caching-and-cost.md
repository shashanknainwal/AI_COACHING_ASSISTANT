---
title: "Errors, Refusals, Prompt Caching, and Cost"
type: reading
minutes: 7
---

> **By the end of this lesson you will be able to:**
> - Configure the SDK's retries and timeouts and handle what's left
> - Catch API errors in the right order
> - Handle refusals and truncation as normal outcomes
> - Use prompt caching, verify it, and compute the real cost of a call

Harbor Bank's assistant will run all day for hundreds of agents, and Priya has a budget line to defend. An uncached 3,000-token system prompt resent on 10,000 conversations a day is most of that bill.

## What the SDK already does

The Anthropic SDK **retries automatically** on connection errors, timeouts, 429s and 5xx errors with exponential backoff, honoring `retry-after`. The default is **2 retries**. Configure it instead of writing your own loop:

```python
client = anthropic.Anthropic(max_retries=3, timeout=60.0)    # for every request

# or per request:
client.with_options(max_retries=0, timeout=10.0).messages.create(...)
```

Chat wants a fast, clear failure; a nightly job can be patient.

## Errors that survive the retries

Catch typed exceptions **most specific first**:

```python
try:
    response = client.messages.create(...)
except anthropic.RateLimitError:          # 429 after retries
    ...
except anthropic.BadRequestError as e:    # 400: your request is wrong
    ...
except anthropic.AuthenticationError:     # 401: bad or missing key
    ...
except anthropic.APIStatusError as e:     # any other HTTP error; check e.status_code
    ...
except anthropic.APIConnectionError:      # network problems (after retries)
    ...
```

The first three are subclasses of `APIStatusError`; catch it first and they never run. Never match on message text.

| Error | What to do |
|---|---|
| 400 | A bug in your request: log with request ID, fix it |
| 401 | Alert: key wrong, expired or missing |
| 429 (already retried) | Queue, slow down, or ask for higher limits |
| 5xx / 529 overloaded, or connection error (already retried) | Degrade gracefully or use a fallback model |

Log `e.request_id` on errors and `response._request_id` on responses.

## Refusals and truncation are outcomes

Both arrive as HTTP 200:

- **`stop_reason == "refusal"`**: declined by Claude's safety systems. `stop_details.category` may say why. Show a polite message; don't retry in a loop. Opus 5.5 also offers opt-in server-side fallbacks (beta) to another model; check the current docs first.
- **`stop_reason == "max_tokens"`**: cut off. Don't present it as complete; raise `max_tokens`, ask for less, or stream.

## Prompt caching

- **Prefix match** over tools, then system, then messages. Any change before the cache point, even one character, misses for everything after it.
- **Mark it** with `cache_control` on a block, or at the top level of the request for growing conversations:

```python
system=[{"type": "text", "text": LONG_SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}]
```

- **Minimum size:** 512 tokens on current models such as Opus 5.5; older models need more (4,096 on Haiku 4.5). Shorter prefixes silently don't cache.
- **Lifetime:** about 5 minutes after last use by default; a 1-hour option exists.
- **Stable first, volatile last.** A timestamp at the top of the system prompt destroys caching.

Verify with `usage` on consecutive requests:

```python
print(response.usage.cache_creation_input_tokens)  # written to the cache this time
print(response.usage.cache_read_input_tokens)      # served from the cache this time
print(response.usage.input_tokens)                 # processed normally
```

If `cache_read_input_tokens` stays at zero, the prefix is changing (timestamp, random ID, unsorted JSON, tool order).

<div data-diagram="prompt-caching"></div>

## The real cost of a call

```
cost = (input_tokens         × input price
      + cache_creation_tokens × cache-write price
      + cache_read_tokens     × cache-read price
      + output_tokens         × output price) ÷ 1,000,000
```

| Claude Opus 5.5, per million tokens | Price |
|---|---|
| Input (uncached) | $4.00 |
| Cache write (5-minute) | $5.00 (1.25 × input) |
| Cache read | $0.20 (0.05 × input) |
| Output (includes thinking) | $20.00 |

Cache reads are 20 times cheaper than uncached input. Keep prices in one table in code. `client.messages.count_tokens(...)` counts input tokens before you send, and lower effort cuts output (thinking) cost.

> **Key takeaways**
> - Configure `max_retries` and `timeout`; don't write your own loop.
> - Catch errors most specific first; log request IDs.
> - Refusal and max_tokens are outcomes with clear handling.
> - Caching is a prefix match: stable content first, verify with usage, price all four token types.
