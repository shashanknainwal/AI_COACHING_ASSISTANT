---
title: "Exercise: A Message Batches Job, End to End"
type: exercise
minutes: 40
hints:
  - "`build_requests`: don't derive the `custom_id` from the order id (`PO#4401/2` has `#` and `/`). Use the position, like `order-00000`, and keep a dict from custom_id back to order id."
  - "`run_batch`: create, then `while retrieve(batch.id).processing_status != \"ended\": time.sleep(poll_seconds)`. Only then iterate `results(batch.id)` and key each result by `custom_id`."
  - "`process`: keep a dict of pending requests keyed by custom_id. Each round, send only the pending ones, and build the next round's dict from the results you'll retry."
  - "For an errored result the error type is two levels down: `result.result.error.error.type`. `invalid_request_error` means fix the request, so it goes straight to `failed`. Everything else errored, plus `expired` and `canceled`, is retryable."
  - "When the rounds run out, whatever is still pending goes into `failed` with the reason from its last attempt. Count `rounds` as batches actually created, so a clean first round stops at 1."
---

Leo here. Tallowmere's analytics team has its own Claude API account, separate from the order desk's Bedrock setup, so they can use the Message Batches API for the archive: three years of order-desk emails to label, nobody waiting on any single answer, half the price. The job runs overnight. In the morning Imani wants one report: what got labelled, what failed and why. She doesn't want to hear "some requests errored, we're not sure which".

The simulated Batches API behaves like the real one. Processing takes 25 simulated minutes, `retrieve` reports `in_progress` until then, results come back **in a different order** from your requests, and asking for results early is an error. In the first round, one email is empty (an invalid request), two hit transient server errors, one expires, and one keeps failing every time.

## Given

`ORDERS` (24 dicts with `order_id` and `text`), `client` (with `client.messages.batches.create`, `.retrieve` and `.results`), `MODEL` (Claude Haiku 5.5), `MAX_TOKENS`, `SYSTEM_PROMPT` and `CUSTOM_ID_PATTERN`. `time.sleep` runs on a virtual clock here, so polling every 60 seconds costs no real time.

## Your task

**1. `build_requests(orders)`** returns `(requests, id_map)`. Each request is `{"custom_id": ..., "params": {...}}`:

- `custom_id`: unique and matching `^[a-zA-Z0-9_-]{1,64}$`. `id_map` maps it back to the `order_id`.
- `params`: `model`, `max_tokens`, `output_config={"effort": "low"}`, `system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral", "ttl": "1h"}}]`, and one user message with the order's text. No `stream`.

**2. `run_batch(client, requests, poll_seconds=60)`** creates a batch, polls `retrieve` with `time.sleep(poll_seconds)` between polls until `processing_status == "ended"`, then reads `results` and returns `(batch_id, {custom_id: result})`.

**3. `process(client, orders, max_rounds=3, poll_seconds=60)`** returns `{"labels", "failed", "rounds", "batch_ids"}`:

- Round 1 sends every request. Each later round sends only the requests that failed in a retryable way, for at most `max_rounds` rounds, and stops early when nothing is left.
- `succeeded`: `labels[order_id]` is the first text block of `result.message`, stripped.
- `errored` with `result.error.error.type == "invalid_request_error"`: `failed[order_id] = "invalid_request_error"`. Don't resend it.
- Other `errored` results (the reason is the error type), `expired` and `canceled` (the reason is the result type) are retried.
- After the last round, every request still pending goes into `failed` with its last reason.
- `rounds` is the number of batches created, and `batch_ids` lists them in order.

## Why each rule exists

- **custom_id, not order id.** Results don't come back in order, so the `custom_id` is your only join key, and the API only accepts letters, digits, `-` and `_`. A mapping table also keeps business identifiers out of a field you may log.
- **Fix versus retry.** Errored, canceled and expired requests aren't billed, so retrying them costs nothing extra. Resending an invalid request just fails again. Params are validated asynchronously, which is why the empty email only shows up when the batch ends: test one request with the normal Messages API before you submit 100,000.
- **Same cached system block everywhere.** Cache hits inside a batch are best-effort, and batches can run longer than 5 minutes, so the docs suggest identical `cache_control` blocks and the 1-hour TTL.
- **Polling, not a tight loop.** Most batches finish within an hour and the limit is 24 hours. Poll every minute or so.
- **Platform.** This only works because the analytics team is on the Claude API. On Bedrock, Vertex or Foundry there is no Batches API; you'd use last exercise's async pool and pay standard prices.

## Example

```python
>>> report = process(client, ORDERS)
>>> report["rounds"], len(report["labels"])
(3, 22)
>>> report["failed"]
{'PO#4415/1': 'invalid_request_error', 'PO#4419/2': 'api_error'}
```

Press **Run** to see the batch sizes shrink round by round (24, then 4, then 2), then **Submit**.
