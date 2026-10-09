---
title: Thinking, Effort and Why Outputs Vary
type: reading
minutes: 16
---

> **By the end of this lesson** you'll be able to explain adaptive thinking and the effort parameter, say why the same prompt can return different answers, and describe how you get consistent behaviour on current Claude models without reaching for temperature.

## How this comes up in an interview

Two kinds of question tend to land here. In a design round: "Your agent is too slow and too expensive. What knobs do you have?" In a fundamentals or project deep dive: "The model gave a different answer to the same input in production. Why, and what did you do about it?"

A weak answer says "set temperature to zero". On the newest Claude models that request is rejected outright. A strong answer talks about effort, prompts, structured outputs and evals. This lesson gives you that answer. Practice prompts here are original, written in the style of these rounds.

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
| `medium` | Cost-saving step-down where quality still holds. **The default on Opus 5.5** |
| `high` | A sensible minimum for intelligence-sensitive work. The default on most other current models |
| `xhigh` | Between high and max; strong for hard coding and agentic work |
| `max` | When correctness matters more than cost |

Lower effort means fewer and more consolidated tool calls, less preamble and terser answers. Higher effort means more thinking and more output tokens, so more cost and more latency.

The defaults differ by model, so set effort explicitly instead of relying on them. And judge by **cost per completed task**, not cost per request: a cheap request that needs a retry or extra turns isn't cheap.

### A design-round answer

"Your agent is too slow and too expensive" has an ordered answer:

1. **Free wins first:** cache the stable prefix, trim what you send, cap output length with a clear output spec.
2. **Lower effort on the routes that don't need it.** Classification and routing steps rarely need `high`. Measure on real requests before and after.
3. **Only then consider a smaller model,** and measure the most capable model at lower effort first. It often matches a bigger setting on routine work, and one model means one cache (caches are per model).

## Why outputs vary

The model generates text by sampling tokens. Two identical requests can produce different wording, different ordering, sometimes a different decision near a borderline case. With adaptive thinking, the amount of reasoning can also differ between runs.

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

- "A teammate wants to add `temperature=0` to make your classifier deterministic. What do you tell them?"
- "Your extraction step costs too much. You can change the model, the effort level or the prompt. In what order do you try them, and how do you know each change didn't hurt quality?"

> **Key takeaways**
>
> - Adaptive thinking lets the model decide how much to reason. On Opus 5.5 it can't be disabled, and old thinking budgets are rejected.
> - Effort (low, medium, high, xhigh, max) is the main cost and quality dial. Opus 5.5 defaults to medium, so set it explicitly.
> - Outputs vary because the model samples. Temperature and similar parameters are rejected on the newest models.
> - Get consistency from clear prompts, structured outputs, strict tools, enums and evals, and judge cost per completed task.
