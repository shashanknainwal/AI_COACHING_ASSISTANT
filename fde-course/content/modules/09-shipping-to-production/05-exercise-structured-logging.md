---
title: "Exercise: Structured Logs for Every Claude Call"
type: exercise
minutes: 30
hints:
  - "`redact`: apply `EMAIL`, then `CARD`, then `PHONE` with `pattern.sub(\"[email]\", text)` and so on. Cards go before phones, because a phone pattern could match part of a card number."
  - "`log`: start with `{\"ts\": round(self.clock(), 3), \"level\": ..., \"service\": ..., \"event\": ...}`, add each field (redacting strings), then `json.dumps(record, sort_keys=True)`."
  - "`logged_create`: read `start = clock()` before the call and `clock()` again right after; `latency_ms = round((end - start) * 1000)`."
  - "Wrap the call in `try/except anthropic.APIError as e`, log the error event, then use a bare `raise` to re-raise it."
  - "Level is `\"warning\"` when `response.stop_reason in (\"max_tokens\", \"refusal\")`, otherwise `\"info\"`. Use `call_cost(response.model, response.usage)`."
---

At 2 a.m. something goes wrong with Brightway's assistant. The on-call engineer has only the logs. Plain-text lines like `called claude ok` won't help them; **structured** JSON logs with request IDs, tokens, latency and cost will. They also must not leak customers' personal data into a log system dozens of people can read.

`PRICES`, `call_cost(model, usage)` and the redaction patterns `EMAIL`, `CARD`, `PHONE` are given.

## Your task

**1. `redact(text)`** replaces emails with `[email]`, card numbers with `[card]` and phone numbers with `[phone]`, in that order.

**2. `JsonLogger.log(level, event, **fields)`** builds one record:

```json
{"ts": 1700000000.123, "level": "info", "service": "triage", "event": "ticket_received", "request_id": "r1", ...}
```

- `ts` is `self.clock()` rounded to 3 decimals; `service` comes from the constructor.
- Every **string** field is passed through `redact`. Other values are kept as they are.
- Serialize with `json.dumps(record, sort_keys=True)`, append the line to `self.lines`, and return it.

**3. `logged_create(client, logger, request_id, clock=time.monotonic, **params)`** calls `client.messages.create(**params)` and logs exactly one event:

- **Success:** event `llm_call` with `request_id`, `model`, `stop_reason`, `input_tokens`, `output_tokens`, `cache_read_tokens`, `cache_write_tokens`, `latency_ms` (an integer: measure with `clock()` before and after) and `cost_usd`. The level is `"warning"` if `stop_reason` is `max_tokens` or `refusal`, otherwise `"info"`. Return the response.
- **`anthropic.APIError`:** event `llm_error`, level `"error"`, with `request_id`, `model` (from params), `error_type` (the exception class name) and `latency_ms`. Then **re-raise** the error.
- **Never** log the prompt or the response text.

Press **Run** to see redacted, structured log lines, then **Submit**.
