---
title: "Choosing Models, Effort, and Latency Budgets"
type: reading
minutes: 5
---

> **By the end of this lesson you will be able to:**
> - Pick a model and effort per task on quality, latency and cost
> - Account for real differences between models
> - Design a router and a fallback chain
> - Explain your choices in business terms

In one day Harbor Bank's assistant will classify 4,000 tickets, chat with agents mid-call, extract fields from loan documents, and analyze a week of complaints for compliance. Priya will ask why each costs what it does. A **router** picks the configuration per task.

## The three dials

| Dial | Affects |
|---|---|
| **Model** (Opus 5.5, Sonnet 5.5, Haiku) | Capability, price, speed |
| **Effort** (low → max, where supported) | Reasoning depth, output tokens, latency |
| **max_tokens and streaming** | Truncation risk, timeouts |

A starting table for Harbor Bank:

| Task | Model | Effort | max_tokens | Why |
|---|---|---|---|---|
| classify | Sonnet 5.5 | low | 1,024 | High volume, simple, eval-tested |
| chat | Opus 5.5 | low | 16,000 | Quality matters; low effort keeps it fast |
| extract | Opus 5.5 | medium | 16,000 | Accuracy over speed |
| analyze | Opus 5.5 | high | 64,000 (streamed) | Hard reasoning; nobody waiting |

Starting points only: keep a cheaper configuration if your evaluation set (Module 8) says quality holds.

## Models aren't interchangeable

- **Parameters:** `effort` works on current Opus, Sonnet and Haiku 5.5 models but returns an error on Claude Haiku 4.5. Build parameters per model, don't just swap the ID.
- **Context windows:** Opus 5.5, Sonnet 5.5 and Haiku 5.5 accept 1 million tokens; Haiku 4.5 accepts 200,000. Route long inputs accordingly.
- Re-run your evaluation whenever you change models.

## Latency budgets

A suggestion that arrives after the caller hangs up is worthless. Lower effort first, then a smaller model for simple tasks; stream; measure p50 and p95 on real traffic.

## Fallback chains

When an overloaded model exhausts the SDK's retries, fail or fall back:

```
claude-opus-5-5  ──overloaded──►  claude-sonnet-5-5  ──overloaded──►  fail clearly
```

Decide **per task**: falling back is usually fine for chat; for compliance analysis, queueing may be better. Record which model served each request so quality metrics aren't silently mixed.

## Explaining choices to the customer

> "Ticket classification runs on a faster, lower-cost configuration that matched the larger model's accuracy on 500 of your labeled tickets (96% vs 97%). That saves about $1,400 a month at your volume. Agent chat and document extraction use the most capable model, because accuracy there drives customer outcomes."

> **Key takeaways**
> - Model, effort and max_tokens/streaming are separate dials; route per task.
> - Step down from the most capable configuration only when evals show quality holds.
> - Build parameters per model; context windows differ.
> - Choose fallbacks per task, record the serving model, explain in business terms.
