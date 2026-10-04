---
title: "Exercise: A Resilient, Cost-Aware Claude Client"
type: exercise
minutes: 35
hints:
  - "`make_client`: `anthropic.Anthropic(max_retries=3, timeout=60.0)`."
  - "`cached_system`: a list with one dict: `{\"type\": \"text\", \"text\": text, \"cache_control\": {\"type\": \"ephemeral\"}}`."
  - "Order the `except` clauses: `RateLimitError`, `BadRequestError`, `AuthenticationError`, then `APIStatusError` (check `e.status_code >= 500`), then `APIConnectionError`."
  - "For errors, the request ID is `getattr(e, \"request_id\", None)`; for responses it's `response._request_id`."
  - "`cost`: look up `PRICES[model]`, then add the four products and divide by 1,000,000. `round(..., 6)`."
  - "Every result dict has the same keys: status, text, request_id, usage. Use None where a value doesn't apply."
---

Harbor Bank's assistant will run all day for hundreds of agents. Before launch, the platform team wants one well-behaved wrapper that every feature uses: it retries what the SDK should retry, turns every failure into a clear status instead of an exception, caches the long system prompt, and prices every call accurately.

## Your task

**1. `make_client()`** returns an `anthropic.Anthropic` client with `max_retries=3` and `timeout=60.0`.

**2. `cached_system(text)`** returns the system prompt as a list with one text block marked for caching: `[{"type": "text", "text": ..., "cache_control": {"type": "ephemeral"}}]`.

**3. `call_claude(client, system, user_text, model=MODEL, max_tokens=4096)`** calls `messages.create` with `system=cached_system(system)` and one user message, and **never raises**. It returns:

```python
{"status": "ok", "text": "...", "request_id": "req_...", "usage": <Usage>}
```

| Outcome | status | text | usage |
|---|---|---|---|
| Normal answer | `"ok"` | joined text blocks | `response.usage` |
| `stop_reason == "max_tokens"` | `"truncated"` | the partial text | `response.usage` |
| `stop_reason == "refusal"` | `"refused"` | `None` | `response.usage` |
| `RateLimitError` | `"rate_limited"` | `None` | `None` |
| `BadRequestError` | `"bad_request"` | `None` | `None` |
| `AuthenticationError` | `"auth_error"` | `None` | `None` |
| other `APIStatusError` with status ≥ 500 | `"server_error"` | `None` | `None` |
| other `APIStatusError` | `"api_error"` | `None` | `None` |
| `APIConnectionError` | `"connection_error"` | `None` | `None` |

`request_id` is `response._request_id` for responses and `e.request_id` (if present) for errors.

**4. `cost(usage, model=MODEL)`** returns the call's cost in dollars, rounded to 6 decimals, using the `PRICES` table and all four token types (`input_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, `output_tokens`).

Press **Run** to send two requests with the same long system prompt (watch the second one hit the cache), then **Submit**. The tests also simulate outages, rate limits, and bad requests.
