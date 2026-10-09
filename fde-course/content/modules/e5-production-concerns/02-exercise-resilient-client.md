---
title: "Exercise: A Retry Policy You Can Defend"
type: exercise
minutes: 40
hints:
  - "`is_retryable`: check `isinstance(exc, anthropic.APIConnectionError)` first (timeouts are a subclass of it). For `anthropic.APIStatusError`, return `exc.status_code in RETRYABLE_STATUS or exc.status_code >= 500`. Anything else is `False`."
  - "`retry_after_seconds`: `getattr(exc, \"response\", None)`, then its `headers.get(\"retry-after\")`. Wrap `float(value)` in `try/except (TypeError, ValueError)` and return `None` for negatives."
  - "`backoff_delay`: `if retry_after is not None: return float(retry_after)`. Otherwise `return rand() * min(cap, base * 2 ** attempt)`. Test `is not None`, because a retry-after of 0 is a real value."
  - "`call_with_retries`: record `start = time.monotonic()`. Each attempt uses `timeout = min(attempt_timeout_s, deadline_s - (time.monotonic() - start))` and calls `client.with_options(max_retries=0, timeout=timeout).messages.create(**params)`."
  - "On `except anthropic.APIError as exc`: append the log entry with `wait: None`; re-raise with a bare `raise` if the error isn't retryable, if this was the last attempt, or if `time.monotonic() - start + delay >= deadline_s`. Otherwise set the entry's `wait` to the delay and `time.sleep(delay)`."
---

Leo Martins here. One of our customers, Ledgerline (fictional), runs accounts-payable automation: Claude reads vendor invoices and pulls out the fields their ledger needs. On the last two days of every month their traffic jumps, and so do their errors. Their current code wraps every call in `for i in range(10): try ... except Exception: time.sleep(1)`. It retries bad requests that can never succeed, it hammers the API at a fixed one-second rhythm during an overload, and when something fails they can't tell support which request it was.

You're replacing that loop with a retry policy you could defend line by line in a design review, or in an interview deep dive. Tests use a fake clock, so `time.sleep` is instant and the checks can assert the exact waits.

## Your task

**1. `is_retryable(exc)`** returns `True` for errors a retry might fix:

| Retry | Don't retry |
|---|---|
| `APIConnectionError` and its subclass `APITimeoutError` | 400 bad request, 401, 403, 404, 413 |
| Status 408, 409, 429 (`RETRYABLE_STATUS`) | Any exception that isn't an `anthropic` API error (your own bugs) |
| Any status of 500 or above, including 529 overloaded | |

**2. `retry_after_seconds(exc)`** returns the error's `retry-after` header as a float, or `None` if there's no response, no header, a value that isn't a number, or a negative number.

**3. `backoff_delay(attempt, retry_after=None, base=1.0, cap=20.0, rand=random.random)`**, where `attempt` is 0 for the first retry:

- If `retry_after` is not `None`, return it. The server knows when capacity frees up.
- Otherwise use **full jitter**: `rand() * min(cap, base * 2 ** attempt)`. With `rand()` always 1.0 that gives 1, 2, 4, 8, 16, 20, 20 seconds.

`rand` is a parameter so tests can make the jitter deterministic. Injecting randomness like this is a point worth making in an interview.

**4. `call_with_retries(client, params, *, max_attempts=4, deadline_s=60.0, attempt_timeout_s=30.0, rand=random.random, log=None)`**:

- Send each attempt with `client.with_options(max_retries=0, timeout=...).messages.create(**params)`. The SDK retries on its own by default (twice); turning that off stops two retry layers from multiplying into twelve attempts.
- Each attempt's timeout is `min(attempt_timeout_s, time left before the deadline)`. Measure time with `time.monotonic()`.
- Return the `Message` on success.
- On an `anthropic.APIError`: raise it at once if it isn't retryable or this was attempt number `max_attempts`. Otherwise compute the delay. If `elapsed + delay >= deadline_s`, raise now rather than sleep into a missed deadline. Else sleep and try again.
- Append one entry per attempt to `log` (if given):

```python
{"attempt": 1, "status": 529, "request_id": "req_...", "wait": 0.84}   # failed, then waited 0.84s
{"attempt": 2, "status": "timeout", "request_id": None, "wait": None}  # failed, gave up
{"attempt": 3, "status": 200, "request_id": "req_...", "wait": None}   # success
```

`status` is the HTTP status, `"timeout"` for `APITimeoutError`, `"connection"` for other connection errors, or 200 on success. `request_id` is `response._request_id` on success and `getattr(exc, "request_id", None)` on failure. `wait` is the delay you slept after this attempt, or `None` if you didn't sleep.

Press **Run** to replay a busy month-end minute: an overload, a rate limit with `retry-after: 3`, then an answer. Then **Submit**.

## Defend it

Be ready to answer these in a deep dive (original practice questions):

- "Why full jitter instead of plain exponential backoff?" Many clients that failed together retry together. Spreading their retries over the whole window breaks up the herd.
- "Why not retry a 400?" The same bytes give the same error. Retrying only adds load and latency.
- "Your service already has a 10-second budget. What does a 30-second `retry-after` mean for it?" It means fail fast and degrade (lesson 5), not sleep.
- "Where would you put this wrapper if three services call Claude?" In one shared client library or gateway, so the policy, the logging and the metrics are the same everywhere.
