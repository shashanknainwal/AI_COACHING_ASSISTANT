import asyncio
import anthropic

RETRYABLE = (anthropic.RateLimitError, anthropic.OverloadedError,
             anthropic.InternalServerError, anthropic.APIConnectionError)


def make_client():
    # This code owns retries, so turn the SDK's own retries off.
    return anthropic.AsyncAnthropic(max_retries=0)


def build_params(ticket):
    return {
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "output_config": {"effort": "low"},
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": ticket["text"]}],
    }


async def classify(client, sem, ticket, max_attempts=4):
    error = None
    for attempt in range(1, max_attempts + 1):
        try:
            async with sem:
                resp = await client.messages.create(**build_params(ticket))
            label = next(b.text for b in resp.content if b.type == "text").strip()
            return {"id": ticket["id"], "label": label, "attempts": attempt, "error": None}
        except RETRYABLE as exc:
            error = type(exc).__name__
            if attempt == max_attempts:
                break
            retry_after = getattr(getattr(exc, "response", None), "headers", {}).get("retry-after")
            wait = float(retry_after) if retry_after else BACKOFF_BASE * 2 ** (attempt - 1)
            await asyncio.sleep(wait)          # outside the semaphore: the slot is free while we wait
        except anthropic.APIStatusError as exc:
            return {"id": ticket["id"], "label": None, "attempts": attempt, "error": type(exc).__name__}
    return {"id": ticket["id"], "label": None, "attempts": max_attempts, "error": error}


async def backfill(client, tickets, max_concurrency=8, max_attempts=4):
    sem = asyncio.Semaphore(max_concurrency)
    results = await asyncio.gather(*(classify(client, sem, t, max_attempts) for t in tickets))
    ok = sum(1 for r in results if r["error"] is None)
    return {"results": list(results), "succeeded": ok, "failed": len(results) - ok,
            "retries": sum(r["attempts"] - 1 for r in results)}


# --- Try it out (not graded) ---
if __name__ == "__main__":
    async def main():
        loop = asyncio.get_running_loop()
        start = loop.time()
        report = await backfill(make_client(), TICKETS, max_concurrency=8)
        return report, loop.time() - start

    report, elapsed = run_async(main())
    print(f"{report['succeeded']} ok, {report['failed']} failed, {report['retries']} retries, "
          f"{elapsed:.1f} s of virtual time, server saw at most {SERVER.max_inflight} in flight")
    for r in report["results"][:6]:
        print(r)
    print([r for r in report["results"] if r["error"]])
