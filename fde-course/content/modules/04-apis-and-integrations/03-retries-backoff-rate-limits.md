---
title: "Errors, Retries, Backoff, and Rate Limits"
type: reading
minutes: 17
---

> **By the end of this lesson you will be able to:**
> - Classify failures as transient or permanent, and retry only the transient ones
> - Implement exponential backoff with a cap, and respect `Retry-After`
> - Explain why retrying a POST can create duplicate orders, and how idempotency keys prevent it
> - Stay inside a customer's rate limits instead of getting your API key blocked

## Failure is normal

Run an integration long enough and every failure mode will happen: servers restart, load balancers time out, networks drop packets, and rate limiters push back. An integration that works only when everything goes right will fail in its first week.

The goal isn't to never fail; it's to **recover automatically from the failures that are temporary, and fail loudly and clearly on the ones that aren't**.

## Transient vs. permanent

| Failure | Transient? | Retry? |
|---|---|---|
| Timeout, connection reset | Usually | Yes |
| 429 Too Many Requests | Yes, by definition | Yes, after the indicated wait |
| 500 / 502 / 503 / 504 | Usually | Yes, a few times |
| 400 Bad Request, 422 | No: your request is wrong | No: fix the code or the data |
| 401 Unauthorized | No (unless your token expired and you can refresh it) | No: refresh once, or stop |
| 403 Forbidden, 404 Not Found | No | No |

Retrying a 400 a hundred times just sends the same broken request a hundred times. Retrying a 503 a few times usually gets through.

## Exponential backoff

If a server is struggling and every client retries immediately, the retries make it worse (a "retry storm"). Instead, wait longer after each failure:

```
attempt 1 fails → wait 1s
attempt 2 fails → wait 2s
attempt 3 fails → wait 4s
attempt 4 fails → wait 8s
attempt 5 fails → give up and raise
```

The formula is `delay = base × 2^(attempt − 1)`, with a **cap** so you never wait absurdly long (for example, 30 seconds), and a **maximum number of attempts** so a dead server doesn't block your job forever.

```python
def backoff_delay(attempt, base=1.0, cap=30.0):
    return min(cap, base * 2 ** (attempt - 1))
```

**Jitter.** In production, add randomness: `random.uniform(0, delay)` ("full jitter"). If a thousand clients all failed at the same moment, jitter spreads their retries out instead of having them all hit the server again at exactly 1s, 2s, 4s. (The exercise uses no jitter so the tests can check exact delays; add it in your real code.)

## Respect `Retry-After`

When an API rate-limits you (429) or is temporarily unavailable (503), it often tells you exactly how long to wait:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 7
```

**If `Retry-After` is present, use it instead of your own backoff.** The server knows its own limits better than your formula does. `Retry-After` can be a number of seconds or an HTTP date; handle the number, and fall back to backoff otherwise.

## Rate limits: stay under, don't bounce off

Retrying on 429 is the safety net, not the strategy. If you hit the rate limit constantly, you're wasting requests and annoying the customer's API owners (who can see your traffic). Better:

- **Know the limit** (from the docs or response headers like `X-RateLimit-Remaining`).
- **Pace yourself:** if the limit is 10 requests per second, sleep 0.1s between requests, or use a token-bucket limiter.
- **Use the largest page size** and bulk endpoints to need fewer requests.
- **Schedule big backfills** off-hours, after telling the customer.

## The dangerous retry: POST

Retrying a `GET` is harmless: reading twice changes nothing. Retrying a `POST` can be a disaster:

```
POST /v1/orders  {"sku": "VALVE-2", "qty": 40}
   → server creates the order... then the response times out on the way back
POST /v1/orders  {"sku": "VALVE-2", "qty": 40}     ← your retry
   → server creates a SECOND order
```

From your side, a timeout doesn't tell you whether the server processed the request. The fix is an **idempotency key**: a unique ID you generate per logical operation and send with every attempt.

```python
import uuid
key = str(uuid.uuid4())   # generated once per order, reused for every retry of it
session.post(url, json=order, headers={"Idempotency-Key": key}, timeout=10)
```

APIs that support this (Stripe and many payment, logistics, and ERP APIs do) remember the key and return the original result instead of creating a duplicate. **If the API doesn't support idempotency keys, don't automatically retry POSTs.** Log the failure, and check whether the record was created before trying again.

## Timeouts deserve their own rule

Always set a timeout, and set it thoughtfully:

- Too short and you'll fail requests that would have succeeded (and with POST, you won't know whether they did).
- Too long and a hung server stalls your whole job.
- 10-30 seconds is typical for normal API calls; bulk exports may need more.

## Putting it together

A resilient GET looks like this:

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

You'll implement exactly this in the next exercise. On your own machine, libraries like `tenacity`, or `urllib3`'s `Retry` mounted on a `requests` adapter, provide the same behavior; knowing how it works lets you configure them correctly.

## Log like you'll need to debug it at 2 a.m.

For every retry, log the URL (minus secrets), the attempt number, the status or exception, and the delay. For every final failure, log the response body. When the customer says "the sync missed some shipments last night," these logs are how you answer in five minutes instead of five hours.

> **Key takeaways**
> - Retry transient failures (timeouts, connection errors, 429, 5xx); fail fast on other 4xx.
> - Use exponential backoff with a cap and a maximum number of attempts; add jitter in production.
> - Honor `Retry-After`, and pace requests to stay under rate limits.
> - Never blindly retry POSTs; use idempotency keys.
