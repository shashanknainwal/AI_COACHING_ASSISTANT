---
title: "Integrations in the Real World: REST, Auth, and Sessions"
type: reading
minutes: 16
---

> **By the end of this lesson you will be able to:**
> - Read an unfamiliar API's docs and know which five things to look for first
> - Make authenticated requests with the `requests` library, using a `Session`
> - Interpret status codes and decide what your code should do with each
> - Avoid the integration mistakes that cause 2 a.m. pages

## Why integrations are the FDE's daily bread

Almost every deployment connects your product to something the customer already has: an ERP, a CRM, a ticketing system, a data warehouse, a carrier's tracking API. These systems weren't designed with you in mind. They rate-limit, paginate, time out, change without notice, and document things optimistically.

A working integration is often the difference between a demo and a deployment. In this module you'll build the integration skills that make deployments survive contact with real systems.

## Meet Northwind Freight

**Northwind Freight** is a logistics company. Their client, a retailer, wants shipment status to flow automatically into its ERP so customer-service agents stop copying tracking numbers by hand. Northwind has a REST API; the ERP has another. You're the FDE connecting them. Every exercise in this module is a piece of that integration.

## REST in five minutes

Most modern APIs follow REST conventions: **resources** at URLs, manipulated with HTTP **methods**.

| Method | Meaning | Example | Safe to retry? |
|---|---|---|---|
| `GET` | Read | `GET /v1/shipments/SHP-1001` | Yes |
| `POST` | Create (or trigger an action) | `POST /v1/shipments` | **No**, unless the API supports idempotency keys |
| `PUT` | Replace | `PUT /v1/shipments/SHP-1001` | Yes |
| `PATCH` | Partial update | `PATCH /v1/shipments/SHP-1001` | Usually |
| `DELETE` | Remove | `DELETE /v1/shipments/SHP-1001` | Yes |

"Safe to retry" (idempotent) matters enormously, and you'll come back to it when you build retries.

## Status codes: what your code should do

| Code | Meaning | What your code does |
|---|---|---|
| **200/201/204** | Success | Continue |
| **400** Bad Request | Your request is malformed | Fix your code; don't retry |
| **401** Unauthorized | Missing or invalid credentials | Stop; check or refresh the token |
| **403** Forbidden | Valid credentials, no permission | Stop; ask the customer for access |
| **404** Not Found | Resource doesn't exist | Handle it (it might be expected) |
| **409** Conflict | State conflict, often a duplicate | Treat as "already done" or investigate |
| **422** Unprocessable | Valid JSON, invalid data | Log the record, skip, report |
| **429** Too Many Requests | Rate limited | Wait (respect `Retry-After`), then retry |
| **500/502/503/504** | Server or gateway problem | Retry with backoff, a limited number of times |

The big split: **4xx means you did something wrong** (usually don't retry, except 429), **5xx means they did** (usually retry).

## Authentication patterns

| Pattern | How it's sent | Notes |
|---|---|---|
| API key | Header like `X-API-Key: abc123` (sometimes a query parameter) | Simple; never put it in URLs that get logged |
| Bearer token | `Authorization: Bearer <token>` | The most common |
| Basic auth | `Authorization: Basic base64(user:password)` | Older systems; always over HTTPS |
| OAuth 2.0 client credentials | Exchange a client ID and secret for a short-lived bearer token | Common for enterprise APIs; tokens expire, so refresh them |

Two rules that prevent incidents:

1. **Secrets never go in code or Git.** Read them from environment variables or a secrets manager: `os.environ["NORTHWIND_TOKEN"]`.
2. **Ask for the least privilege you need.** Read-only scopes for a read-only integration. Security teams approve narrow requests much faster.

## The `requests` library

`requests` is the standard way to call HTTP APIs from Python:

```python
import requests

response = requests.get(
    "https://api.northwind.example/v1/shipments",
    params={"status": "in_transit", "limit": 50},   # becomes ?status=in_transit&limit=50
    headers={"Authorization": "Bearer abc123"},
    timeout=10,                                     # seconds; always set one
)
response.raise_for_status()      # raises requests.HTTPError for 4xx/5xx
data = response.json()           # parse the JSON body
```

Three habits to build now:

- **Always pass `timeout`.** Without it, a hung server can block your job forever. This is one of the most common production bugs in integrations.
- **Call `raise_for_status()`** (or check `response.status_code`) before using the body. A 500 error page parsed as JSON produces confusing errors far from the real cause.
- **Use `params=`** instead of building query strings by hand; it handles escaping.

### Sessions

When you make many requests to the same API, use a `Session`. It reuses connections (much faster) and lets you set shared headers once:

```python
session = requests.Session()
session.headers.update({"Authorization": f"Bearer {token}", "Accept": "application/json"})

r1 = session.get(f"{BASE}/v1/shipments", params={"limit": 50}, timeout=10)
r2 = session.get(f"{BASE}/v1/shipments/SHP-1001", timeout=10)
```

> **About the course simulator:** in this module, `import requests` loads a simulated version of the library with the same functions, `Response` objects, and exceptions. Each exercise sets up a realistic fake API (with pagination, rate limits, and failures). Your code runs unchanged against real APIs with `pip install requests`. `time.sleep` is also simulated, so retry code runs instantly.

## Reading API docs: the first five things

When you get access to a new API, find these before writing code:

1. **Authentication:** which method, which scopes, how tokens expire.
2. **Rate limits:** requests per second or minute; what happens when exceeded (429? `Retry-After`?).
3. **Pagination:** cursor, page number, or offset? Maximum page size?
4. **Filtering by time:** is there an `updated_since` parameter? (Essential for incremental sync, covered later.)
5. **Error format:** what an error body looks like, so you can log it usefully.

Then **make one request by hand** (in a scratchpad or with `curl`) before writing any integration code. Docs are often slightly wrong: field names differ, dates come back in another format, an "optional" parameter is required.

## The integration mistakes that page you at 2 a.m.

| Mistake | Symptom | Prevention |
|---|---|---|
| No timeout | Job hangs forever | `timeout=` on every call |
| Only fetching the first page | Missing 95% of the data, silently | Always handle pagination |
| Retrying POSTs blindly | Duplicate orders or charges | Idempotency keys, or don't retry |
| Ignoring 429 | Customer's API blocks your key | Respect `Retry-After`, back off |
| Token in code or logs | Security incident | Environment variables; redact logs |
| Not logging the response body on errors | Impossible to debug | Log status, URL (without secrets), and the error body |

**Try it:** the scratchpad on the right calls the simulated Northwind API. Run it, then try fetching a single shipment by ID.

> **Key takeaways**
> - 4xx usually means fix your request (except 429); 5xx usually means retry with backoff.
> - Keep secrets in environment variables and request least-privilege access.
> - Always set `timeout`, check the status, and use `params=`; use a `Session` for many calls.
> - Before coding against a new API, find auth, rate limits, pagination, time filters, and error format, then make one request by hand.
