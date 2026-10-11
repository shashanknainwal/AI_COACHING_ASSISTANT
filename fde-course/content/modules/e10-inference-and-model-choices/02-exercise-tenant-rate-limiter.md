---
title: "Exercise: Token Buckets, Priorities and Cost per Tenant"
type: exercise
minutes: 45
hints:
  - "`TokenBucket`: write one private helper that refills for the time since `self.updated` (capped at `capacity`) and moves `self.updated` forward. Call it at the start of `available`, `try_take` and `adjust`."
  - "`submit`: check tenant, priority and model first. A request reserves `input_tokens + max_tokens`; if that is more than the tenant bucket's capacity or the pool's capacity it can never be admitted, so reject it now instead of letting it wait forever."
  - "`effective_priority`: `PRIORITY[...] - int(waited // AGING_SECONDS)`, floored at 0. In `drain`, sort the queue by `(effective_priority, _seq)` so ties go to the earlier arrival."
  - "`drain`: keep two sets, blocked tenants and blocked pools. When a request doesn't fit its tenant's buckets, block that tenant for the rest of this pass; when it doesn't fit the model pool, block that pool. Skip anything whose tenant or pool is blocked. Take from all three buckets only after all three checks pass."
  - "`complete`: tokens used are input + cache writes + output (cache reads don't count toward the limit). Adjust both the tenant bucket and the pool by `reserved - used`. Price every usage field, cache reads included, at the model's own rate, and round to 6 decimals."
---

Noor Haddad runs the ML platform at Lumenfold Media, a fictional company that sells AI writing and tagging features to about 300 publishers. Every publisher is a tenant, and every tenant's traffic goes through one gateway to the Claude API. Last week one tenant's overnight re-tagging job took the whole Sonnet 5.5 rate limit for 40 minutes, and every other tenant's editors saw 429s. Noor and Lumenfold are fictional.

You'll build the gateway's admission control in plain Python. Each tenant gets token buckets, and each model has one shared pool that mirrors the organisation's upstream limit. Waiting requests go into a priority queue that ages, so batch work can't starve forever. The gateway also attributes the cost of every finished call to the tenant that made it. Time is passed in as `now` (seconds), so tests are deterministic.

This is the core of the "multi-tenant gateway" question you met in E6, built for real. The design round in lesson 03 goes one layer lower, into how the model is served.

## Your task

**1. `TokenBucket(capacity, refill_per_sec, now)`** starts full.

- `available(now)`: refill for the time since the last update, never above `capacity`, then return the tokens.
- `try_take(amount, now)`: if `amount` is available, take it and return `True`; otherwise take nothing and return `False`.
- `adjust(delta, now)`: add `delta` (a refund) or subtract it (an overrun). The result may go negative (a debt that refills over time) but never above `capacity`.

**2. `Gateway(tenants, pools)`.** `__init__` is given. Each tenant has a tokens-per-minute bucket and a requests-per-minute bucket. Each model has a pool bucket.

- `submit(req, now)`: raise `ValueError` for an unknown tenant (`"unknown tenant: <name>"`), priority (`"unknown priority: ..."`) or model (`"unknown model: ..."`), and for a request whose reservation (`input_tokens + max_tokens`) is larger than the tenant's or the pool's capacity (the message contains `"never fit"`). Otherwise append a copy to `self.queue` with `_seq` (1, 2, 3, ...) and `_arrived` (`now`). Return `None`.
- `effective_priority(queued, now)`: the request's `PRIORITY` minus one level per full `AGING_SECONDS` waited, never below 0.
- `drain(now)`: go through the queue sorted by `(effective_priority, _seq)`. Admit a request when its tenant has the tokens and one request available **and** its model pool has the tokens. Then take from all three buckets and move it to `self.in_flight[id] = (request, reserved)`. Two rules keep it fair:
  - If a request doesn't fit its **tenant's** buckets, skip every later request from that tenant in this pass.
  - If it doesn't fit the **model pool**, skip every later request for that model in this pass, so a small batch job can't slip past a waiting interactive one.

  Return the admitted ids in order.
- `complete(req_id, usage, now)`: raise `ValueError("unknown request: ...")` if it isn't in flight. Tokens used = `input_tokens + cache_creation_input_tokens + output_tokens`. Cache reads don't count, as upstream on most models. Adjust the tenant's token bucket and the pool by `reserved - used`. Price the call from `PRICES` (cache writes at `cache_write_5m`), round it to 6 decimals, add it to the tenant's spend and return it.
- `costs()`: `{tenant: spend rounded to 6 decimals}`.

Example: with a 50,000-token Sonnet pool, a batch request reserving 28,000 and an interactive one reserving 8,000 are both admitted at `t=0`, interactive first. A second 28,000 batch request waits until the pool refills.

Press **Run** to watch the demo, then **Submit**.

## Defend it

These are original practice questions in the style of a design round:

- "Why reserve `max_tokens` instead of an average?" You only learn the output length when the call ends. Reserving the worst case keeps the bucket honest, and the refund in `complete` gives back what wasn't used. On thinking models `max_tokens` includes thinking, so the worst case is real.
- "Where does this state live when you run 20 gateway nodes?" Options include a shared store with atomic decrements, or local buckets with leases from a central allocator. Say which you'd fail open or closed for each priority class.
- "Why do cache reads not count here?" Lumenfold mirrors the upstream rule: on most models, cache reads don't count toward the input-tokens-per-minute limit. Check the current rate-limit docs before you promise a customer that.
- "Why not use the API's Priority Tier for interactive traffic?" Check the docs for your model first. The skill's migration notes say Priority Tier is not supported on Opus 5.5, Sonnet 5.5 or Fable 5.1. Your own queue is what protects interactive traffic.
