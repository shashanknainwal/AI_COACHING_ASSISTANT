---
title: Transformers for Applied Engineers
type: reading
minutes: 20
---

> **By the end of this lesson** you'll be able to explain next-token prediction, attention as a weighted lookup, the KV cache, and prefill versus decode, and use them to answer "why does a longer prompt make this slower and more expensive?" without hand-waving.

## Why an applied engineer needs this

You won't be asked to derive backpropagation. You will be asked why things behave the way they do. "Why did latency jump when we added the policy manual to the prompt?" "Why is prompt caching so much cheaper?" "Why does the model miss a fact that is plainly in the context?" Candidates report that fundamentals and design rounds for applied roles probe exactly this kind of reasoning (**Reported**, for Anthropic, OpenAI and Perplexity applied loops). The questions in this lesson are original practice prompts written in that style.

The goal is a mental model that is accurate enough to predict behaviour, and honest about where it stops. Provider serving stacks are not fully public, so say "conceptually" when you describe them.

## Next-token prediction

A language model does one thing: given a sequence of tokens, it produces a score (a **logit**) for every token in its vocabulary, saying how likely each one is to come next. Turn the scores into probabilities, pick one token, append it, and repeat. That loop is **autoregressive generation**.

Everything else you see is built on that loop. A chat reply, a JSON object, a tool call and a chain of reasoning are all tokens produced one at a time. Two consequences matter in interviews:

- **Output is sequential.** The model can't write token 50 before token 49. That's why output speed is measured in tokens per second and why long answers take long.
- **The model only "knows" what is in its weights and its context.** There is no lookup into a database unless you give it one through tools or retrieval.

## Attention as a weighted lookup

The transformer, introduced in the 2017 paper ["Attention Is All You Need"](https://arxiv.org/abs/1706.03762), is the architecture behind current LLMs. Its key operation is **attention**. A useful way to explain it:

1. Every token is turned into three vectors: a **query** ("what am I looking for?"), a **key** ("what do I contain?") and a **value** ("what do I pass on if chosen?").
2. To update one token, the model compares its query with the key of every earlier token (a dot product). High score means relevant.
3. The scores go through a softmax, so they become weights that sum to 1.
4. The token's new representation is the weighted average of the earlier tokens' values.

So attention is a soft dictionary lookup: instead of fetching the one matching key, you fetch a blend of all values, weighted by how well each key matches. Real models run many of these lookups in parallel (**heads**) and stack dozens of **layers**. You'll compute one by hand in the next exercise.

```text
query  ·  key_1  -> score 2.1 \
query  ·  key_2  -> score 0.3  >  softmax -> weights 0.81, 0.13, 0.06 -> 0.81·v1 + 0.13·v2 + 0.06·v3
query  ·  key_3  -> score -0.4/
```

## Why cost and latency grow with context

Every token in the context takes part in attention for every token after it. Two consequences:

- **More input means more compute before the first output token.** The provider bills input per token because each one is real work.
- **Naive attention is quadratic.** Comparing every token with every earlier token is roughly n² work for n tokens. Serving stacks use many optimizations, so don't quote a precise curve. Do say: long prompts cost more than linearly in compute, and providers price per token to keep billing simple.

## Prefill and decode

A request runs in two phases. Interviewers like this distinction because it explains most latency questions.

| Phase | What happens | Bound by | You notice it as |
|---|---|---|---|
| **Prefill** | The whole prompt is processed at once, in parallel | Compute | **Time to first token (TTFT)** grows with prompt length |
| **Decode** | Output tokens are generated one at a time | Memory bandwidth (reading weights and cached state each step) | **Output tokens per second**, roughly steady for a given model and load |

A rough latency model you can say out loud:

```text
total time ≈ overhead + (uncached prompt tokens ÷ prefill speed) + (thinking tokens ÷ decode speed) + (output tokens ÷ decode speed)
```

On current Claude models, adaptive thinking is on by default, and thinking tokens are generated before the visible answer. So they sit inside the time to first visible token and are billed as output. Any latency estimate for these models should either set `effort` explicitly or include a line for thinking tokens. (C2 lesson 3 covers effort.)

## The KV cache

During decode, the model would waste effort if it recomputed the keys and values of every earlier token at every step. Instead it stores them: the **KV cache**. Each new token computes only its own query, key and value, then attends over the stored ones.

What to say about it:

- **It makes decode feasible.** Without it, each output token would repeat the work of the whole prefix.
- **It costs memory that grows with context length.** Roughly: 2 (keys and values) × layers × KV heads × head dimension × bytes per number, for every token in the context. Long contexts for many concurrent users fill accelerator memory, which is one reason long-context serving is expensive. You'll compute this in the exercise.
- **It lives for one request.** The API is stateless. The next request starts from scratch unless the provider reuses work, which brings us to caching.

## Why prompt caching is cheap

Conceptually, prompt caching keeps the result of prefill for a prefix, so a later request with the exact same prefix skips that work. The provider spends storage instead of compute, and passes part of the saving on. Implementation details aren't public, so describe it at this level.

On Claude, caching is a prefix match over tools, then system, then messages. Any byte change invalidates everything after it. Cache reads are billed at a fraction of the input price: 0.05x on Claude Opus 5.5 and Claude Sonnet 5.5 (for example $0.10 per million tokens on Sonnet 5.5 against $2 base), 0.025x on Claude Fable 5.1, and 0.1x on other models. Cached prefixes also cut time to first token, because the prefill is skipped. Caching is opt-in: top-level `cache_control` for automatic caching, or breakpoints on blocks. The minimum cacheable prefix on current models is 512 tokens.

## Context rot and lost in the middle

A 1M-token window is a capacity, not a promise of equal attention to every token. Two observations to cite:

- **Lost in the middle.** The paper ["Lost in the Middle: How Language Models Use Long Contexts"](https://arxiv.org/abs/2307.03172) (Liu et al., 2023) found that models used information at the start and end of long inputs better than information in the middle. Newer models are better at this, but the lesson holds: position matters.
- **Context rot.** A term used across the industry for the way quality tends to degrade as input grows, even below the window limit. More irrelevant tokens means more distractors competing for attention.

What you do about it, in a design answer: retrieve the few relevant chunks instead of stuffing everything, put the instructions and the question where the model will use them (long documents first, the question at the end is a common Claude recommendation), trim stale tool results, and measure with an eval at the context lengths you'll actually run.

## Practice (say it out loud)

Original prompts in the style of a fundamentals round:

- "We added a 60K-token manual to every request and p50 latency went from 2 seconds to 9. Generation speed didn't change. Explain."
- "Why can a provider charge a tenth or less for cached input tokens?"
- "Your model answers questions about page 3 of a 400-page filing well, and page 200 badly. What's happening, and what would you change?"

> **Key takeaways**
>
> - LLMs predict one token at a time. Output is sequential, so its speed is tokens per second.
> - Attention is a weighted lookup: query against keys, softmax, weighted sum of values. Every context token is work for every later token.
> - Prefill (whole prompt, parallel) sets time to first token. Decode (one token at a time) sets generation speed. Thinking tokens add to time to first visible token.
> - The KV cache stores keys and values so decode doesn't redo the prefix. Its memory grows with context length.
> - Prompt caching skips repeated prefill for an identical prefix, so it is cheaper and faster. Long contexts still degrade: retrieve, place carefully and measure.
