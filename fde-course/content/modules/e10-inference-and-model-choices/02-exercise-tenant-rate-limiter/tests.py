SONNET, HAIKU, OPUS = "claude-sonnet-5-5", "claude-haiku-5-5", "claude-opus-5-5"


def _gw(pool=100_000):
    return Gateway(
        tenants={"a": {"tokens_per_min": 60_000, "requests_per_min": 60},
                 "b": {"tokens_per_min": 60_000, "requests_per_min": 3}},
        pools={SONNET: pool, HAIKU: 600_000, OPUS: 60_000},
    )


def _req(rid, tenant="a", priority="standard", model=SONNET, inp=1_000, mx=1_000):
    return {"id": rid, "tenant": tenant, "priority": priority, "model": model, "input_tokens": inp, "max_tokens": mx}


def _raises(fn, contains):
    try:
        fn()
    except ValueError as exc:
        assert contains in str(exc), f"error should mention {contains!r}, got {str(exc)!r}"
        return
    raise AssertionError(f"expected ValueError mentioning {contains!r}")


def test_bucket_refill_and_cap():
    """TokenBucket refills with time, never above capacity, and a failed take costs nothing"""
    b = TokenBucket(600, 10, now=0)
    assert b.try_take(500, now=0) is True, "a full bucket of 600 can give 500"
    assert abs(b.available(now=0) - 100) < 1e-9, "100 left after taking 500"
    assert b.try_take(200, now=0) is False, "only 100 left: refuse 200"
    assert abs(b.available(now=0) - 100) < 1e-9, "a refused take must not remove tokens"
    assert abs(b.available(now=5) - 150) < 1e-9, "5 seconds at 10 tokens/s adds 50"
    assert abs(b.available(now=1_000) - 600) < 1e-9, "refill stops at capacity"


def test_bucket_adjust():
    """adjust() refunds up to capacity and can charge the bucket below zero"""
    b = TokenBucket(100, 1, now=0)
    b.try_take(80, now=0)
    b.adjust(500, now=0)
    assert abs(b.available(now=0) - 100) < 1e-9, "a refund never lifts the bucket above capacity"
    b.adjust(-150, now=0)
    assert abs(b.available(now=0) + 50) < 1e-9, "a request that used more than it reserved leaves a debt (negative tokens)"


def test_submit_validates():
    """submit() rejects unknown tenants, priorities and models, and requests that can never fit"""
    gw = _gw()
    _raises(lambda: gw.submit(_req("x", tenant="zzz"), now=0), "unknown tenant")
    _raises(lambda: gw.submit(_req("x", priority="urgent"), now=0), "unknown priority")
    _raises(lambda: gw.submit(_req("x", model="claude-nope"), now=0), "unknown model")
    _raises(lambda: gw.submit(_req("x", inp=50_000, mx=20_000), now=0), "never fit")
    assert gw.submit(_req("ok"), now=0) is None and len(gw.queue) == 1, "a valid request is queued, not admitted"


def test_drain_reserves_input_plus_max_tokens():
    """drain() reserves input_tokens + max_tokens from the tenant and the model pool"""
    gw = _gw()
    gw.submit(_req("r1", inp=10_000, mx=5_000), now=0)
    got = gw.drain(now=0)
    assert got == ["r1"], f"r1 fits and should be admitted, got {got}"
    assert abs(gw.tenant_tokens["a"].available(0) - 45_000) < 1e-6, "tenant a reserved 15,000 of 60,000"
    assert abs(gw.pools[SONNET].available(0) - 85_000) < 1e-6, "the Sonnet pool reserved 15,000 too"
    assert abs(gw.tenant_requests["a"].available(0) - 59) < 1e-6, "one request taken from the request bucket"
    assert gw.queue == [] and "r1" in gw.in_flight, "admitted requests leave the queue and go in flight"


def test_priority_order_on_shared_pool():
    """Interactive goes first on a shared pool, and lower priority can't jump a waiting request"""
    gw = _gw(pool=30_000)
    gw.submit(_req("batch1", tenant="a", priority="batch", inp=10_000, mx=5_000), now=0)
    gw.submit(_req("int1", tenant="b", priority="interactive", inp=10_000, mx=10_000), now=0)
    gw.submit(_req("small_batch", tenant="a", priority="batch", inp=500, mx=500), now=0)
    got = gw.drain(now=0)
    assert got and got[0] == "int1", f"interactive is admitted first, got {got}"
    assert "batch1" not in got, "batch1 needs 15,000 but only 10,000 is left in the pool"
    assert got == ["int1"], ("once batch1 is waiting on the Sonnet pool, the smaller batch request behind it "
                             f"must not jump ahead on that pool; got {got}")


def test_one_tenant_does_not_block_another():
    """A tenant out of tokens or requests waits; other tenants keep flowing"""
    gw = _gw()
    for i in range(4):
        gw.submit(_req(f"b{i}", tenant="b", priority="interactive"), now=0)
    gw.submit(_req("a0", tenant="a", priority="batch", model=HAIKU), now=0)
    got = gw.drain(now=0)
    assert got == ["b0", "b1", "b2", "a0"], f"tenant b has 3 requests a minute; a0 still goes. Got {got}"
    assert [q["id"] for q in gw.queue] == ["b3"], "b3 waits in the queue"
    assert gw.drain(now=10) == [], "after 10 s tenant b has refilled only half a request"
    assert gw.drain(now=20) == ["b3"], "after 20 s tenant b has a whole request again"


def test_aging_prevents_starvation():
    """A batch request that has waited long enough outranks a fresh standard request"""
    gw = _gw()
    gw.submit(_req("old_batch", priority="batch"), now=0)
    gw.submit(_req("new_std", priority="standard"), now=45)
    q = {x["id"]: x for x in gw.queue}
    assert gw.effective_priority(q["old_batch"], 45) == 1, "45 s of waiting promotes batch (2) to 1"
    assert gw.effective_priority(q["old_batch"], 75) == 0, "75 s promotes it twice, to 0"
    assert gw.effective_priority(q["new_std"], 200) == 0, "never below 0"
    assert gw.drain(now=45) == ["old_batch", "new_std"], "same effective priority: the earlier arrival goes first"


def test_complete_refunds_and_attributes_cost():
    """complete() refunds unused tokens (cache reads don't count) and prices usage per model"""
    gw = _gw()
    gw.submit(_req("r1", tenant="b", inp=8_000, mx=4_000), now=0)
    gw.drain(now=0)
    usage = {"input_tokens": 1_000, "cache_read_input_tokens": 7_000,
             "cache_creation_input_tokens": 0, "output_tokens": 500}
    cost = gw.complete("r1", usage, now=0)
    assert cost == 0.0077, f"1,000 x $2 + 7,000 x $0.10 + 500 x $10 per million = $0.0077, got {cost}"
    assert abs(gw.tenant_tokens["b"].available(0) - 58_500) < 1e-6, (
        "reserved 12,000, used 1,500 (input + cache writes + output; cache reads don't count): 58,500 left")
    assert gw.costs() == {"a": 0.0, "b": 0.0077}, f"got {gw.costs()}"
    _raises(lambda: gw.complete("r1", usage, now=1), "unknown request")


def test_complete_cache_writes_and_overrun():
    """Cache writes count and are priced at the write rate; an overrun leaves the tenant in debt"""
    gw = _gw()
    gw.submit(_req("r2", model=OPUS, inp=2_000, mx=1_000), now=0)
    gw.drain(now=0)
    cost = gw.complete("r2", {"input_tokens": 200, "cache_creation_input_tokens": 1_800, "output_tokens": 1_500}, now=0)
    assert cost == 0.0398, f"200 x $4 + 1,800 x $5 + 1,500 x $20 per million = $0.0398, got {cost}"
    assert abs(gw.pools[OPUS].available(0) - 56_500) < 1e-6, "reserved 3,000, used 3,500: the pool pays 500 extra"
