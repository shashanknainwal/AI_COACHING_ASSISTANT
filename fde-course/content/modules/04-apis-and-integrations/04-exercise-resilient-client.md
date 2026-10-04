---
title: "Exercise: Build a Resilient API Client"
type: exercise
minutes: 30
hints:
  - "`backoff_delay`: `return min(cap, base * 2 ** (attempt - 1))`."
  - "`retry_after_seconds`: read `response.headers.get(\"Retry-After\")`. If it's None, return None. Otherwise try `float(value)` and return None on `ValueError` (it might be an HTTP date)."
  - "Loop with `for attempt in range(1, max_attempts + 1):` so attempt numbers start at 1, matching `backoff_delay`."
  - "Wrap only the `session.get(...)` call in `try/except (requests.Timeout, requests.ConnectionError)`. On the last attempt, re-raise with a bare `raise`."
  - "For retryable statuses on the last attempt, call `response.raise_for_status()` so the caller gets an `HTTPError`."
  - "Use `time.sleep(delay)` for waiting. In the course it's instant and recorded, so the tests can check your exact delays."
---

Northwind's tracking API is busy on Monday mornings: you'll see 503s, occasional timeouts, and 429s with a `Retry-After` header. The ERP sync can't fall over every time that happens. Build a GET helper that retries what's worth retrying, waits the right amount of time, and gives up cleanly.

## Your task

**1. `backoff_delay(attempt, base=1.0, cap=30.0)`** returns `base × 2^(attempt − 1)`, capped at `cap`. Attempts start at 1: delays are 1, 2, 4, 8, 16, 30, 30…

**2. `retry_after_seconds(response)`** returns the `Retry-After` header as a float if it's a number of seconds, otherwise `None` (header missing, or in HTTP-date format).

**3. `get_with_retries(session, url, params=None, max_attempts=5, base=1.0, cap=30.0)`** returns the parsed JSON of a successful response:

| What happens on attempt *n* | Not the last attempt | Last attempt |
|---|---|---|
| `requests.Timeout` or `requests.ConnectionError` | `time.sleep(backoff_delay(n, base, cap))`, retry | re-raise the exception |
| Status in `RETRYABLE_STATUS` (429, 500, 502, 503, 504) | sleep `retry_after_seconds(response)` if present, else `backoff_delay(n, base, cap)`, then retry | `response.raise_for_status()` |
| Any other 4xx/5xx | `raise_for_status()` immediately (no retry) | same |
| Success | return `response.json()` | same |

Every request must pass `timeout=TIMEOUT`. Never sleep after the final attempt.

Press **Run** to fetch a shipment from Northwind's flaky endpoint, then **Submit**. The tests check your results, every request, and every delay you slept.

> **In production** you'd also add jitter (`random.uniform(0, delay)`), log every retry, and stop retrying if the total time spent passes a budget. The tests here use exact delays so you can see the pattern clearly.
