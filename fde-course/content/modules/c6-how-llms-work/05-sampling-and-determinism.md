---
title: "Sampling: Logits, Temperature and Why Zero Isn't Deterministic"
type: reading
minutes: 15
---

> **By the end of this lesson** you'll be able to explain how a model turns logits into a chosen token, what temperature, top-k and top-p do, what logprobs and seeds are for, and give the vendor-neutral answer to "why isn't temperature 0 deterministic?"

## Why this comes up

C2 lesson 3 covered the Claude-specific side: the newest Claude models reject sampling parameters, and you get consistency from effort, prompts, structured outputs and evals. But interviews are often vendor-neutral, and many teams run more than one provider. Candidates report OpenAI and Perplexity applied loops include model-fundamentals questions of this kind (**Anecdotal**). You need the mechanism, not just the Claude rule. Practice prompts here are original.

## From logits to a token

At each step the model outputs one **logit** per vocabulary entry: an unbounded score. To choose the next token:

1. **Softmax** turns logits into probabilities: `p_i = exp(z_i) / Σ exp(z_j)`.
2. Optional **filters** remove unlikely tokens and renormalize.
3. A **sampler** draws one token from what's left, using a random number.

| Knob | What it does | Effect |
|---|---|---|
| **Temperature T** | Divides every logit by T before softmax | T < 1 sharpens toward the top token; T > 1 flattens toward randomness. T → 0 approaches **greedy** decoding (always the top token) |
| **Top-k** | Keep only the k most likely tokens | Cuts the long tail, fixed size |
| **Top-p (nucleus)** | Keep the smallest set of top tokens whose probabilities sum to at least p | Adapts: a confident step keeps 1–2 tokens, an uncertain step keeps many |

A quick worked example. Logits `[2.0, 1.0, 0.1]`:

| Temperature | Probabilities |
|---|---|
| 1.0 | 0.66, 0.24, 0.10 |
| 0.5 | 0.86, 0.12, 0.02 |
| 2.0 | 0.50, 0.30, 0.19 |

With top-p 0.9 at temperature 1.0, the first two tokens sum to 0.90, so the third is dropped and the first two are renormalized to 0.73 and 0.27.

## Logprobs and seeds

- **Logprobs** are the log of each chosen token's probability, sometimes with the top alternatives. Teams use them for confidence scores, for cheap classification (compare the logprob of "yes" versus "no"), and for spotting low-confidence spans. Not every API exposes them. At the time of writing the Claude Messages API doesn't return token log probabilities, so on Claude you get confidence another way: ask for a calibrated label in a structured output, sample several times and measure agreement, or verify against sources. Check each vendor's current docs.
- **Seeds** fix the random number generator used by the sampler, so the same request can reproduce the same draws. Where vendors offer a seed, it's documented as best-effort, for the reasons in the next section. Check each vendor's docs.

## Why temperature 0 isn't fully deterministic

This is the vendor-neutral answer interviewers want. Greedy decoding removes the sampler's randomness, but the logits themselves can differ slightly between two runs of the same request:

1. **Floating-point arithmetic isn't associative.** `(a + b) + c` can differ from `a + (b + c)` in the last bits. GPU kernels sum in different orders depending on how work is split.
2. **Batching changes the split.** Your request shares the accelerator with other users' requests. The batch size and its contents change how the kernels reduce, so your logits can differ in tiny ways from run to run. Thinking Machines Lab wrote this up in ["Defeating Nondeterminism in LLM Inference"](https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/) (2025).
3. **Tiny differences become big ones.** When two tokens are nearly tied, a last-bit difference flips which one wins. Every later token is conditioned on that choice, so the outputs diverge from there.
4. **Infrastructure varies.** Different hardware, software versions or routing across a provider's fleet can change results, and models with expert routing can route differently depending on the batch.

Then add the modern twist: on current Claude models, sampling parameters are rejected (on Claude Opus 5.5 `temperature`, `top_p` and `top_k` all return a 400; on Claude Sonnet 5.5 and Claude Haiku 5.5 non-default values are rejected), and adaptive thinking means the amount of reasoning can differ between runs too.

So the strong answer has two halves: "Here's why the bits differ," and "So I don't design for determinism. I design for variance: structured outputs and enums for shape, deterministic code for business rules, caching of results I need to replay, and evals that run each case several times and report a pass rate."

## Practice (say it out loud)

- "We set temperature to zero and still get different answers on the same input about 2% of the time. Bug or expected?"
- "Explain top-p to a product manager in two sentences. Then explain when you'd prefer it to top-k."
- "How would you get a confidence score for a classifier on a model that doesn't return logprobs?"

> **Key takeaways**
>
> - Logits become probabilities through softmax. Temperature rescales logits; top-k and top-p cut the tail and renormalize.
> - Logprobs give per-token confidence where an API exposes them. Seeds make sampling reproducible on a best-effort basis. Check each vendor's docs.
> - Temperature 0 isn't deterministic because floating-point sums depend on batching and kernel order, near-ties flip, and errors compound token by token.
> - The newest Claude models reject sampling parameters. Design for variance with schemas, code and repeated-run evals.
