import asyncio
from anthropic import _sim

BY_ID = {t["id"]: t for t in TICKETS}


def _fresh():
    _sim.calls.clear()
    SERVER.reset()


def _timed(coro):
    async def wrapper():
        loop = asyncio.get_running_loop()
        start = loop.time()
        out = await coro
        return out, loop.time() - start
    return run_async(wrapper())


def test_client_and_params():
    """make_client() turns off SDK retries and build_params() sets model, effort and system"""
    c = make_client()
    assert isinstance(c, anthropic.AsyncAnthropic), "use anthropic.AsyncAnthropic"
    assert c.max_retries == 0, "this pool owns retries; SDK retries underneath would multiply them"
    p = build_params(BY_ID["T-0001"])
    assert p.get("model") == MODEL and p.get("max_tokens") == MAX_TOKENS and p.get("system") == SYSTEM_PROMPT, p
    assert p.get("output_config") == {"effort": "low"}, "set effort explicitly (thinking counts toward max_tokens and cost)"
    assert p.get("messages") == [{"role": "user", "content": BY_ID["T-0001"]["text"]}], p.get("messages")


def test_classify_one():
    """classify() returns the label and attempt count for one ticket"""
    _fresh()
    r = run_async(classify(make_client(), asyncio.Semaphore(1), BY_ID["T-0002"]))
    assert r == {"id": "T-0002", "label": "returns", "attempts": 1, "error": None}, r


def test_classify_retries_overload():
    """classify() retries a 529 with backoff and succeeds"""
    _fresh()
    r = run_async(classify(make_client(), asyncio.Semaphore(1), BY_ID["T-0017"]))
    assert r["label"] == "returns" and r["attempts"] == 2 and r["error"] is None, r


def test_classify_does_not_retry_bad_request():
    """classify() gives up at once on a 400"""
    _fresh()
    r = run_async(classify(make_client(), asyncio.Semaphore(1), BY_ID["T-0009"]))
    assert r == {"id": "T-0009", "label": None, "attempts": 1, "error": "BadRequestError"}, r


def test_classify_honours_retry_after_and_caps_attempts():
    """classify() waits retry-after seconds between 429s and stops at max_attempts"""
    _fresh()
    r = run_async(classify(make_client(), asyncio.Semaphore(1), BY_ID["T-0031"], max_attempts=3))
    assert r == {"id": "T-0031", "label": None, "attempts": 3, "error": "RateLimitError"}, r
    log = SERVER.attempts[BY_ID["T-0031"]["text"]]
    gaps = [log[i + 1][0] - log[i][2] for i in range(len(log) - 1)]
    assert gaps and all(g >= RETRY_AFTER_SECONDS - 1e-9 for g in gaps), f"wait the retry-after value (2 s) before retrying: gaps {gaps}"


def test_backfill_runs_concurrently():
    """backfill() keeps input order, stays under the cap and finishes far faster than a loop"""
    _fresh()
    report, elapsed = _timed(backfill(make_client(), TICKETS, max_concurrency=8))
    ids = [r["id"] for r in report["results"]]
    assert ids == [t["id"] for t in TICKETS], "return results in input order"
    assert report["succeeded"] == 38 and report["failed"] == 2, f"succeeded {report['succeeded']}, failed {report['failed']}"
    assert report["retries"] == 4, f"retries counts extra attempts: expected 4, got {report['retries']}"
    assert SERVER.max_inflight <= 8, f"never more than max_concurrency in flight (saw {SERVER.max_inflight})"
    assert elapsed < 15, f"40 one-second calls 8 at a time should take well under 15 s of virtual time, took {elapsed:.1f}"


def test_backfill_cap_is_respected():
    """backfill() honours a small max_concurrency"""
    _fresh()
    report, elapsed = _timed(backfill(make_client(), TICKETS[:12], max_concurrency=3))
    assert SERVER.max_inflight <= 3, f"saw {SERVER.max_inflight} in flight with max_concurrency=3"
    assert elapsed >= 4, "12 calls, 3 at a time, can't finish in under 4 s: is the semaphore around the call?"


def test_backfill_recovers_from_overcommit():
    """backfill() still completes when concurrency exceeds the server limit"""
    _fresh()
    report, _ = _timed(backfill(make_client(), TICKETS, max_concurrency=20, max_attempts=6))
    assert SERVER.rate_limited > 5, "at 20 in flight the server returns 429s"
    bad = {r["id"] for r in report["results"] if r["error"]}
    assert bad == {"T-0009", "T-0031"}, f"every other ticket should succeed after honouring retry-after: failed {sorted(bad)}"
