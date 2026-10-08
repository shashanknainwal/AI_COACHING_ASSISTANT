# Prices here are passed in explicitly, in dollars per million tokens.
OPUS = {"input": 4.00, "output": 20.00, "cache_read": 0.20, "cache_write": 5.00}
SONNET = {"input": 2.00, "output": 10.00, "cache_read": 0.10, "cache_write": 2.50}
MADE_UP = {"input": 3.00, "output": 15.00, "cache_read": 0.30, "cache_write": 3.75}


def _usage(inp=0, out=0, read=0, write=0):
    return {
        "input_tokens": inp,
        "output_tokens": out,
        "cache_read_input_tokens": read,
        "cache_creation_input_tokens": write,
    }


def test_input_and_output_only():
    """request_cost() prices input and output tokens per million"""
    got = request_cost(_usage(inp=3000, out=500), OPUS)
    assert got == 0.022, f"3,000 input x $4/M + 500 output x $20/M = $0.022, got {got!r}"


def test_uses_the_prices_passed_in():
    """request_cost() uses the price table it is given, not hard-coded prices"""
    got = request_cost(_usage(inp=3000, out=500), MADE_UP)
    assert got == 0.0165, f"with input $3/M and output $15/M the cost is $0.0165, got {got!r}"


def test_cache_read_and_write():
    """request_cost() bills cache reads and cache writes at their own prices"""
    warm = request_cost(_usage(inp=1000, out=400, read=20000), SONNET)
    assert warm == 0.008, f"a cache-hit request should cost $0.008 (20,000 x $0.10/M + 1,000 x $2/M + 400 x $10/M), got {warm!r}"
    cold = request_cost(_usage(inp=1000, out=400, write=20000), SONNET)
    assert cold == 0.056, f"a cache-write request should cost $0.056 (20,000 x $2.50/M + 1,000 x $2/M + 400 x $10/M), got {cold!r}"


def test_missing_or_none_cache_fields():
    """request_cost() treats missing or None cache fields as 0"""
    got = request_cost({"input_tokens": 3000, "output_tokens": 500}, OPUS)
    assert got == 0.022, f"missing cache keys should count as 0 tokens, got {got!r}"
    usage = _usage(inp=3000, out=500)
    usage["cache_read_input_tokens"] = None
    usage["cache_creation_input_tokens"] = None
    got = request_cost(usage, OPUS)
    assert got == 0.022, f"None cache fields should count as 0 tokens, got {got!r}"


def test_rounds_to_six_decimals():
    """request_cost() rounds to 6 decimal places"""
    got = request_cost(_usage(inp=7, out=3), MADE_UP)
    assert got == 6.6e-05, f"7 x $3/M + 3 x $15/M = $0.000066, got {got!r}"
    got = request_cost(_usage(inp=1, out=1), {"input": 0.1, "output": 0.5, "cache_read": 0, "cache_write": 0})
    assert got == 1e-06, f"1 x $0.10/M + 1 x $0.50/M = $0.0000006, which rounds to $0.000001, got {got!r}"


def test_monthly_cost():
    """monthly_cost() multiplies by requests per day and days, rounded to 2 decimals"""
    got = monthly_cost(100_000, _usage(inp=3000, out=500), OPUS)
    assert got == 66000.0, f"$0.022 x 100,000/day x 30 days = $66,000, got {got!r}"
    got = monthly_cost(1000, _usage(inp=3000, out=500), SONNET, days=7)
    assert got == 77.0, f"$0.011 x 1,000/day x 7 days = $77, got {got!r}"


def test_monthly_cost_does_not_round_per_request_first():
    """monthly_cost() rounds only the final total"""
    tiny = {"input": 0.1, "output": 0.5, "cache_read": 0, "cache_write": 0}
    got = monthly_cost(1_000_000, _usage(inp=1, out=1), tiny)
    assert got == 18.0, f"$0.0000006 x 1,000,000/day x 30 days = $18.00; rounding each request to $0.000001 first would give $30.00. Got {got!r}"
