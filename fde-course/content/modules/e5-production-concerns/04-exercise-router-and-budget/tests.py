import copy

_ROUTES_BEFORE = copy.deepcopy(ROUTES)


def _raises(fn, exc_type, contains=""):
    try:
        fn()
    except exc_type as exc:
        assert contains in str(exc), f"error message should mention {contains!r}, got {str(exc)!r}"
        return
    raise AssertionError(f"expected {exc_type.__name__}")


def test_route_basics():
    """route() returns a copy of the task's route and rejects unknown tasks"""
    r = route("classify_email", 1_000)
    assert r == {"model": HAIKU, "effort": "low", "max_tokens": 512}, f"got {r}"
    r["model"] = "changed"
    assert ROUTES == _ROUTES_BEFORE, "return a copy; never modify ROUTES"
    assert route("draft_reply", 1_000) == {"model": SONNET, "effort": "medium", "max_tokens": 4096}
    _raises(lambda: route("write_poem", 10), ValueError, "unknown task: write_poem")


def test_route_complexity_and_size():
    """High complexity moves one step up the ladder (or raises Opus effort); big prompts skip Haiku"""
    assert route("extract_invoice", 1_000, "high") == {"model": SONNET, "effort": "low", "max_tokens": 2048}, \
        "high complexity on Haiku moves up to Sonnet, keeping effort and max_tokens"
    assert route("draft_reply", 1_000, "high") == {"model": OPUS, "effort": "medium", "max_tokens": 4096}
    assert route("audit_anomaly", 1_000, "high") == {"model": OPUS, "effort": "high", "max_tokens": 16000}, \
        "Opus is the top of the ladder: raise effort to high instead"
    assert route("extract_invoice", 150_000) == {"model": SONNET, "effort": "low", "max_tokens": 2048}, \
        "prompts over 100,000 tokens don't go to Haiku"
    assert route("classify_email", 100_000)["model"] == HAIKU, "exactly 100,000 tokens is still fine for Haiku"


def test_call_cost_four_meters():
    """call_cost() prices input, output, cache writes and cache reads"""
    got = call_cost(OPUS, {"input_tokens": 10_000, "output_tokens": 2_000,
                           "cache_creation_input_tokens": 50_000, "cache_read_input_tokens": 0})
    assert got == 0.33, f"10K x $4 + 2K x $20 + 50K x $5 (5-minute writes) per million = $0.33; got {got}"
    got = call_cost(SONNET, {"input_tokens": 3_000, "output_tokens": 600, "cache_read_input_tokens": 12_000})
    assert got == 0.0132, f"missing fields count as 0; got {got}"
    got = call_cost(HAIKU, {"input_tokens": 3_000, "output_tokens": 500,
                            "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0})
    assert got == 0.00055, f"zero cache tokens need no cache price; got {got}"


def test_call_cost_ttl_split_and_batch():
    """Cache writes are priced by TTL when usage has the breakdown; batch halves everything"""
    usage = {"input_tokens": 1_000, "output_tokens": 500, "cache_creation_input_tokens": 30_000,
             "cache_read_input_tokens": 200_000,
             "cache_creation": {"ephemeral_5m_input_tokens": 10_000, "ephemeral_1h_input_tokens": 20_000}}
    got = call_cost(OPUS, usage)
    assert got == 0.264, f"10K at the 5-minute rate ($5) and 20K at the 1-hour rate ($8): expected 0.264, got {got}"
    got = call_cost(SONNET, {"input_tokens": 3_000, "output_tokens": 600, "cache_read_input_tokens": 12_000}, batch=True)
    assert got == 0.0066, f"batch is 50% off every token type: expected 0.0066, got {got}"


def test_call_cost_refuses_to_guess():
    """Unknown models and missing rates raise instead of silently pricing at $0"""
    _raises(lambda: call_cost("claude-unknown-1", {"input_tokens": 1}), ValueError, "no prices for claude-unknown-1")
    _raises(lambda: call_cost(HAIKU, {"input_tokens": 100, "cache_read_input_tokens": 5_000}),
            ValueError, "no cache_read price for claude-haiku-5-5")
    _raises(lambda: call_cost(HAIKU, {"input_tokens": 100, "cache_creation_input_tokens": 5_000}),
            ValueError, "no cache_write_5m price for claude-haiku-5-5")
    custom = {"m": {"input": 1.0, "output": 2.0}}
    assert call_cost("m", {"input_tokens": 1_000_000, "output_tokens": 500_000}, prices=custom) == 2.0, \
        "use the prices argument, not the global table"


def test_worst_case_cost():
    """worst_case_cost() assumes no cache hits and output up to max_tokens"""
    assert worst_case_cost({"model": OPUS, "effort": "high", "max_tokens": 16000}, 40_000) == 0.48
    assert worst_case_cost({"model": SONNET, "effort": "medium", "max_tokens": 4096}, 6_000) == 0.05296


def test_admit_within_budget():
    """admit() returns the normal route, marked not degraded, when it fits"""
    g = BudgetGuard(1.00)
    got = g.admit("draft_reply", 6_000, "2026-10-30")
    assert got == {"model": SONNET, "effort": "medium", "max_tokens": 4096, "degraded": False}, f"got {got}"


def test_admit_degrades_when_tight():
    """When the worst case doesn't fit, a degradable task steps down to the most capable model that does"""
    got = BudgetGuard(0.10).admit("draft_reply", 6_000, "d", "high")
    assert got == {"model": SONNET, "effort": "medium", "max_tokens": 4096, "degraded": True}, \
        f"Opus worst case is $0.10592 > $0.10; Sonnet ($0.05296) fits. got {got}"
    got = BudgetGuard(0.01).admit("draft_reply", 6_000, "d", "high")
    assert got is not None and got["model"] == HAIKU and got["degraded"] is True, f"only Haiku fits $0.01; got {got}"
    _raises(lambda: BudgetGuard(0.01).admit("draft_reply", 150_000, "d"), BudgetExceeded)


def test_admit_rejects_non_degradable():
    """A task outside DEGRADABLE is rejected rather than downgraded"""
    _raises(lambda: BudgetGuard(0.40).admit("audit_anomaly", 40_000, "d"), BudgetExceeded, "audit_anomaly")
    got = BudgetGuard(0.50).admit("audit_anomaly", 40_000, "d")
    assert got == {"model": OPUS, "effort": "medium", "max_tokens": 16000, "degraded": False}, f"got {got}"


def test_budget_counts_actual_spend_per_day():
    """Recorded spend shrinks what's left today; a new day starts fresh"""
    g = BudgetGuard(0.10)
    cost = g.record("d1", "draft_reply", SONNET, {"input_tokens": 10_000, "output_tokens": 4_000}, True)
    assert cost == 0.06, f"record() returns the call's cost; got {cost}"
    assert g.spent("d1") == 0.06
    got = g.admit("draft_reply", 6_000, "d1")
    assert got is not None and got["model"] == HAIKU and got["degraded"] is True, \
        f"$0.04 left: Sonnet's $0.05296 worst case doesn't fit, Haiku does. got {got}"
    got = g.admit("draft_reply", 6_000, "d2")
    assert got is not None and got["degraded"] is False, "a different day has its own budget"
    assert g.record("d2", "classify_email", SONNET, {"input_tokens": 3_000, "output_tokens": 600,
                                                     "cache_read_input_tokens": 12_000}, True, batch=True) == 0.0066


def test_report_cost_per_completed_task():
    """report() includes failed attempts in cost per completed task"""
    g = BudgetGuard(1.00)
    d = "2026-10-30"
    g.record(d, "extract_invoice", HAIKU, {"input_tokens": 3_200, "output_tokens": 420}, True)
    g.record(d, "extract_invoice", HAIKU, {"input_tokens": 2_900, "output_tokens": 2_048}, False)
    g.record(d, "extract_invoice", SONNET, {"input_tokens": 1_100, "output_tokens": 380, "cache_read_input_tokens": 1_800}, True)
    g.record(d, "draft_reply", SONNET, {"input_tokens": 2_000, "output_tokens": 900, "cache_creation_input_tokens": 4_000}, True)
    g.record(d, "audit_anomaly", OPUS, {"input_tokens": 5_000, "output_tokens": 1_000}, False)
    got = g.report(d)
    expected = {
        "spent": 0.071024,
        "remaining": 0.928976,
        "by_model": {HAIKU: 0.001844, SONNET: 0.02918, OPUS: 0.04},
        "cost_per_completed": {"extract_invoice": 0.004012, "draft_reply": 0.023, "audit_anomaly": None},
    }
    assert got == expected, f"expected {expected}\n got {got}"
