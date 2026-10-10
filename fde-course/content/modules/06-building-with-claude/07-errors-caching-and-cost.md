---
title: "Errors, Refusals, Prompt Caching, and Cost"
type: reading
minutes: 10
---

> **By the end of this lesson you will be able to:**
> - Configure the SDK's retries and timeouts and handle what's left
> - Catch API errors in the right order
> - Handle refusals and truncation as normal outcomes, including fallbacks, refusal metrics and escalation
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

- **`stop_reason == "max_tokens"`**: cut off. Don't present it as complete; raise `max_tokens` (it covers thinking too), ask for less, or stream.
- **`stop_reason == "refusal"`**: declined, either by the model itself or by a safety classifier. Branch on `stop_reason`, then read `stop_details`.

### Handling a refusal properly

Banks, healthcare providers and security teams can hit refusals on legitimate work: a fraud analyst pasting a phishing kit, a security engineer triaging a malware sample. Classifiers are tuned to leave everyday health questions alone, but benign work can still trip them. "Show a polite message" is not enough for those customers.

```python
if response.stop_reason == "refusal":
    details = response.stop_details          # informational; can be None
    category = details.category if details else None
    log.warning("refusal", extra={"request_id": response._request_id, "category": category})
    # discard any partial output: a mid-stream refusal is not a complete answer
    return escalate(ticket, reason=f"refusal:{category}")
```

- **`stop_details.category`** says which class you hit. On current models the documented values include `"cyber"`, `"bio"`, `"reasoning_extraction"` (the prompt asked the model to write out its internal reasoning), and on Sonnet 5.5 and Haiku 5.5 also `"frontier_llm"` and `"general_harms"`. It can be `None`, and `explanation` isn't guaranteed. Never branch on it alone.
- **Before or mid-output.** A classifier can fire before any output (empty `content`) or partway through a stream. Throw away partial text. A refusal still counts against your rate limits.
- **Fallbacks.** Server-side `fallbacks` (beta) re-runs a declined request on another model in the same call. `fallbacks: "default"` lets Anthropic pick the model by refusal category. It exists on the Claude API and Claude Platform on AWS only, not on Bedrock, Vertex or Foundry, where you retry on another model yourself. Haiku 5.5 has no server-side fallback at all. `reasoning_extraction` declines are not retried, and a fallback model runs without Opus 5.5's earlier thinking blocks. Check the current docs for the beta header before you ship.
- **Measure it.** Refusal rate is an eval metric. Put realistic, legitimate-but-sensitive cases in your eval set (Module 8) and track refusals per category. A refusal on a case that should be answered counts as a failure, like a wrong answer. Watch the same rate in production dashboards.
- **Escalate.** Route refused work to a human queue with the request ID and category, never to a silent dead end. Collect false-positive patterns and take them to the customer's Anthropic account team. For legitimate security or life-sciences work there are verification programs (the Cyber Verification Program and the Life Sciences Verification Program); the account team can tell you whether the customer qualifies.
- **Fix the prompt you can fix.** If a prompt asks Claude to "show your reasoning step by step" in the answer, remove it: it invites `reasoning_extraction` declines. Read the thinking blocks (with summarized display) instead.

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

On Opus 5.5, cache reads are 20 times cheaper than uncached input (0.05×, 95% off); Sonnet 5.5 is the same. Most other models, including Haiku 5.5, charge 0.1× (90% off), and Fable 5.1 charges 0.025×. Always name the model when you quote a caching saving. Keep prices in one table in code. `client.messages.count_tokens(...)` counts input tokens before you send, and lower effort cuts output (thinking) cost.

> **Key takeaways**
> - Configure `max_retries` and `timeout`; don't write your own loop.
> - Catch errors most specific first; log request IDs.
> - Refusal and max_tokens are outcomes. For refusals: log the category and request ID, use fallbacks where the platform has them, track refusal rate in evals, escalate to a human.
> - Caching is a prefix match: stable content first, verify with usage, price all four token types.
