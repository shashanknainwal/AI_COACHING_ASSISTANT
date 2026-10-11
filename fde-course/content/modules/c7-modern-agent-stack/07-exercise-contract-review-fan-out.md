---
title: "Exercise: Fan Out a Contract Review, Then Prove It Paid Off"
type: exercise
minutes: 50
hints:
  - "Build `worker_request` and `run_worker` first and get CC-102 passing. A worker here is one call, not a tool loop: one contract in, one structured report out."
  - "The budget gate runs before you spend anything: `client.messages.count_tokens(model=..., system=..., messages=...)` returns an object with `input_tokens`. Over `budget` means status `skipped`, error `over_budget`, zero usage, and no `messages.create` call."
  - "`run_worker` never raises. Catch `anthropic.APIError` (the SDK has already retried) and return status `failed` with the exception's class name. Check `stop_reason` before parsing, and reject a report whose `contract_id` isn't the one you sent."
  - "Rules belong in code. `assess` decides what's risky from the extracted fields; the model only extracts. `merge` sorts each result into flagged, clean, failed or skipped, so a gap can never look like a clean contract."
  - "For `compare`, run `assess` over the baseline's reports too. Then find the contract IDs the baseline never mentioned: `set(CONTRACTS) - {ids it reported}`."
---

Rhea's procurement team renews twenty carrier contracts every autumn. "Someone reads all twenty, fills in a spreadsheet and flags the risky ones. Last year they missed an auto-renewal with 120 days' notice, and we were locked in for another year. Engineering wants to paste all twenty into one big Opus call. I've heard sub-agents are cheaper and more reliable. Prove it. Show me cost and accuracy side by side, and show me what happens when one worker fails."

The 20 fictional contracts (`CONTRACTS`), the answer key (`TERMS`, `TRUTH_RISKY`), `REPORT_SCHEMA`, `WORKER_MODEL` (Haiku 5.5), `LEAD_MODEL` (Opus 5.5), `WORKER_SYSTEM`, `LEAD_SYSTEM`, `WORKER_BUDGET`, `PRICES` and `run_single_agent(client)` (the baseline) are given. In this simulation, CC-117's worker calls fail with 529 Overloaded every time, CC-113 carries a huge rate-table appendix, and the single long-context baseline is scripted to skip three contracts from the middle. That last one is a failure mode you would measure on real runs, not assume. The capstone kit has the version that calls the real API.

## Your task

**1. `worker_request(contract_id, text)`** returns request parameters: `WORKER_MODEL`, `max_tokens` of at least 1000 (it covers thinking), `WORKER_SYSTEM`, `output_config` with `"effort": "low"` and a `json_schema` format using `REPORT_SCHEMA`, and one user message holding only this contract in `<contract id="...">` tags.

**2. `run_worker(client, contract_id, text, budget=WORKER_BUDGET)`** returns `{"contract_id", "status", "report", "error", "usage": {"input_tokens", "output_tokens"}}` and never raises:

| What happened | `status` | `error` |
|---|---|---|
| Counted input tokens over `budget` (no model call made) | `skipped` | `over_budget` |
| The SDK raised `anthropic.APIError` after its retries | `failed` | the class name, e.g. `OverloadedError` |
| `stop_reason` is `refusal` or `max_tokens` | `failed` | `refused` or `max_tokens` |
| Text isn't JSON, or `contract_id` doesn't match | `failed` | `bad_report` |
| Otherwise | `ok` | `None` |

**3. `assess(report)`** returns the flags, in this order: `low_liability_cap` (cap under 50,000), `long_notice` (over 90 days), `auto_renew_trap` (auto-renew and notice over 60 days), `high_fuel_cap` (over 15%). A `None` term never triggers a flag.

**4. `merge(results)`** returns `{"flagged": {id: flags}, "clean": [...], "failed": [...], "skipped": [...], "coverage": reviewed / total}` (coverage rounded to 3 decimals).

**5. `lead_request(merged)`** returns parameters for one Opus 5.5 call: `LEAD_MODEL`, `LEAD_SYSTEM`, an explicit `effort`, and the merged findings as JSON. No contract text.

**6. `cost_usd(model, usage)`** prices usage with `PRICES` (per million tokens).

**7. `run_review(client, contracts)`** runs one worker per contract in order, merges, makes the lead call, and returns `{"merged", "summary", "usage": {"workers", "lead"}, "cost_usd"}`.

**8. `compare(review, baseline, truth_risky)`** returns, for `"fanout"` and `"baseline"`: `cost_usd`, `recall` (risky contracts flagged divided by all risky contracts), and `unreviewed_reported` (the fan-out's failed plus skipped IDs, sorted; empty for the baseline). The baseline entry also gets `silently_missing`: the contract IDs it never reported on, sorted.

## Example

```text
Flagged: {'CC-102': ['low_liability_cap', 'long_notice'], 'CC-103': ['high_fuel_cap'], ...}
Failed: ['CC-117'] Skipped: ['CC-113'] Coverage: 0.9
fanout:   cost ~$0.003, recall 0.91, unreviewed_reported ['CC-113', 'CC-117']
baseline: cost ~$0.11,  recall 0.82, silently_missing ['CC-109', 'CC-110', 'CC-111']
```

## Why it's built this way

- **The real win is visible gaps.** Both runs miss risky contracts. The fan-out names what it didn't review and why, so a person checks two contracts. The baseline's misses look like a finished job.
- **Budgets are checked before spending.** `count_tokens` is cheap. A per-worker cap stops one oversized document (CC-113) from blowing the run's budget, and routes it to a different path (chunking, or a person).
- **Read the cost numbers honestly.** These simulated usage figures leave out thinking tokens. On the real API, thinking is billed as output, which is why every request sets `effort` explicitly. The simulator's prices match the list prices for Haiku 5.5 (prompts up to 100K tokens) and Opus 5.5.
- **A fair baseline is part of the eval.** Before claiming sub-agents win, also try the single big call on a cheaper model or at lower effort, and check the result against the same answer key. The cheapest correct design wins, whatever its shape.
- **Run workers concurrently in production** (a thread pool or `asyncio` with a semaphore sized to your rate limit). The browser runtime here runs them in sequence.

In a debrief, expect: "Your fan-out was cheaper. Was it more accurate, and how do you know?" Answer with the recall figures and the unreviewed list, not with the architecture.
