---
title: "Capacity and Commercials: Peak Load, Priority Tier, Commits and Marketplaces"
type: reading
minutes: 22
---

> **By the end of this lesson** you'll be able to size a workload against rate limits at peak (requests, input tokens and output tokens per minute, per model and platform), explain what Priority Tier is and why you probably won't sell it, describe how marketplace billing and private offers work on Claude Platform on AWS and Foundry, and talk about commits and seat versus usage pricing without promising terms that aren't yours to give.

## How this comes up in the job

Two questions end most architecture reviews: "Will it hold up on our busiest day?" and "How do we buy it?" The first is yours to answer with arithmetic. The second belongs to the account team, but the architect supplies the forecast it rests on, and a bad forecast turns into a bad contract.

Everything specific below comes from Anthropic's [rate limits](https://platform.claude.com/docs/en/api/rate-limits), [service tiers](https://platform.claude.com/docs/en/api/service-tiers) and [pricing](https://platform.claude.com/docs/en/about-claude/pricing) pages, checked in October 2026. Anything marked **General practice** is common industry practice, not an Anthropic policy. Re-check the docs before you quote a customer.

## How rate limits work on the Claude API

- **Three meters per model:** requests per minute (RPM), input tokens per minute (ITPM) and output tokens per minute (OTPM). Exceed any one and you get a `429` with a `retry-after` header that says which limit you hit.
- **Per model, not per account.** Each model has its own limits, so you can run different models up to their own limits at the same time. Current models such as Opus 5.5 and Sonnet 5.5 each have a separate pool. Moving traffic to a new model doesn't bring headroom with it.
- **Token bucket.** Capacity refills continuously rather than resetting each minute. A limit of 60 RPM may be enforced as one request per second, so short bursts can trip it even when the per-minute average is fine.
- **Cache reads don't count toward ITPM on most models.** Only uncached input tokens and cache writes count. The docs' own example: with a 2,000,000 ITPM limit and an 80% cache hit rate, you can process about 10,000,000 total input tokens a minute. Caching is a capacity lever as well as a cost lever.
- **OTPM counts tokens actually generated**, not `max_tokens`. Setting a high `max_tokens` costs nothing in rate-limit terms. But thinking tokens are output tokens: a model running at a higher `effort` uses more OTPM.
- **Acceleration limits.** A sharp jump in usage can return `429`s even below your limits. Ramp traffic gradually.
- **US-only and global inference share one pool.** `inference_geo: "us"` doesn't give you separate capacity.
- **Tiers.** Organisations are placed on a usage tier (Start, Build, Scale) with standard limits and a monthly spend cap ($500, $1,000 and $200,000 respectively). Above Scale, the Custom tier has limits arranged with the account team and no monthly spend cap. Hitting the spend cap returns a `429` without `retry-after`, with `error.details.error_code` set to `enforced_spend_limit_reached`: retrying won't help.
- **Workspaces** can be given lower limits to protect other teams from a noisy neighbour; organisation limits always apply on top.

### On other platforms

- **Claude Platform on AWS:** the same rate-limit model, but organisations start on the Start tier and move up as they build a history of paid AWS Marketplace invoices. There's no self-service tier increase; you ask the Anthropic account representative or support, with the models, the peak input and output tokens per minute for each, and roughly what share of input is cached. Per-workspace rate limits aren't available there.
- **Amazon Bedrock:** quotas are set by AWS. Module A2 lesson 01 has the defaults it documents and the increases customers can request.
- **Microsoft Foundry:** doesn't return Anthropic's `anthropic-ratelimit-*` headers, so monitoring and backoff use Azure's tooling.
- **Google Cloud:** quotas are managed in Google Cloud.

Whatever the platform, the numbers you plan against come from the customer's own console or quota page on the day, not from a table in a slide deck.

## Planning for peak

Average load doesn't break systems. Peak does. The method:

1. **Start from the business event.** Calls per hour on the busiest hour of the busiest day (Monday 9am after a holiday, month-end close, a storm for an insurer), not the monthly average.
2. **Convert to model calls per minute.** One user action often triggers several model calls in an agent loop.
3. **Per call, split the input** into cache reads (don't count toward ITPM on most models), cache writes and uncached input (both count). Estimate output including thinking at the `effort` you'll actually run.
4. **Multiply** to get peak RPM, counted ITPM and OTPM for each model.
5. **Compare with the limits per model and per platform or region,** and flag anything over the limit, and anything above your headroom target. **General practice:** plan to stay below roughly 70 to 80% of a limit at forecast peak, because forecasts are wrong, retries add load, and token buckets punish bursts.
6. **Decide what to do about each breach:** request higher limits early (it takes time), improve caching, spread load across models or regions where the residency rules allow, move work nobody is waiting for to the Batches API where the platform has it, or shape traffic with a queue.

The exercise in the next lesson builds this calculation.

## Priority Tier: know it, and know it's closed to new buyers

Anthropic's service tiers page describes three tiers: **Standard** (the default), **Batch** (asynchronous, 50% off), and **Priority Tier**. The page also says, at the top, that **Priority Tier capacity commitments are no longer available for purchase.** Organisations with an existing commitment can keep using it until their contract ends. For guaranteed capacity, the page says to contact sales.

You still need to understand it, because existing customers have it and because the mechanics show how capacity commitments are measured.

- **What it was:** a commitment to a number of input tokens per minute and output tokens per minute, for a duration of 1, 3, 6 or 12 months, on a specific model version. Requests in it are prioritised over other traffic, with a 99.5% uptime target. Requests beyond the commitment fall back to standard tier automatically.
- **Model support:** not supported on several current models, including Claude Opus 5.5, Sonnet 5.5, Haiku 5.5 and Fable 5.1. A customer with a commitment on an older model loses it when they migrate. Put that in the upgrade plan.
- **Requests use both pools.** A Priority Tier request draws from the commitment and from the regular rate limits.
- **The `service_tier` parameter:** `"auto"` (the default) uses Priority Tier capacity if available and falls back otherwise; `"standard_only"` never uses it. The response's `usage.service_tier` says which tier served the request, and `anthropic-priority-*` headers show the commitment's remaining capacity.

**Burn-down.** Usage counts against a Priority Tier commitment at rates that reflect relative pricing:

| Token type | Counts as |
|---|---|
| Cache read | 0.1 token per token |
| Cache write, 5-minute TTL | 1.25 tokens per token |
| Cache write, 1-hour TTL | 2.00 tokens per token |
| Other input | 1 token per token |
| Output | 1 token per token |
| `inference_geo: "us"` on Claude 4.6 and later | 1.1 tokens per token (input and output) |

So, unlike the standard ITPM limit, cache reads do count here, at a tenth. A design with a large cached prefix burns far less commitment than the same tokens uncached. If a customer asks you for "reserved capacity" today, don't describe Priority Tier as something they can buy. Say what the docs say, and bring in the account team.

## Commits, marketplaces and private offers

### Direct: volume discounts and custom limits

Anthropic's pricing page says volume discounts may be available for high-volume users, negotiated case by case, and that enterprise arrangements can include custom rate limits. That's all the public docs say. The terms are the account team's.

**General practice** across cloud and software vendors: a committed-spend agreement trades a minimum spend over a term for a discount or other terms. The risks for the customer are over-committing (paying for unused spend) and under-forecasting (running out of headroom). The architect's contribution is a forecast with a range, built from the unit economics in A3 lesson 04 and the peak plan above, with the assumptions written down.

### Through a cloud marketplace

- **Claude Platform on AWS** bills through **AWS Marketplace** in Claude Consumption Units (CCUs). Usage is rated in USD at standard prices, any negotiated discount is applied, and the result is converted at **$0.01 per CCU**. Metering is hourly; invoices are monthly, in arrears, with no prepaid credits. Discounts show up as fewer CCUs, not a lower CCU price.
- **Private offers on AWS.** When a customer signs up for Claude Platform on AWS in the AWS Console, the console looks up any private offer for their account and prompts them to accept it. Terms come from the Anthropic account representative. If they already have an Amazon Bedrock private offer, they should contact their Anthropic or AWS representative before starting, and discounts can't be applied retroactively to usage before the offer is accepted. That last sentence is worth saying out loud early in a deal.
- **Microsoft Foundry** bills through **Azure Marketplace** in CCUs on the same model.
- **Amazon Bedrock** and **Google Cloud** are billed by the cloud provider as their own services.

Customers often ask whether marketplace spend counts toward their existing cloud commitment. That's a question for their cloud account team, under their cloud agreement. Don't answer it.

## Seat versus usage pricing

Anthropic sells two shapes of product, and customers mix them up:

- **Usage-based:** the API (on any platform) is billed per token. Cost scales with volume and design choices such as caching, model choice and `effort`.
- **Seat-based:** Claude apps for organisations (such as the Team and Enterprise plans) are sold per user. Check [claude.com/pricing](https://claude.com/pricing) and the account team for current plans and terms.

**General practice** for advising the customer:

| Question | Points toward |
|---|---|
| Are employees using Claude directly to do their own work? | Seats |
| Is Claude a component inside your own application or pipeline? | Usage (API) |
| Is usage per person spiky and hard to forecast, and do you want a predictable budget? | Seats, or usage with spend limits and alerts |
| Is volume large and repetitive with stable prompts? | Usage, where caching and batch cut cost |

Many enterprises need both: seats for knowledge workers, API usage for the systems their engineers build. Say which is which in your design, and route the pricing conversation to the account team.

## What the architect says, and doesn't

| Say | Don't say |
|---|---|
| "At forecast peak you need about X ITPM on this model; here's the arithmetic and the assumptions." | "You'll be fine on rate limits." |
| "Cache reads don't count toward ITPM on most models, so caching raises effective throughput." | "Caching gives you unlimited throughput." |
| "Priority Tier isn't available for new purchase; for guaranteed capacity, let's bring in the account team." | "We'll put you on Priority Tier." |
| "Private offer terms come from our account team; discounts aren't retroactive, so let's sort it before usage starts." | "You'll get 30% off." |
| "Whether it counts toward your cloud commitment is a question for your cloud account team." | "Yes, it burns down your AWS commit." |

> **Key takeaways**
> - Rate limits are per model and per meter (RPM, ITPM, OTPM), enforced as a token bucket. Cache reads don't count toward ITPM on most models; thinking tokens do count as output.
> - Plan for peak from the business event, split input into cached and counted, include thinking in output, compare per model and platform, and keep headroom. Request increases early.
> - Priority Tier is no longer sold. Existing commitments burn down at documented rates (cache read 0.1, 5-minute write 1.25, 1-hour write 2.0, US-only 1.1) and it isn't supported on current 5.x models such as Opus 5.5 and Sonnet 5.5.
> - Claude Platform on AWS and Foundry bill through their marketplaces in CCUs ($0.01 each, discounts as fewer CCUs). AWS private offers are accepted in the console; discounts aren't retroactive.
> - Volume discounts and custom limits are negotiated by the account team. The architect brings the forecast and never promises terms.
