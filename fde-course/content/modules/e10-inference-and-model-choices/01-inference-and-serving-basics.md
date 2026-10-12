---
title: "Inference and Serving: What Happens Between the Request and the First Token"
type: reading
minutes: 18
---

> **By the end of this lesson** you'll be able to explain prefill and decode, say what the KV cache is and why it limits batch size, separate time to first token from throughput, reason about rate-limit pools and the batch tier, and answer "why is my first token slow?" with a list of causes you can check.

## Why this comes up

Candidate accounts describe Anthropic's design round as often being about LLM infrastructure (**Reported**; see E6 lesson 01). You won't be asked to build a GPU scheduler. You will be asked questions like "why does a long prompt slow the first token but not the rest?", "why is a cached prefix cheaper?" and "how many concurrent users does this fit?". A candidate who knows the two phases of inference answers these in one sentence. Everyone else guesses.

A note on sources. Anthropic doesn't publish how it serves Claude. Everything here about serving internals is the general picture from open serving stacks and published research. Facts about the Claude API (pricing, limits, effort) come from the Claude API docs, and the lesson says which is which.

## Two phases: prefill and decode

A transformer generates text one token at a time. Every request goes through two phases.

**Prefill.** The model reads the whole prompt in one pass. All prompt tokens are processed in parallel, so prefill is limited by compute (matrix multiplies). Longer prompts take longer, roughly in proportion at moderate lengths and worse at very long lengths, because attention compares every token with every earlier one.

**Decode.** The model produces output tokens one at a time. Each new token needs a full pass through the model, but only for that one token. The arithmetic per step is small. What dominates is reading the model's weights and the stored keys and values from GPU memory. So decode is limited by memory bandwidth, not compute.

| | Prefill | Decode |
|---|---|---|
| Work | All prompt tokens at once | One token per step |
| Bottleneck | Compute | Memory bandwidth |
| Users feel it as | Time to first token | Tokens per second while streaming |
| Grows with | Prompt length | Output length (thinking included) |

This one table answers most interview questions. A 200K-token prompt hurts the first token. A 4,000-token answer hurts total time. Streaming hides decode time from the user, but it can't hide prefill.

## The KV cache

During attention, each token produces a key and a value vector at every layer. Decode needs the keys and values of every earlier token at every step. Recomputing them each step would be wasteful, so servers keep them in GPU memory. That store is the **KV cache**.

Its size per token is easy to work out:

```
bytes per token = 2 (K and V) x layers x KV heads x head dimension x bytes per number
```

For a published open-weight 8B-parameter model with 32 layers, 8 KV heads, head dimension 128 and 16-bit numbers, that's 2 x 32 x 8 x 128 x 2 = 131,072 bytes, which is 128 KiB per token. A single 32K-token conversation then holds 4 GiB of KV cache. On an 80 GB GPU with about 16 GB of weights, the rest of memory fits only around 15 such conversations at full length.

So KV-cache memory, not compute, usually caps how many requests a GPU serves at once. That's why serving stacks care about:

- **Grouped-query attention** (fewer KV heads than query heads), which shrinks the cache.
- **Paged KV memory**, which allocates the cache in blocks so memory isn't reserved for the longest possible output.
- **KV quantisation** (8-bit or lower), which trades a little quality for capacity.

### Prefix caching, and Claude's prompt caching

If many requests share the same prefix (a long system prompt, a tool list, a document), a server can keep that prefix's KV cache and skip its prefill next time. Open serving stacks call this prefix caching.

Claude's prompt caching behaves the way you'd expect from that mechanism. It is a prefix match over tools, then system, then messages. Any byte change invalidates everything after it. A cache hit shows up in `usage.cache_read_input_tokens`. Cache reads are billed at a fraction of base input: 0.05x on Opus 5.5 and Sonnet 5.5, 0.025x on Fable 5.1, and 0.1x on other current models. Anthropic doesn't publish its implementation. When you explain the discount, say "consistent with skipping prefill for the prefix", not "Anthropic stores the KV cache on GPU X".

On the Claude API, caching is opt-in. Use top-level `cache_control` for automatic caching, or put breakpoints on blocks. The minimum cacheable prefix is 512 tokens on current models (4,096 on Haiku 4.5).

## Batching: throughput versus latency

A decode step reads all the weights from memory whether it serves one request or 64. So servers **batch**: each decode step advances many requests at once. Up to a point, a bigger batch gives more total tokens per second at almost the same cost per step.

The tradeoff:

- **Bigger batches** mean higher throughput and lower cost per token. Each request's tokens-per-second drops a little, and queueing grows when the server is full.
- **Smaller batches** mean faster individual streams and wasted hardware.

**Continuous batching** adds and removes requests from the running batch at every step, instead of waiting for a whole batch to finish. It's the default in modern open serving stacks. **Chunked prefill** splits a long prompt's prefill into pieces interleaved with other requests' decode steps, so one 100K-token prompt doesn't freeze every stream on that GPU. Some stacks go further and run prefill and decode on separate GPU pools ("disaggregated serving"), because the two phases want different hardware.

Two more techniques you should be able to name:

- **Speculative decoding.** A small draft model proposes several tokens, and the big model checks them in one pass. Output is identical in distribution. It's faster when the draft is often right.
- **Weight quantisation.** Serving weights at 8 or 4 bits cuts memory and bandwidth, which speeds up decode. It can cost quality, so you measure it on your own eval.

## The metrics that matter

| Metric | What it measures | Driven by |
|---|---|---|
| **TTFT** (time to first token) | Request sent to first visible token | Queueing, prefill, and on Claude, thinking before the visible text |
| **TPOT** or inter-token latency | Time per output token while streaming | Decode speed, batch size |
| **Throughput** | Tokens per second across all users | Batch size, hardware |
| **Goodput** | Requests per second that meet the latency targets | All of the above |

Report latencies as percentiles (p50, p95, p99), never averages. A p95 TTFT target is what product teams actually sign up to.

**On Claude, thinking sits inside TTFT.** Current models think by default (adaptive thinking). Thinking tokens are generated before the visible answer and billed as output. Effort controls how much the model thinks: Opus 5.5 and Haiku 5.5 default to `medium`, Sonnet 5.5 defaults to `high`, and `max_tokens` covers thinking as well as the answer. Under the default `display`, thinking text comes back empty, so a user staring at a spinner sees only "slow first token". To cut TTFT, lower effort before you add "think less" instructions, and measure.

### Worked example: where the first second went

Here is an illustrative chat request to Sonnet 5.5. These numbers are invented for the arithmetic. Measure your own; Anthropic doesn't publish per-phase timings.

| Step | Time |
|---|---|
| Gateway and network | 60 ms |
| Queueing upstream | 0 to 300 ms, depending on load |
| Prefill of a 30,000-token prompt, nothing cached | 400 ms |
| Thinking at effort `high` (Sonnet 5.5's default), about 600 tokens at 80 tokens/s | 750 ms |
| **First visible token** | **about 1.2 to 1.5 s** |

Two changes, both measurable:

1. Cache the 28,000-token stable prefix. Prefill now covers only about 2,000 new tokens.
2. Set `output_config: {effort: "low"}` and check quality on the team's eval. Thinking might drop to about 100 tokens.

The same request could reach its first token in roughly 300 ms. It also costs less: the thinking tokens you removed were billed as output.

## Rate limits and pools on the Claude API

The serving side is shared, so the API meters you. Limits are set per organisation and per model, as requests per minute and as input and output tokens per minute. Exceeding one returns a 429 with a `retry-after` header. A few facts from the docs are worth knowing exactly:

- **Pools are per model family, and new models get their own.** Opus 5.5 has a separate pool from Opus 5. Sonnet 5.5 has its own pool, separate from Sonnet 5's. Fable 5.1 shares one "Fable 5.x" pool with Fable 5. Re-check your tier's numbers before you move volume.
- **Cache reads don't count toward input-token limits on most models.** So caching raises effective throughput as well as cutting cost. (Haiku 3.5 is the documented exception.)
- **The Message Batches API** costs 50% of standard prices and returns results asynchronously. It isn't available on Bedrock, Vertex or Foundry.
- **Priority Tier** is not supported on Opus 5.5, Sonnet 5.5 or Fable 5.1, according to the migration notes. Don't design a latency guarantee around it without checking the current docs for your model and platform.
- **Fast mode** is a research preview on the Claude API only. On Opus 5.5 it's `speed: "fast"` at $8/$40 per million tokens, twice the standard price.

What this means for your design: the upstream limit is one shared bucket per model. If you have tenants or priority classes, you need your own admission control in front of it. That's what you build in the next exercise.

## "Why is my first token slow?" A checklist

When a customer asks, work through the list in this order:

1. **Is the request queued on your side?** Look at gateway queue time and 429s with retries.
2. **Did the prompt grow?** Check `input_tokens`. Prefill grows with prompt length.
3. **Did the cache stop hitting?** Is `cache_read_input_tokens` at zero? Look for a timestamp in the system prompt, reordered tools, or a changed model or effort.
4. **How much is the model thinking?** Compare `output_tokens` with the visible text, and check `effort`. Try one level lower.
5. **Are you streaming, and do you flush?** A proxy that buffers the response turns 300 ms into the whole response time.
6. **Has the upstream changed?** Check the status page and compare with request ids from a good day.

> **Key takeaways**
> - Prefill reads the prompt in parallel and is compute-bound, so it sets time to first token. Decode writes one token at a time and is bandwidth-bound, so it sets streaming speed.
> - KV-cache memory grows with tokens in flight and usually caps how many requests a GPU serves at once.
> - Batching trades a little per-user speed for much more throughput. Continuous batching and chunked prefill keep long prompts from freezing other streams.
> - On Claude, thinking sits inside TTFT and is billed as output. Effort is the main lever, and defaults differ by model.
> - Upstream limits are per model pool. Priority across your own tenants is your job, and Priority Tier isn't available on the newest models.
