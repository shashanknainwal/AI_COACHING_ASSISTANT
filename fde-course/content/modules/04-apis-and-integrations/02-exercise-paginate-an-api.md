---
title: "Exercise: Pull Every Record from a Paginated API"
type: exercise
minutes: 25
hints:
  - "`make_session`: create `requests.Session()` and `session.headers.update({\"Authorization\": f\"Bearer {token}\", \"Accept\": \"application/json\"})`."
  - "`fetch_page`: build `params = {\"limit\": limit}`, add `cursor` and `status` only when they're not None, then `session.get(f\"{BASE}/v1/shipments\", params=params, timeout=TIMEOUT)`."
  - "Call `response.raise_for_status()` before `response.json()`. Return `(body[\"data\"], body[\"next_cursor\"])`."
  - "`fetch_all`: loop with `cursor = None`; after each page, extend your list; stop when `next_cursor` is None."
  - "Keep a `seen` set of cursors. If the API hands you a cursor you've already used, raise `RuntimeError(\"pagination loop\")` instead of looping forever."
  - "`count_by_status`: count with a dict or `Counter`, then return `dict(sorted(counts.items()))`."
---

The retailer's ERP needs every Northwind shipment. Northwind's API returns them **50 at a time at most**, using **cursor pagination**: each response includes a `next_cursor` you pass back to get the next page, until it's `null`.

```http
GET /v1/shipments?limit=50
Authorization: Bearer nw_test_token

{"data": [ ...50 shipments... ], "next_cursor": "c_50"}

GET /v1/shipments?limit=50&cursor=c_50
{"data": [ ...50 shipments... ], "next_cursor": "c_100"}

GET /v1/shipments?limit=50&cursor=c_100
{"data": [ ...27 shipments... ], "next_cursor": null}
```

The API also accepts an optional `status` filter, and returns **401** if the token is wrong.

## Your task

**1. `make_session(token)`** returns a `requests.Session` whose headers include `Authorization: Bearer <token>` and `Accept: application/json`.

**2. `fetch_page(session, cursor=None, status=None, limit=PAGE_SIZE)`** makes **one** request to `f"{BASE}/v1/shipments"`:
- Query parameters: `limit`, plus `cursor` and `status` only if they're not `None`.
- Always pass `timeout=TIMEOUT`.
- Call `raise_for_status()`, then return a tuple `(data, next_cursor)`.

**3. `fetch_all(session, status=None)`** returns a list of **all** shipments, following `next_cursor` until it's `None`. If the API ever returns a cursor you've already requested, raise `RuntimeError("pagination loop")`. (Buggy APIs do this, and an infinite loop against a customer's API is a very bad day.)

**4. `count_by_status(shipments)`** returns a dict of status → count, with keys in alphabetical order.

Press **Run** to pull all of Northwind's shipments, then **Submit**. The tests check your results and every request your code sent.

> **Why page size matters:** 127 shipments at 50 per page is 3 requests; at the API's default of 20 it would be 7. Against a rate-limited API with 2 million records, using the maximum page size is the difference between a 1-hour sync and a 3-hour one.
