---
title: "Errors, Retries, Backoff, and Rate Limits"
type: reading
minutes: 3
---

> **By the end of this lesson you will be able to:**
> - Retry only transient failures, with capped exponential backoff and `Retry-After`
> - Explain why retrying a POST creates duplicates, and how idempotency keys prevent it
> - Stay inside a customer's rate limits instead of getting your key blocked

Last night Northwind's API restarted twice and returned a burst of 503s and 429s. Leah's question this morning: did your sync recover by itself, or did it miss shipments? The goal is to recover automatically from temporary failures and fail loudly on permanent ones.

## Transient vs. permanent

| Failure | Retry? |
|---|---|
| Timeout, connection reset | Yes |
| 429 Too Many Requests | Yes, after the indicated wait |
| 500 / 502 / 503 / 504 | Yes, a few times |
| 400, 422 | No: fix the code or data |
| 401 | Refresh the token once, or stop |
| 403, 404 | No |

Retrying a 400 a hundred times sends the same broken request a hundred times.

## Exponential backoff

If every client retries immediately, the retries make a struggling server worse (a "retry storm"). Wait 1s, 2s, 4s, 8s, then give up:

```python
def backoff_delay(attempt, base=1.0, cap=30.0):
    return min(cap, base * 2 ** (attempt - 1))
```

Add a **cap** and a **maximum number of attempts**. In production add **jitter**, `random.uniform(0, delay)`, so clients that failed together don't retry together. (The exercise skips jitter so tests can check exact delays.)

## Respect `Retry-After`

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 7
```

**If `Retry-After` is present, use it instead of your backoff.** The server knows its limits. It can be seconds or an HTTP date; handle seconds and fall back to backoff otherwise.

## Stay under the rate limit

Retrying on 429 is the safety net, not the strategy, and the customer's API owners can see your traffic. Know the limit (docs, or headers like `X-RateLimit-Remaining`), pace requests (10 per second means 0.1s apart, or a token bucket), use the largest page size, and schedule big backfills off-hours after telling the customer.

## The dangerous retry: POST

```
POST /v1/orders  {"sku": "VALVE-2", "qty": 40}
   → server creates the order... then the response times out
POST /v1/orders  {"sku": "VALVE-2", "qty": 40}     ← your retry
   → server creates a SECOND order
```

A timeout doesn't tell you whether the server processed the request. Send an **idempotency key**, generated once per logical operation and reused on every retry:

```python
import uuid
key = str(uuid.uuid4())   # once per order, reused for every retry of it
session.post(url, json=order, headers={"Idempotency-Key": key}, timeout=10)
```

APIs that support it return the original result instead of a duplicate. **If the API doesn't, don't auto-retry POSTs**: log it and check whether the record exists first.

Timeouts of 10–30 seconds are typical. Too short fails requests that would have succeeded (and with POST you won't know); too long stalls the job.

## A resilient GET

```
for attempt in 1..max_attempts:
    try:
        response = session.get(url, timeout=TIMEOUT)
    except Timeout or ConnectionError:
        if last attempt: raise
        sleep(backoff(attempt)); continue
    if status is 429 or 5xx:
        if last attempt: raise_for_status()
        sleep(Retry-After if present else backoff(attempt)); continue
    raise_for_status()          # 4xx: raise immediately, no retry
    return response.json()
```

You'll build this next. In real code, `tenacity` or `urllib3`'s `Retry` do the same; knowing the mechanics lets you configure them.

Log every retry (URL without secrets, attempt, status, delay) and the body of every final failure. That's how you answer Leah in five minutes instead of five hours.

> **Key takeaways**
> - Retry timeouts, connection errors, 429 and 5xx; fail fast on other 4xx.
> - Capped exponential backoff, a max attempt count, jitter in production.
> - Honor `Retry-After` and pace requests under the limit.
> - Never blindly retry POSTs; use idempotency keys.
