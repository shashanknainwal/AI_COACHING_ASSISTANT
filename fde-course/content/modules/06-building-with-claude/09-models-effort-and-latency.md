---
title: "Choosing Models, Effort, and Latency Budgets"
type: reading
minutes: 14
---

> **By the end of this lesson you will be able to:**
> - Pick a model and effort level per task based on quality, latency, and cost
> - Account for real differences between models (parameters, context windows)
> - Design a simple router and a fallback chain
> - Explain your choices to a customer in business terms

## One application, many kinds of requests

Harbor Bank's assistant doesn't do one thing. In a single day it will:

- classify 4,000 incoming tickets (short, simple, high volume),
- chat with agents (interactive, latency matters),
- extract fields from loan documents (accuracy matters),
- analyze a week of complaints for the compliance team (hard reasoning, nobody waiting).

Using one model and one setting for all of these either overpays for the easy tasks or underperforms on the hard ones. A **router** picks the configuration per task.

## The three dials

| Dial | Options | Affects |
|---|---|---|
| **Model** | Opus 5.5, Sonnet 5.5, Haiku 4.5 | Capability, price, speed |
| **Effort** | low → max (on models that support it) | Depth of reasoning, output tokens, latency |
| **max_tokens and streaming** | small for classifications, large and streamed for long outputs | Truncation risk, timeouts |

A reasonable starting table for Harbor Bank:

| Task | Model | Effort | max_tokens | Why |
|---|---|---|---|---|
| classify | Sonnet 5.5 | low | 1,024 | High volume, simple, tested against an eval set |
| chat | Opus 5.5 | low | 16,000 | Quality matters; low effort keeps replies fast |
| extract | Opus 5.5 | medium | 16,000 | Accuracy matters more than speed |
| analyze | Opus 5.5 | high | 64,000 (streamed) | Hard reasoning; nobody waiting |

These are **starting points**. The real answer comes from your evaluation set (Module 8): try cheaper configurations and keep them only if quality holds.

## Models aren't interchangeable

Swapping a model ID isn't always a drop-in change. Real differences include:

- **Supported parameters.** The `effort` setting works on current Opus and Sonnet models but returns an error on Claude Haiku 4.5. A router must build parameters per model, not just swap the ID.
- **Context windows.** Claude Opus 5.5 and Sonnet 5.5 accept up to 1 million input tokens; Claude Haiku 4.5 accepts 200,000. Route very long inputs accordingly.
- **Behavior.** Prompts tuned on one model may need adjustment on another. Re-run your evaluation whenever you change models.

## Latency budgets

Some features have a hard latency budget. An agent-assist suggestion that arrives after the customer hangs up is worthless. For these:

- Prefer **lower effort** first (less thinking before the answer starts).
- Consider a **smaller, faster model** for simple tasks with tight budgets.
- **Stream** so the first words appear quickly.
- **Measure** the 50th and 95th percentile latency on real traffic, not just one test request.

## Fallback chains

What if a model is temporarily overloaded? The SDK retries automatically, but after retries are exhausted you have a choice: fail, or fall back to another model.

```
claude-opus-5-5  ──overloaded──►  claude-sonnet-5-5  ──overloaded──►  fail clearly
```

Fallbacks keep a feature available during incidents, at a possible quality cost. Decide **per task** whether that's acceptable: a fallback for chat is usually fine; a fallback for compliance analysis might not be, and could instead queue the work for later. Record which model actually served each request, so quality metrics aren't silently mixed.

(Separately from availability fallbacks, Claude Opus 5.5 supports server-side fallbacks for refused requests, mentioned in lesson 7.)

## Explaining choices to the customer

Customers rarely care which model ID you use. They care about outcomes. Frame decisions in their terms:

> "Ticket classification runs on a faster, lower-cost configuration that matched the larger model's accuracy on 500 of your labeled tickets (96% vs 97%). That saves about $1,400 a month at your volume. Agent chat and document extraction use the most capable model, because accuracy there drives customer outcomes."

That's a decision an executive can approve, backed by numbers you measured.

> **Key takeaways**
> - Route by task: model, effort, and max_tokens/streaming are separate dials.
> - Start from the most capable configuration and step down only when an evaluation shows quality holds.
> - Models differ in supported parameters and context windows; build parameters per model.
> - Use fallback chains deliberately per task, record which model served each request, and explain choices in business terms.
