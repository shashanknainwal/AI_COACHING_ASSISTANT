import asyncio
import anthropic

RETRYABLE = (anthropic.RateLimitError, anthropic.OverloadedError,
             anthropic.InternalServerError, anthropic.APIConnectionError)


def make_client():
    """An AsyncAnthropic client for a pool that does its own retries."""
    # TODO
    return None


def build_params(ticket):
    """Keyword arguments for messages.create."""
    # TODO
    return {}


async def classify(client, sem, ticket, max_attempts=4):
    """Classify one ticket under the semaphore, retrying what can be retried."""
    # TODO
    return {"id": ticket["id"], "label": None, "attempts": 0, "error": None}


async def backfill(client, tickets, max_concurrency=8, max_attempts=4):
    """Classify every ticket with at most max_concurrency requests in flight."""
    # TODO
    return {"results": [], "succeeded": 0, "failed": 0, "retries": 0}


# --- Try it out (not graded) ---
if __name__ == "__main__":
    async def main():
        loop = asyncio.get_running_loop()
        start = loop.time()
        report = await backfill(make_client(), TICKETS, max_concurrency=8)
        return report, loop.time() - start

    report, elapsed = run_async(main())
    print(report, f"{elapsed:.1f} s virtual")
