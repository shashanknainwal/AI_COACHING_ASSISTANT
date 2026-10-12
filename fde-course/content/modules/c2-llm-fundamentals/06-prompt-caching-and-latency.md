---
title: Prompt Caching and Latency
type: reading
minutes: 26
---

> **By the end of this lesson** you'll be able to explain how prompt caching works, design a prompt so it caches, prove a cache is hitting, do the break-even math, and talk through latency and rate limits in a design round.

## How this comes up in an interview

Caching is where cost and latency questions meet. In an LLM system design round (Reported as common in applied AI loops), a good follow-up to "your agent resends a 20K-token system prompt every turn" is "so what?", and the answer should include prompt caching, its numbers, and how you'd know it's working. Practice prompts in this lesson are original.

## How prompt caching works

<div data-diagram="prompt-caching"></div>

Prompt caching is a **prefix match**. The API renders your request in a fixed order: **tools, then system, then messages**. You mark a point with `cache_control`, and the API can reuse the processed prefix up to that point on the next request, as long as every byte before it is identical.

The one rule to say in an interview: **any change anywhere in the prefix invalidates everything after it.** A timestamp in the system prompt, a reordered JSON key, one extra tool: the cache misses from that point on.

```python
# Illustrative: cache a large, stable system prompt (Anthropic Python SDK shapes)
response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=16000,
    system=[{
        "type": "text",
        "text": LARGE_STABLE_INSTRUCTIONS,
        "cache_control": {"type": "ephemeral"},          # 5-minute TTL (default)
    }],
    messages=[{"role": "user", "content": question}],   # varies per request: after the breakpoint
)
```

Caching is **opt-in**: nothing caches unless you add a marker. There's also a simpler top-level `cache_control` on the request (automatic caching) that places the breakpoint on the last cacheable block. You can have at most 4 breakpoints per request, and prompts below a minimum length silently don't cache: 512 tokens on current models, but 4,096 on the older Haiku 4.5.

## Designing for cache hits

Order content from most stable to least stable:

| Position | Content | Changes |
|---|---|---|
| First | Tool definitions (sorted, deterministic) | Rarely |
| Then | System prompt: instructions, examples, reference docs | Per release |
| Then | Conversation history | Grows each turn, but earlier turns don't change |
| Last | The new question, timestamps, per-request IDs | Every request |

The silent invalidators to name:

- `datetime.now()` or a user's name interpolated into the system prompt.
- `json.dumps()` without `sort_keys=True`, or iterating a set, so bytes differ between requests.
- A tool list that varies per user or per mode. Tools render first, so nothing after them caches.
- Switching models mid-conversation. Caches are per model.
- Editing earlier turns instead of appending. Append-only history keeps the prefix stable, and on Opus 5.5 and the other current models it also keeps thinking signatures valid (Lesson 4).
- Changing `effort` or the thinking setting from request to request. Pin them per route.

Caches are also isolated per workspace on the Claude API, so the same prompt sent from two workspaces writes two separate entries.

## Verifying hits

Never assume a cache works. The response `usage` tells you:

| Field | Meaning |
|---|---|
| `cache_creation_input_tokens` | Written to the cache this request (you paid the write premium) |
| `cache_read_input_tokens` | Served from the cache (you paid the cheap read price) |
| `input_tokens` | The uncached remainder only |

Total prompt size is the sum of all three. If `cache_read_input_tokens` stays at zero across requests that should share a prefix, something in the prefix is changing. Diff two consecutive request bodies to find it.

The costliest caching failure is silent: requests keep succeeding and the bill quietly goes up after someone adds a dynamic field to the system prompt. A strong answer adds a standing check, such as a test asserting a second identical request shows `cache_read_input_tokens > 0`, or monitoring on the usage fields.

## TTLs and break-even

| | 5-minute TTL (default) | 1-hour TTL (`"ttl": "1h"`) |
|---|---|---|
| Cache write | about 1.25x base input price | 2x base input price |
| Cache read | about 0.1x base input on most models | same |
| Pays off after | 2 requests | 3 requests |

Each read refreshes the entry's timer at no extra cost, so traffic that arrives more often than every 5 minutes keeps the default cache warm on its own. Use the 1-hour TTL for bursty traffic with longer gaps.

The break-even math, in units of "one uncached prefix":

- **5-minute TTL, two requests:** 1.25 (write) + 0.1 (read) = 1.35, against 2.0 uncached. Caching wins from the second request.
- **1-hour TTL, three requests:** 2.0 + 0.1 + 0.1 = 2.2, against 3.0 uncached.

Reads are even cheaper on some models. On Claude Opus 5.5 and Sonnet 5.5, a cache read is 5% of base input: $0.20 per million tokens on Opus 5.5 (against $4 input) and $0.10 on Sonnet 5.5 (against $2).

### Worked example

A support assistant on Sonnet 5.5 ($2 input, $10 output, $0.10 cache read, $2.50 cache write, per million tokens). Each request has a 20,000-token stable prefix, a 1,000-token question and a 400-token answer. The route sets `output_config.effort` to `"low"`, and the 400 output tokens include its short thinking. (Leave Sonnet 5.5 at its default, `high`, and the output line can double or triple.)

| Request | Prefix | Question | Output | Total |
|---|---:|---:|---:|---:|
| No caching | 20,000 x $2/M = $0.040 | $0.002 | $0.004 | **$0.046** |
| First request (cache write) | 20,000 x $2.50/M = $0.050 | $0.002 | $0.004 | **$0.056** |
| Later requests (cache read) | 20,000 x $0.10/M = $0.002 | $0.002 | $0.004 | **$0.008** |

At volume, the cached request costs under a fifth of the uncached one. That's the number to say: "Caching takes this from about 4.6 cents to under 1 cent per request, and the output is now half of the bill, so output length is the next lever."

## Latency: what the user feels

Split latency into two parts and you can answer most latency questions:

1. **Time to first token.** The model has to process the input first. Longer prompts take longer. Caching a long stable prefix helps here too, not just on cost.
2. **Generation time.** Roughly proportional to output tokens, and thinking counts. Lower effort, a tighter output spec and shorter answers all help.

Then the levers:

- **Streaming** doesn't make the answer finish sooner, but the user sees text as it's generated, so perceived latency drops sharply for chat. It's also how you avoid HTTP timeouts on long outputs; the SDKs require streaming for very large `max_tokens`.
- **Smaller or faster options.** A smaller model, lower effort, or (on Opus 5.5, as a research preview on the Claude API only) fast mode, which runs the same model with faster output at a premium price.
- **Don't wait when no one is waiting.** Work nobody watches (overnight backfills, eval runs) can go through the Batch API at 50% of the standard price, discounts stacking with caching.

## Rate limits

APIs limit requests and tokens per minute, including **input tokens per minute (ITPM)**. When you exceed a limit you get a 429 with a `retry-after` header; the Anthropic SDKs retry 429s automatically (twice by default) with backoff.

The detail that impresses: **on the Claude API, cache reads don't count toward input-token rate limits on most models.** So good caching raises your effective throughput as well as cutting cost. If a design is bumping into ITPM limits with a large shared prefix, caching is the first fix, before asking for a higher limit.

And for debugging any of this, log the `request-id` header that every API response carries. It's what you give support when you need them to look at one specific call.

## Practice (say it out loud)

Answer out loud first, then open the model answer.

**1.** "Your agent's cache hit rate dropped to zero after Tuesday's deploy. Nothing errored. Walk me through how you find the cause."

<details>
<summary>Model answer and self-check</summary>

"First I'd confirm the symptom from `usage`, not from latency. Two patterns mean different things. If `cache_creation_input_tokens` is large on every request, the prefix is being rewritten each time. If both cache fields are zero, the marker is gone, or the prefix fell under the minimum length.

Then I'd capture two consecutive request bodies for the same conversation and diff them in render order: tools, then system, then messages. The first differing byte is the cause. The usual suspects from a deploy are a timestamp, user name or request ID added to the system prompt; tool definitions built per request, or in a different order; `json.dumps` without `sort_keys`; a route that now switches models or changes effort per request; and code that edits or trims earlier turns.

After the fix I'd add a standing check: a test that sends the same request twice and asserts `cache_read_input_tokens > 0`, and a dashboard alert on cache-read share, so the next regression shows up the same day."

Score yourself:
- [ ] Used the usage fields to tell 'rewritten every time' from 'not cached at all'.
- [ ] Diffed two real request bodies in tools, system, messages order.
- [ ] Named at least three concrete invalidators.
- [ ] Ended with a test or monitor.

</details>

**2.** "You run 5,000 document-QA requests a day over the same 150K-token manual, spread evenly over business hours. 5-minute or 1-hour TTL? What's the daily cost difference with and without caching on Sonnet 5.5?"

<details>
<summary>Model answer and self-check</summary>

"Assume an 8-hour business day. 5,000 requests over 480 minutes is about 10 a minute, so a request arrives every six seconds or so. Each read refreshes the 5-minute timer, so the default TTL stays warm all day. The 1-hour TTL costs more per write and buys nothing here. I'd pick 5 minutes, and only revisit if there are long gaps, say overnight or at lunch.

Prefix cost per day on Sonnet 5.5 ($2 input, $2.50 5-minute write, $0.10 read, per million):

| | Arithmetic | Per day |
|---|---|---:|
| No caching | 5,000 × 150K = 750M tokens × $2/M | **$1,500** |
| Caching, reads | about 750M tokens × $0.10/M | $75 |
| Caching, writes | one 150K write each morning: 150K × $2.50/M | about $0.38 |
| Caching, total | | **about $75** |

So caching saves about $1,425 a day on the prefix, roughly $30,000 a month over 21 working days. A few extra writes after any gap don't move that. The question tokens and the answers cost the same either way, so I'd state them separately, with effort set explicitly because thinking is output.

Two more things I'd say. On Sonnet 5.5 a cache read is 0.05x input; on a model at 0.1x the read line doubles to about $150, which is still a 90% saving. And cache reads don't count toward input-token rate limits on most models, so a 750M-token-a-day workload becomes much easier to fit under the limits."

Score yourself:
- [ ] Worked out the request rate and used it to pick the TTL.
- [ ] Got the uncached prefix cost ($1,500 a day) and the cached cost (about $75).
- [ ] Named the model when quoting the read price.
- [ ] Kept the question and output costs out of the comparison, or treated them separately.
- [ ] Mentioned rate limits or time to first token as a second benefit.

</details>

> **Key takeaways**
>
> - Caching is a prefix match over tools, then system, then messages. Any byte change invalidates everything after it, so put stable content first and volatile content last.
> - Verify with `usage.cache_read_input_tokens`, and keep a standing check, because cache failures are silent.
> - Writes cost about 1.25x input (5-minute TTL) or 2x (1-hour); reads about 0.1x, and 0.05x on Opus 5.5 and Sonnet 5.5. The 5-minute cache pays off from the second request.
> - Latency is time to first token plus generation time. Caching, effort, output length and streaming each attack a different part.
> - Cache reads don't count toward input-token rate limits on most models, so caching also buys throughput.
