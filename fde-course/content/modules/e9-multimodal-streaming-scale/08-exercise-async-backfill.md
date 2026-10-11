---
title: "Exercise: An Async Backfill That Respects Rate Limits"
type: exercise
minutes: 40
hints:
  - "`make_client` is one line: `anthropic.AsyncAnthropic(max_retries=0)`. Your loop retries, so the SDK mustn't retry underneath it."
  - "`classify`: a `for attempt in range(1, max_attempts + 1)` loop. Put only the API call inside `async with sem:`, so the `await asyncio.sleep(...)` between attempts happens with the slot released."
  - "Order the `except` clauses: the retryable tuple `RETRYABLE` first, then `anthropic.APIStatusError` for everything else (a 400 is an `APIStatusError` but not retryable). Use `type(exc).__name__` for the error string."
  - "The retry-after value is in `exc.response.headers.get(\"retry-after\")`, as a string of seconds. Without it, wait `BACKOFF_BASE * 2 ** (attempt - 1)`. Don't sleep after the last attempt."
  - "`backfill`: create one `asyncio.Semaphore(max_concurrency)`, then `await asyncio.gather(*(classify(...) for t in tickets))`. `gather` returns results in input order."
---

Leo again. Tallowmere wants three years of order-desk emails labelled by intent so they can tune their routing rules. Their platform team runs everything through their own AWS account, and their first plan was the Message Batches API. Then someone noticed their Claude access goes through Amazon Bedrock, where Batches isn't available. So it's a worker pool. Their first attempt used `asyncio.gather` over every email at once and got a wall of 429s, then retried them all on the same one-second timer.

You'll write the pool against a simulated server that allows **8** requests in flight and returns a 429 with `retry-after: 2` above that. One email (`T-0009`) is empty, one (`T-0017`) hits a transient 529 overload once, and one (`T-0031`) is rate-limited every time.

## Given

`TICKETS` (40 dicts with `id` and `text`), `MODEL` (Claude Haiku 5.5), `MAX_TOKENS`, `SYSTEM_PROMPT`, `BACKOFF_BASE = 0.5`, `RETRYABLE`, the simulated `anthropic.AsyncAnthropic`, and `run_async(coro)`.

**About `run_async`.** In production you'd write `asyncio.run(main())`. The browser already runs an event loop, so here `run_async(main())` runs your coroutine on a private loop with a **virtual clock**: `await asyncio.sleep(2)` returns at once but moves `loop.time()` forward 2 seconds. Your code uses ordinary `asyncio` and works unchanged outside the course.

## Your task

**1. `make_client()`** returns an `anthropic.AsyncAnthropic` with SDK retries turned off.

**2. `build_params(ticket)`** returns keyword arguments for `messages.create`: `model`, `max_tokens`, `output_config={"effort": "low"}`, `system=SYSTEM_PROMPT`, and one user message whose content is the ticket's text.

**3. `async classify(client, sem, ticket, max_attempts=4)`** returns `{"id", "label", "attempts", "error"}`:

- Make the call while holding `sem`. On success, `label` is the first text block's text stripped, and `error` is `None`.
- On an exception in `RETRYABLE`: if attempts remain, wait (`retry-after` seconds when the header is present, otherwise `BACKOFF_BASE * 2 ** (attempt - 1)`) **without holding the semaphore**, then try again. After the last attempt, give up with `error` set to the exception's class name.
- On any other `anthropic.APIStatusError` (such as a 400): give up at once with `error` set to its class name.
- `attempts` is the number of calls made for this ticket. `label` is `None` on failure.

**4. `async backfill(client, tickets, max_concurrency=8, max_attempts=4)`** classifies every ticket with at most `max_concurrency` in flight and returns `{"results", "succeeded", "failed", "retries"}`: results in input order, counts of successes and failures, and `retries` as the total number of extra attempts (attempts beyond the first, summed).

## Things to notice when you run it

- **The speed-up is real but bounded.** 40 calls of about a second each, 8 at a time, take about 10 virtual seconds instead of about 48. Go above the server's limit (the last test runs at 20) and you buy 429s, not speed.
- **Where you sleep matters.** A task that sleeps for 2 seconds while holding the semaphore keeps a healthy request from starting. Put only the call inside `async with sem:`.
- **One retry layer.** With the SDK's default `max_retries=2` underneath your loop of 4, one stubborn email could make 12 calls.
- **Report failures, don't hide them.** `T-0031` fails after its attempts and `T-0009` fails at once. Both come back with a reason, ready for a second pass or a person.

## Example

```python
>>> report = run_async(backfill(make_client(), TICKETS, max_concurrency=8))
>>> report["succeeded"], report["failed"], report["retries"]
(38, 2, 4)
>>> [r for r in report["results"] if r["error"]]
[{'id': 'T-0009', 'label': None, 'attempts': 1, 'error': 'BadRequestError'}, {'id': 'T-0031', 'label': None, 'attempts': 4, 'error': 'RateLimitError'}]
```

Press **Run** to see the virtual time and the peak in-flight count, then **Submit**.
