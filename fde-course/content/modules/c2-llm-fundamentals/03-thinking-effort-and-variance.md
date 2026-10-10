---
title: Thinking, Effort and Why Outputs Vary
type: reading
minutes: 24
---

> **By the end of this lesson** you'll be able to explain adaptive thinking and the effort parameter, explain how sampling works (logits, softmax, temperature, top-p), say why the same prompt can return different answers even at temperature 0, and describe how you get consistent behaviour on current Claude models without reaching for temperature.

## How this comes up in an interview

Two kinds of question tend to land here. In a design round: "Your agent is too slow and too expensive. What knobs do you have?" In a fundamentals or project deep dive: "The model gave a different answer to the same input in production. Why, and what did you do about it?"

A third kind is a plain fundamentals question, common in vendor-neutral and OpenAI-style rounds: "What does temperature do?"

A weak answer to the consistency question says "set temperature to zero, then it's deterministic". That's wrong twice. Temperature 0 isn't fully deterministic on any hosted model, and on the newest Claude models the parameter is rejected outright. A strong answer explains the mechanism, then talks about effort, prompts, structured outputs and evals. This lesson gives you both. Practice prompts here are original, written in the style of these rounds.

## Adaptive thinking

Current Claude models can reason before they answer. With **adaptive thinking**, the model decides when to think and how much, based on how hard the request is. A simple lookup gets little or no thinking; a multi-step problem gets more.

What to know for an interview:

- **On Claude Opus 5.5, thinking is always on.** You can't disable it. Sending `thinking: {"type": "disabled"}` or an old-style fixed thinking budget returns a 400 error. Omit the `thinking` parameter (or send `{"type": "adaptive"}`, which is the same thing).
- **The older "thinking budget" is gone on current models.** Earlier models took `budget_tokens`, a fixed number of thinking tokens. That's rejected on the newest models. Adaptive thinking replaced it.
- **Thinking is billed as output.** It happens and is billed the same whether or not you ask to see it.
- **You see a summary at most.** By default on current models the thinking text comes back empty. You can ask for a readable summary with `thinking: {"type": "adaptive", "display": "summarized"}`. The raw chain of thought is never returned.

Rules differ by model (for example, Sonnet 5.5 has its own way to switch thinking off between tool calls). In an interview, say "on the model we chose" and name it.

## Effort: the main dial

The **effort** parameter sets how thorough the model is, and therefore how many tokens it spends. It lives inside `output_config`:

```python
# Illustrative: request shape from the Anthropic Python SDK
response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=16000,
    output_config={"effort": "low"},   # low | medium | high | xhigh | max
    messages=[{"role": "user", "content": "Classify this ticket: ..."}],
)
```

| Level | Typical use |
|---|---|
| `low` | Classification, chat, simple sub-tasks, high-volume or latency-sensitive routes |
| `medium` | Cost-saving step-down where quality still holds. **The default on Opus 5.5 and Haiku 5.5** |
| `high` | A sensible minimum for intelligence-sensitive work. **The default on Sonnet 5.5** and most other current models |
| `xhigh` | Between high and max; strong for hard coding and agentic work |
| `max` | When correctness matters more than cost |

Lower effort means fewer and more consolidated tool calls, less preamble and terser answers. Higher effort means more thinking and more output tokens, so more cost and more latency.

The defaults differ by model, so set effort explicitly instead of relying on them. Two related facts to have ready: `max_tokens` caps thinking and the visible answer together, so a limit sized for the answer alone can cut the reply off; and thinking happens before the first visible token, so higher effort also raises time to first token. And judge by **cost per completed task**, not cost per request: a cheap request that needs a retry or extra turns isn't cheap.

### A design-round answer

"Your agent is too slow and too expensive" has an ordered answer:

1. **Free wins first:** cache the stable prefix, trim what you send, cap output length with a clear output spec.
2. **Lower effort on the routes that don't need it.** Classification and routing steps rarely need `high`. Measure on real requests before and after.
3. **Only then consider a smaller model,** and measure the most capable model at lower effort first. It often matches a bigger setting on routine work, and one model means one cache (caches are per model).

## How sampling works

This part is vendor-neutral. It's what "what does temperature do?" is really asking.

1. **Logits.** At each step, the model produces one score (a logit) for every token in its vocabulary. A higher score means "more likely next".
2. **Softmax.** The scores are turned into probabilities that sum to 1. Each logit is divided by the **temperature** `T`, exponentiated, and normalised: `p_i = exp(z_i / T) / sum_j exp(z_j / T)`.
3. **Sampling.** The next token is drawn at random from that distribution. Then the whole thing repeats for the next token, with the chosen token now part of the input.

Temperature reshapes the distribution before the draw. Take three candidate tokens with logits 2.0, 1.0 and 0.1:

| Temperature | Probabilities | Effect |
|---|---|---|
| 0.5 | 0.86, 0.12, 0.02 | Sharper: the top token dominates |
| 1.0 | 0.66, 0.24, 0.10 | The model's own distribution |
| 2.0 | 0.50, 0.30, 0.19 | Flatter: unlikely tokens get picked more often |

As `T` approaches 0, the draw approaches **greedy decoding**: always take the top token. Two related knobs trim the distribution instead of reshaping it. **Top-k** keeps only the `k` most likely tokens. **Top-p** (nucleus sampling) keeps the smallest set of tokens whose probabilities add up to at least `p`. Some APIs also return **logprobs**, the log-probabilities of the chosen tokens, which are useful for confidence scores in classifiers.

### Why temperature 0 still isn't fully deterministic

This is the strong-answer detail. Even with greedy decoding, the logits themselves can differ slightly between two identical requests. Hosted models run on GPUs that batch your request with other people's, and floating-point addition isn't associative: the order in which partial sums are combined depends on the batch and the hardware path, so the last digits of a logit can change. When two tokens are nearly tied, a tiny change flips which one wins. One different token early on changes everything generated after it.

So say it like this: "Temperature 0 makes outputs much more repeatable, not guaranteed identical. If I need the same answer every time, I cache the answer or constrain the output, I don't rely on sampling settings." Some vendors offer a `seed` parameter for best-effort reproducibility; check that vendor's current docs for what it promises.

## Why outputs vary on current Claude models

The model generates text by sampling tokens, as above. Two identical requests can produce different wording, different ordering, sometimes a different decision near a borderline case. With adaptive thinking, the amount of reasoning can also differ between runs.

Older advice was to lower `temperature`. On current models that lever is gone:

- On Claude Opus 5.5, `temperature`, `top_p` and `top_k` are rejected with a 400.
- On Claude Sonnet 5.5 and Claude Haiku 5.5, non-default values are rejected.

Older models still accept these parameters, which is why you'll see them in tutorials. Don't carry them into new code for current models. Assistant-message prefill, the old trick for forcing a response to start with `{`, is also rejected on current models.

## How you get consistency instead

Interviewers want to hear that you design for variance rather than wish it away.

| Technique | What it fixes |
|---|---|
| **Clear, specific prompts** | Most "random" behaviour is an ambiguous instruction. State the task, the output shape and an example. |
| **Structured outputs** | `output_config.format` with a JSON schema makes the response valid JSON that matches your schema. Shape stops varying. (Lesson 4.) |
| **Strict tools** | `strict: true` on a tool makes its arguments match the schema exactly. |
| **Enums and closed sets** | If the answer is one of five categories, make the schema an `enum`. The model can't invent a sixth. |
| **Evals** | Run a fixed set of real examples on every prompt or model change. Report pass rates, not single anecdotes. Run borderline cases more than once. |
| **Deterministic code around the model** | Validation, retries on schema failure, and business rules in code, not in the prompt. |

A strong answer to "the model gave a different answer in production": "First I'd check whether the input really was identical, including the system prompt and tools. If it was, I'd add the case to the eval set, tighten the prompt or the schema, and check the pass rate over several runs. I'd also log the `request-id` header from the API response so I can trace that exact call."

## Practice (say it out loud)

Answer out loud first (two minutes each), then open the model answer and check yourself.

**1.** "A teammate wants to add `temperature=0` to make your classifier deterministic. What do you tell them?"

<details>
<summary>Model answer and self-check</summary>

"Two things. First, on the model we're using it won't work: Opus 5.5 rejects `temperature` with a 400, and Sonnet 5.5 and Haiku 5.5 reject non-default values. Second, even where temperature 0 is accepted, it isn't fully deterministic. It makes sampling greedy, but the logits can shift slightly between runs because of batching and floating-point order on the GPU, and a near-tie can flip.

What I'd do instead: make the output a closed set with structured outputs and an `enum`, so the shape can't vary. Tighten the prompt with a clear definition and examples for each label. Then measure: run the eval set several times and look at which cases flip. Flipping cases are usually ambiguous inputs, and the fix is a clearer label definition or a 'needs review' label, not a sampling setting. If the business needs the same answer for the same input, cache the answer by input hash."

Score yourself:
- [ ] Said what happens on the current model (rejected), naming the model.
- [ ] Explained why temperature 0 isn't fully deterministic anyway.
- [ ] Offered structured outputs or an enum, a clearer prompt, and an eval run several times.
- [ ] Treated flipping cases as a signal about the data or labels.

</details>

**2.** "Your extraction step costs too much. You can change the model, the effort level or the prompt. In what order do you try them, and how do you know each change didn't hurt quality?"

<details>
<summary>Model answer and self-check</summary>

"Before changing anything, I build or reuse an eval: a few hundred real documents with known correct extractions, and a pass-rate number for the current setup. I also record cost per completed task, including retries, not just cost per request.

Then, cheapest risk first:

1. **The prompt and the context.** Cache the stable instructions, cut anything the step doesn't need, and cap the output with a tight schema. These rarely hurt quality.
2. **Effort.** Extraction is well defined, so try `low` with `output_config.effort` set explicitly. Compare pass rate and output tokens, since thinking is billed as output.
3. **The model,** last. Try a smaller model such as Haiku 5.5 at the same effort. It can be far cheaper per token, but a cheaper model that fails more often and needs retries may cost more per completed task.

After each change I rerun the eval, several runs for borderline cases, and keep the change only if the pass rate holds within the noise. I'd change one thing at a time so I know which change did what."

Score yourself:
- [ ] Set up a measurement before changing anything.
- [ ] Ordered the levers (prompt and caching, then effort, then model) and said why.
- [ ] Mentioned thinking as output cost, or cost per completed task.
- [ ] Changed one variable at a time and reran the eval each time.

</details>

> **Key takeaways**
>
> - Adaptive thinking lets the model decide how much to reason. On Opus 5.5 it can't be disabled, and old thinking budgets are rejected.
> - Effort (low, medium, high, xhigh, max) is the main cost and quality dial. Opus 5.5 and Haiku 5.5 default to medium, Sonnet 5.5 to high, so set it explicitly. `max_tokens` covers thinking too.
> - Sampling turns logits into probabilities with softmax; temperature sharpens or flattens them, top-k and top-p trim them. Temperature 0 is close to greedy but still not fully deterministic.
> - Temperature and similar parameters are rejected on the newest Claude models.
> - Get consistency from clear prompts, structured outputs, strict tools, enums and evals, and judge cost per completed task.
