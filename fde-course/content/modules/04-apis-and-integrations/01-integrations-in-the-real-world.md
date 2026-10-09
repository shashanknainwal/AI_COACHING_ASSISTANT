---
title: "Integrations in the Real World: REST, Auth, and Sessions"
type: reading
minutes: 7
---

> **By the end of this lesson you will be able to:**
> - Know the five things to find first in an unfamiliar API's docs
> - Make authenticated requests with `requests` and a `Session`
> - Decide what your code does with each status code

Leah Park, Head of Integrations at Northwind Freight, needs shipment status from Northwind's REST API to flow into a retail client's ERP so agents stop copying tracking numbers by hand. You're connecting them, and her on-call engineer gets paged if your job breaks.

## Methods and retry safety

`GET` (read), `PUT` (replace) and `DELETE` are safe to retry; `PATCH` usually is. `POST` (create) is **not**, unless the API supports idempotency keys.

## Status codes: what your code does

| Code | Meaning | What your code does |
|---|---|---|
| **200/201/204** | Success | Continue |
| **400** | Malformed request | Fix your code; don't retry |
| **401** | Missing or invalid credentials | Stop; check or refresh the token |
| **403** | Valid credentials, no permission | Stop; ask the customer for access |
| **404** | Not found | Handle it (may be expected) |
| **409** | Conflict, often a duplicate | Treat as "already done" or investigate |
| **422** | Valid JSON, invalid data | Log the record, skip, report |
| **429** | Rate limited | Wait (respect `Retry-After`), then retry |
| **5xx** | Server or gateway problem | Retry with backoff, a limited number of times |

**4xx means you did something wrong** (don't retry, except 429); **5xx means they did** (usually retry).

## Authentication

| Pattern | How it's sent | Notes |
|---|---|---|
| API key | Header like `X-API-Key: abc123` | Never in URLs that get logged |
| Bearer token | `Authorization: Bearer <token>` | The most common |
| Basic auth | `Authorization: Basic base64(user:password)` | Older systems; HTTPS only |
| OAuth 2.0 client credentials | Exchange client ID and secret for a short-lived token | Tokens expire; refresh them |

Secrets never go in code or Git: read them from `os.environ["NORTHWIND_TOKEN"]` or a secrets manager. Ask for least privilege; security teams approve narrow, read-only scopes faster.

## The `requests` library

```python
import requests

response = requests.get(
    "https://api.northwind.example/v1/shipments",
    params={"status": "in_transit", "limit": 50},   # becomes ?status=in_transit&limit=50
    headers={"Authorization": "Bearer abc123"},
    timeout=10,                                     # seconds; always set one
)
response.raise_for_status()      # raises requests.HTTPError for 4xx/5xx
data = response.json()
```

- **Always pass `timeout`.** Without it, a hung server blocks your job forever.
- **Check the status before using the body.** A 500 error page parsed as JSON fails far from the real cause.
- **Use `params=`**; it handles escaping.

For many calls, a `Session` reuses connections and sets shared headers once:

```python
session = requests.Session()
session.headers.update({"Authorization": f"Bearer {token}", "Accept": "application/json"})
r = session.get(f"{BASE}/v1/shipments/SHP-1001", timeout=10)
```

> **About the course simulator:** here `import requests` loads a simulated library with the same API, against a fake server with pagination, rate limits and failures. Your code runs unchanged against real APIs. `time.sleep` is simulated too.

## Read the docs for five things

1. **Authentication:** method, scopes, token expiry.
2. **Rate limits:** the limit, and what happens when exceeded (429? `Retry-After`?).
3. **Pagination:** cursor, page number or offset; maximum page size.
4. **Time filtering:** an `updated_since` parameter (essential for incremental sync).
5. **Error format**, so you can log it usefully.

Then **make one request by hand** before writing code. Docs are often slightly wrong.

## Mistakes that page you at 2 a.m.

| Mistake | Symptom | Prevention |
|---|---|---|
| No timeout | Job hangs forever | `timeout=` on every call |
| Only the first page | Most data missing, silently | Follow pagination |
| Retrying POSTs blindly | Duplicate orders | Idempotency keys |
| Ignoring 429 | Your key gets blocked | Respect `Retry-After` |
| No error body in logs | Impossible to debug | Log status, URL (no secrets), body |

**Try it:** the scratchpad on the right calls the simulated Northwind API. Run it, then fetch a single shipment by ID.

> **Key takeaways**
> - 4xx: fix your request (except 429). 5xx: retry with backoff.
> - Secrets in environment variables; least-privilege access.
> - Always `timeout`, check status, use `params=` and a `Session`.
> - Find auth, rate limits, pagination, time filters and error format, then make one request by hand.
