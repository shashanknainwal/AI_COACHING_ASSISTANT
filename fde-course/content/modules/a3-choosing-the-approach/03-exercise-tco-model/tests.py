import copy

_OPTIONS_BEFORE = copy.deepcopy(OPTIONS)

_P = {"input": 2.00, "output": 10.00, "cache_write": 2.50, "cache_read": 0.10}


def _raises(fn, exc_type, contains=""):
    try:
        fn()
    except exc_type as exc:
        assert contains in str(exc), f"error message should mention {contains!r}, got {str(exc)!r}"
        return
    raise AssertionError(f"expected {exc_type.__name__}")


def test_api_cost_uncached():
    """monthly_api_cost() prices prefix, input and output without caching"""
    w = {"requests": 10_000, "prefix_tokens": 5_000, "input_tokens": 1_000, "output_tokens": 500}
    got = monthly_api_cost(w, _P)
    assert got == 170.0, f"(5,000 x $2 + 1,000 x $2 + 500 x $10) / 1M = $0.017 per request x 10,000 = $170.00; got {got}"
    assert monthly_api_cost(w, None) == 0.0, "prices=None means the option makes no API calls: return 0.0"
    assert monthly_api_cost({"requests": 3}, _P) == 0.0, "missing token fields count as 0"


def test_api_cost_caching():
    """Cache hits bill at the read rate, misses at the write rate"""
    w = {"requests": 10_000, "prefix_tokens": 5_000, "caching": True, "cache_hit_rate": 0.9,
         "input_tokens": 1_000, "output_tokens": 500}
    got = monthly_api_cost(w, _P)
    assert got == 87.0, (
        "prefix rate = 0.9 x $0.10 + 0.1 x $2.50 = $0.34 per million; "
        f"(5,000 x 0.34 + 1,000 x 2 + 500 x 10) / 1M x 10,000 = $87.00; got {got}"
    )
    cold = dict(w, cache_hit_rate=0.0)
    assert monthly_api_cost(cold, _P) == 195.0, \
        "a 0% hit rate means every request pays the write premium: (5,000 x 2.50 + 2,000 + 5,000) / 1M x 10,000 = $195.00"


def test_api_cost_batch():
    """batch_share sends that fraction of requests through the 50% batch discount"""
    w = {"requests": 10_000, "prefix_tokens": 5_000, "input_tokens": 1_000, "output_tokens": 500, "batch_share": 1.0}
    assert monthly_api_cost(w, _P) == 85.0, "all traffic in batch halves $170.00 to $85.00"
    w["batch_share"] = 0.6
    got = monthly_api_cost(w, _P)
    assert got == 119.0, f"60% at half price: $170 x (1 - 0.6 x 0.5) = $119.00; got {got}"


def test_build_option_api_cost():
    """Harborview's build option: under $500 a month of model spend"""
    got = monthly_api_cost(OPTIONS[2]["workload"], OPTIONS[2]["prices"])
    assert got == 484.96, f"expected 484.96, got {got}"


def test_review_cost():
    """monthly_review_cost() = requests x review_rate x minutes / 60 x hourly rate"""
    got = monthly_review_cost(OPTIONS[0]["workload"])
    assert got == 224000.0, f"40,000 x 1.0 x 8 / 60 x $42 = $224,000.00; got {got}"
    got = monthly_review_cost(OPTIONS[2]["workload"])
    assert got == 16800.0, f"40,000 x 0.15 x 4 / 60 x $42 = $16,800.00; got {got}"
    assert monthly_review_cost({"requests": 100}) == 0.0, "no review fields means no review cost"


def test_monthly_run_cost():
    """monthly_run_cost() adds fixed, API and review cost"""
    assert monthly_run_cost(OPTIONS[0]) == 224000.0
    assert monthly_run_cost(OPTIONS[1]) == 93600.0, "buy_isv: $60,000 licence + $0 API + $33,600 review"
    got = monthly_run_cost(OPTIONS[2])
    assert got == 35284.96, f"build_api: $18,000 + $484.96 + $16,800 = $35,284.96; got {got}"


def test_cumulative_costs_go_live():
    """Before go-live the old process keeps running; one-time cost lands in month 1"""
    base = OPTIONS[0]
    got = cumulative_costs(OPTIONS[2], 6, base)
    assert isinstance(got, list) and len(got) == 6, f"expected a list of 6 monthly totals, got {got!r}"
    assert got[:3] == [474000.0, 698000.0, 922000.0], \
        f"months 1-3: $250,000 one-time plus the status quo's $224,000 each month; got {got[:3]}"
    assert got[3:] == [957284.96, 992569.92, 1027854.88], f"from month 4 the option's own run cost applies; got {got[3:]}"
    no_base = cumulative_costs(OPTIONS[1], 3)
    assert no_base == [40000.0, 133600.0, 227200.0], \
        f"with no baseline, pre-live months cost nothing extra; got {no_base}"
    assert OPTIONS == _OPTIONS_BEFORE, "don't modify the options"


def test_compare_ranked_with_break_even():
    """compare() ranks by 12-month total and finds each option's break-even month"""
    rows = compare(OPTIONS, months=12, baseline_name="status_quo")
    assert isinstance(rows, list) and len(rows) == 3, f"expected 3 rows, got {rows!r}"
    assert [r["name"] for r in rows] == ["build_api", "buy_isv", "status_quo"], \
        f"cheapest 12-month total first; got {[r['name'] for r in rows]}"
    assert rows[0] == {"name": "build_api", "total": 1239564.64, "monthly_run": 35284.96,
                       "break_even_month": 5, "rank": 1}, f"got {rows[0]}"
    assert rows[1] == {"name": "buy_isv", "total": 1293600.0, "monthly_run": 93600.0,
                       "break_even_month": 2, "rank": 2}, f"got {rows[1]}"
    assert rows[2]["break_even_month"] is None and rows[2]["rank"] == 3, "the baseline has no break-even month"


def test_horizon_changes_the_answer():
    """Over 6 months buying wins; the horizon is part of the recommendation"""
    rows = compare(OPTIONS, months=6, baseline_name="status_quo")
    assert [r["name"] for r in rows] == ["buy_isv", "build_api", "status_quo"], \
        f"over 6 months: buy $732,000, build $1,027,854.88; got {[(r['name'], r['total']) for r in rows]}"


def test_never_breaks_even_and_errors():
    """break_even_month is None when an option never catches up; bad input raises"""
    pricey = {"name": "pricey", "one_time": 5_000_000, "monthly_fixed": 0, "go_live_month": 1,
              "prices": None, "workload": {"requests": 0}}
    rows = compare([OPTIONS[0], pricey], months=12, baseline_name="status_quo")
    by = {r["name"]: r for r in rows}
    assert by["pricey"]["break_even_month"] is None, "$5M up front never beats $224K/month within 12 months"
    rows = compare(OPTIONS, months=12)
    assert all(r["break_even_month"] is None for r in rows), "no baseline means no break-even months"
    _raises(lambda: compare(OPTIONS, baseline_name="nope"), ValueError, "unknown baseline: nope")
    _raises(lambda: compare([OPTIONS[0], OPTIONS[0]]), ValueError, "unique")
