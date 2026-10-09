---
title: "Exercise: A Model Router With a Daily Budget"
type: exercise
minutes: 40
hints:
  - "`route`: start from `r = dict(ROUTES[task])`. For `complexity == \"high\"`, Opus gets `effort = \"high\"`; any other model becomes `LADDER[LADDER.index(r[\"model\"]) + 1]`. Then, if the model is Haiku and `input_tokens > HAIKU_MAX_INPUT`, switch to Sonnet."
  - "`call_cost`: build a list of `(token_count, rate_key)` pairs: input, output, cache_read, then either the two TTL counts from `usage[\"cache_creation\"]` or all of `cache_creation_input_tokens` at `cache_write_5m`. Skip pairs with 0 tokens; raise if a needed key is missing from the model's rates."
  - "`worst_case_cost`: `(input_tokens * rates[\"input\"] + r[\"max_tokens\"] * rates[\"output\"]) / 1_000_000`, rounded to 6 decimals."
  - "`admit`: `left = self.daily_budget_usd - self._day(day)[\"spent\"]`. If the normal route's worst case fits, return `dict(r, degraded=False)`. For a degradable task, try `reversed(LADDER[:LADDER.index(r[\"model\"])])`, skipping Haiku for prompts over 100K tokens."
  - "`report`: per task keep `cost` and `completed`. `cost_per_completed` is `round(cost / completed, 6)`, or `None` when nothing completed. Failed attempts still add to `cost`."
---

Leo again. Ledgerline's CFO saw last month's bill and asked a fair question: "Why does every request go to the most expensive model, and what stops a bad day from costing ten times a good one?" Their workload is four tasks: classifying inbound vendor emails, extracting invoice fields, drafting replies to vendors, and auditing payment anomalies.

You'll build two things the CFO can understand. A **router** that sends each task to the cheapest model that does it well (the routes in `ROUTES` came from their eval sweep), and a **budget guard** that prices every call from its real `usage`, enforces a daily cap, and reports **cost per completed task**, the number that actually matters. This is plain Python: the guard sits in front of whatever client code makes the call.

`PRICES` (US dollars per million tokens), `ROUTES`, `LADDER`, `DEGRADABLE` and `BudgetExceeded` are given. Haiku's cache prices are left out of the table on purpose; your code must refuse to guess them.

## Your task

**1. `route(task, input_tokens, complexity="normal")`** returns a **copy** of `ROUTES[task]` (unknown task: `ValueError("unknown task: <task>")`), then:

- `complexity == "high"`: move one step up `LADDER` (Haiku to Sonnet, Sonnet to Opus), keeping effort and `max_tokens`. Opus is already at the top, so set its effort to `"high"` instead.
- If the result is Haiku and `input_tokens > 100_000` (`HAIKU_MAX_INPUT`), use Sonnet. Haiku 5.5's listed price applies to prompts up to 100K tokens.

**2. `call_cost(model, usage, prices=PRICES, batch=False)`** prices one call from its usage dict, rounded to 6 decimals. Missing fields count as 0.

| Usage field | Rate key |
|---|---|
| `input_tokens` | `input` |
| `output_tokens` | `output` |
| `cache_read_input_tokens` | `cache_read` |
| `cache_creation_input_tokens` | `cache_write_5m`, unless... |
| `cache_creation: {"ephemeral_5m_input_tokens", "ephemeral_1h_input_tokens"}` | ...this breakdown is present: price each part at `cache_write_5m` and `cache_write_1h` |

`batch=True` multiplies the total by `BATCH_DISCOUNT`. Raise `ValueError("no prices for <model>")` for an unknown model, and `ValueError("no <rate_key> price for <model>")` when a token type has a nonzero count but no rate. Silently pricing tokens at $0 is how cost dashboards lie.

**3. `worst_case_cost(r, input_tokens, prices=PRICES)`**: the most this call could cost before you send it. Every input token uncached, output all the way to `max_tokens`. Round to 6 decimals.

**4. `BudgetGuard(daily_budget_usd, prices=PRICES)`** (`__init__`, `_day` and `spent` are given). Each `day` key (`"2026-10-30"`) has its own budget.

- `admit(task, input_tokens, day, complexity="normal")`: get the route. If its worst case fits in what's left today, return it with `"degraded": False`. Otherwise, if the task is in `DEGRADABLE`, try the cheaper models below it on `LADDER`, most capable first (never Haiku for a prompt over 100K tokens), and return the first that fits, keeping effort and `max_tokens`, with `"degraded": True`. If nothing fits, raise `BudgetExceeded` with the task name in the message. Anomaly audits are never downgraded.
- `record(day, task, model, usage, completed, batch=False)`: add the call's actual cost to the day and return it.
- `report(day)`:

```python
{"spent": 0.071024, "remaining": 0.928976,
 "by_model": {"claude-haiku-5-5": 0.001844, "claude-sonnet-5-5": 0.02918, "claude-opus-5-5": 0.04},
 "cost_per_completed": {"extract_invoice": 0.004012, "draft_reply": 0.023, "audit_anomaly": None}}
```

`cost_per_completed` divides **all** of a task's spend, failures included, by the number of completed tasks (`None` if none completed).

Press **Run** to replay a day of Ledgerline traffic with a $0.30 cap, then **Submit**.

## Defend it

Original practice questions for the design round:

- "Your extraction route is cheap per call. Why is its cost per completed task almost eight times the cost of the call that worked?" Look at the failed attempt that ran to `max_tokens` and the retry on a bigger model.
- "Two hundred requests pass `admit` in the same second and together overspend. How do you fix it?" Reserve the worst case at admission and release the difference at `record`, inside one lock or one atomic counter.
- "Why price the worst case instead of the expected cost?" A cap only works if it holds on the expensive days. Expected cost is for forecasting.
- "Why is a router not free?" Each model has its own prompt cache, so splitting traffic splits cache hits. Every route is also one more thing to evaluate.
