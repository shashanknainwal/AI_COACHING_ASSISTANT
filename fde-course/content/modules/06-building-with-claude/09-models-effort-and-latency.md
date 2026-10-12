---
title: "Choosing Models, Effort, and Latency Budgets"
type: reading
minutes: 7
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
| **Model** (Opus 5.5, Sonnet 5.5, Haiku 5.5) | Capability, price, speed: Haiku 5.5 is 20× cheaper than Sonnet 5.5 and 40× cheaper than Opus 5.5 |
| **Effort** (low → max) | Reasoning depth, thinking tokens (billed as output), latency. Defaults: `medium` on Opus 5.5 and Haiku 5.5, `high` on Sonnet 5.5 |
| **max_tokens and streaming** | Truncation risk, timeouts |

A starting table for Harbor Bank:

| Task | Model | Effort | max_tokens | Why |
|---|---|---|---|---|
| classify | Haiku 5.5 | low | 2,048 | High volume, simple, eval-tested; try it before Sonnet |
| chat | Opus 5.5 | low | 16,000 | Quality matters; low effort keeps it fast |
| extract | Opus 5.5 | medium | 16,000 | Accuracy over speed |
| analyze | Opus 5.5 | high | 64,000 (streamed) | Hard reasoning; nobody waiting |

Starting points only: keep a cheaper configuration if your evaluation set (Module 8) says quality holds.

## Models aren't interchangeable

- **Parameters:** `effort` works on Opus 5.5, Sonnet 5.5 and Haiku 5.5. The legacy Claude Haiku 4.5 rejects it, so if a customer still runs Haiku 4.5, build parameters per model rather than just swapping the ID.
- **Defaults differ:** with no `effort`, Sonnet 5.5 runs at `high` and the others at `medium`. All three think by default, and `max_tokens` covers the thinking. Set `effort` explicitly in every route so cost and latency don't change when you swap models.
- **Pricing tiers:** Haiku 5.5 bills a prompt over 100K tokens at $0.50/$2.50 instead of $0.10/$0.50. Long-document work is still cheap on Haiku 5.5, but price it on the right card.
- **Context windows:** Opus 5.5, Sonnet 5.5 and Haiku 5.5 all accept 1 million tokens; only the legacy Haiku 4.5 is limited to 200,000.
- **Thinking blocks across models:** a router that moves a multi-turn conversation from Opus 5.5 to another model runs the later turns without Opus 5.5's earlier reasoning. Route per conversation, not per turn, when that matters.
- Re-run your evaluation whenever you change models.

## Latency budgets

A suggestion that arrives after the caller hangs up is worthless. Thinking happens before the first visible token, so effort drives time-to-first-token as well as total time. Lower effort first, then a smaller model for simple tasks; stream; measure p50 and p95 on real traffic.

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
> - Set effort explicitly per route; defaults and long-prompt pricing differ by model.
> - Choose fallbacks per task, record the serving model, explain in business terms.
