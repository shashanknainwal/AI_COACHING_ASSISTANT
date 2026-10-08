---
title: "Cost at Enterprise Scale: Unit Economics and Sensitivity"
type: reading
minutes: 20
---

> **By the end of this lesson** you'll be able to turn a workload into cost per business unit (per ticket, per document, per user), test which assumptions actually move the answer, and present the cost levers in the order Anthropic's own guidance recommends.

## How this comes up in interviews

Every architecture recommendation ends with "what will it cost?" In a case round you're expected to estimate out loud, from token counts and list prices, and then say what you'd do to bring it down (Reported for applied AI design rounds generally; solutions architect loops specifically are thinly documented, Anecdotal). The architect's version of this question is different from the engineer's. An engineer optimizes the bill. An architect explains whether the project is worth doing and which assumption the business case depends on.

The Engineer track's "Cost at Scale" lesson (module E5) covers the mechanics: the four token meters, cache placement, routing and batch details. This lesson builds on that for executive conversations.

## Prices used here

Claude list prices per million tokens, from [claude.com/pricing](https://claude.com/pricing) and Anthropic's API docs, October 2026. Re-check before any customer quote.

| Model | Input | Output | Cache read |
|---|---:|---:|---:|
| Claude Opus 5.5 | $4.00 | $20.00 | $0.20 |
| Claude Sonnet 5.5 | $2.00 | $10.00 | $0.20 |
| Claude Haiku 5.5 (prompts up to 100K tokens) | $0.10 | $0.50 | not used below |

Cache writes cost 1.25x the input price for the default 5-minute lifetime. The Batch API is 50% off. Output tokens include thinking.

## Unit economics: price the business unit

Executives don't buy tokens. They buy resolved tickets, processed claims, or hours back per employee. Convert every estimate into that unit, and put it next to what the unit costs today.

### Worked example: a support assistant

**Larchmont Outfitters** (fictional retailer) handles 300,000 support tickets a month. Today each one takes an agent about 10 minutes at a fully loaded $36 an hour: **$6.00 per ticket**, $1.8M a month.

Proposed design on Sonnet 5.5: about 4 model calls per ticket. Each call sends a 10,000-token stable prefix (instructions, policies, tool definitions) that is cached, about 2,500 tokens of new conversation and tool results, and gets back about 400 tokens. To keep the arithmetic simple, the new tokens are treated as uncached; real loops also cache the growing conversation, which lowers the number.

| Line | Per call | Per ticket (x4) | Per month (300K tickets) |
|---|---:|---:|---:|
| Cached prefix: 10,000 x $0.20 / 1M | $0.0020 | $0.0080 | $2,400 |
| New input: 2,500 x $2 / 1M | $0.0050 | $0.0200 | $6,000 |
| Output: 400 x $10 / 1M | $0.0040 | $0.0160 | $4,800 |
| **Total, cached** | **$0.0110** | **$0.044** | **$13,200** |
| Same without caching (12,500 x $2 + 400 x $10) | $0.0290 | $0.116 | $34,800 |
| Opus 5.5, cached (10,000 x $0.20 + 2,500 x $4 + 400 x $20) | $0.0200 | $0.080 | $24,000 |

Now the value side. Suppose the assistant resolves 35% of tickets end to end and drafts replies for the rest, saving an agent 3 minutes each:

- Resolved: 0.35 x $6.00 = $2.10
- Drafted: 0.65 x (3 / 60 x $36) = 0.65 x $1.80 = $1.17
- **Gross saving: $3.27 per ticket. Model cost: $0.044. Net: about $3.23 per ticket**, or roughly $970,000 a month before fixed costs (engineering, operations, review).

The model is about 1% of the value it creates here. That changes which questions matter.

## Sensitivity analysis: which assumption matters?

Change one assumption at a time and watch the net saving per ticket (base: $3.226).

| Change | Net per ticket | Change vs base |
|---|---:|---:|
| Token prices up 50% | $3.204 | -0.7% |
| Calls per ticket double (4 to 8) | $3.182 | -1.4% |
| 2% of AI-resolved tickets come back and cost $15 each to fix | $3.121 | -3.3% |
| Resolution rate 35% to 25% | $2.806 | -13.0% |
| Time saved per draft 3 to 1.5 minutes | $2.641 | -18.1% |

The business case rides on resolution rate and time saved, not on token prices. So the proof of concept must measure those two numbers on real tickets (module A4), and the go/no-go threshold should be written in them. Present the table to the executive sponsor. It shows you know where the risk is.

### When token cost does dominate

Flip the workload. **Halstead Marketplace** (fictional) wants to classify 20 million product listings a month for policy violations. Each request is about 1,500 tokens in and 50 out (measure the real output, including any thinking). Value per item is a fraction of a cent.

| Model | Per item | Per month |
|---|---:|---:|
| Haiku 5.5: 1,500 x $0.10 + 50 x $0.50 per million | $0.000175 | $3,500 |
| Opus 5.5: 1,500 x $4 + 50 x $20 per million | $0.0070 | $140,000 |

That's a 40x spread. On high-volume, low-value-per-item work with checkable outputs, model choice and batch decide whether the project exists. Run the cheaper model against the eval, and price the failures it adds before you trust it.

Rule of thumb: **the lower the value per unit, the more the token bill matters.** Work out value per unit first, then decide how hard to optimize.

## The levers, in order

Anthropic's cost-optimization guidance splits levers into two kinds and puts them in a deliberate order: **free wins first** (they cut cost without touching quality), **tradeoffs last** (they exchange capability for cost and need an eval). It also frames everything as **cost per completed task**, not cost per token: failed attempts and retries count.

| Order | Lever | Kind | Typical effect | Architect's note |
|---|---|---|---|---|
| 1 | **Prompt caching** | Free | Biggest saving on repeated prefixes; above, $34,800 to $13,200 | Stays on permanently. Needs a stable prefix, so design prompts for it. |
| 2 | **Input hygiene** | Free | Removes tokens you don't need to send | Load reference material on demand instead of in every call. |
| 3 | **Output length** | Free | Output costs 5x input on these models | Specify the exact output shape. `max_tokens` is a backstop, not a tuning knob. |
| 4 | **Batch** | Free | 50% off for work nobody is waiting on | Nightly jobs, backfills, eval runs. Not for users waiting on an answer. |
| 5 | **Effort** | Tradeoff | Less thinking, lower output spend | Sweep it on the eval before changing the model. |
| 6 | **Model choice and routing** | Tradeoff | Up to 40x per-token spread | Last, because it limits capability. Compare on cost per completed task, including the hardest tasks. |

Two platform details that change the plan:

- **Batch depends on the platform.** In Anthropic's current platform availability table, the Message Batches API is listed for the Claude API and Claude Platform on AWS, but not for Amazon Bedrock, Google Vertex AI or Microsoft Foundry. Those clouds may offer their own batch options at their own prices; confirm with the vendor's current docs.
- **Residency can have a price.** The pricing page lists US-only inference at 1.1x. If the customer needs it, add it to the model and to the sensitivity table.

## Presenting cost to an executive

1. **Lead with the unit.** "About 4 cents of model cost per ticket, against $6 today."
2. **Give a range, not a point.** Low, expected and high, from the sensitivity table.
3. **Name the assumption that matters** and how the pilot will measure it.
4. **Show the full cost of ownership**, not just the API line: build, operations, human review, evaluation. Lesson 3's model does this.
5. **Say what you'd do if it runs hot**: caching, then output length, then effort, then model choice, each checked against the eval.

## Practice (say it out loud)

Original prompts in the style of a solutions architect case round:

- "An insurer processes 1 million pages a month. Estimate the model cost on two models and tell me which assumptions you're least sure of."
- "The CFO says the pilot's API bill was triple your estimate. Walk me through how you'd find out why."
- "Build me a one-slide business case for a contract-review assistant used by 400 lawyers."

> **Key takeaways**
>
> - Price the business unit (ticket, document, user) and put it next to today's cost per unit.
> - Run a one-at-a-time sensitivity table. On most service workloads, resolution rate and time saved matter far more than token prices.
> - When value per item is tiny and volume is huge, the token bill and model choice decide the project.
> - Pull levers in order: caching, input hygiene, output length, batch, then effort, then model choice, measured as cost per completed task.
> - Check platform availability (batch) and price multipliers (US-only inference) before you promise a saving.
