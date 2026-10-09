def _tokens(usage, key):
    """Read a token count from usage, treating a missing key or None as 0."""
    return usage.get(key) or 0


def _raw_cost(usage, prices):
    """Unrounded dollar cost of one request."""
    total = (
        _tokens(usage, "input_tokens") * prices["input"]
        + _tokens(usage, "output_tokens") * prices["output"]
        + _tokens(usage, "cache_read_input_tokens") * prices["cache_read"]
        + _tokens(usage, "cache_creation_input_tokens") * prices["cache_write"]
    )
    return total / 1_000_000


def request_cost(usage, prices):
    """Return the dollar cost of one request, rounded to 6 decimals."""
    return round(_raw_cost(usage, prices), 6)


def monthly_cost(requests_per_day, usage, prices, days=30):
    """Return the dollar cost of a month of identical requests, rounded to 2 decimals."""
    return round(_raw_cost(usage, prices) * requests_per_day * days, 2)


# --- Try it out (not graded) ---
PRICES = {
    "claude-opus-5-5": {"input": 4.00, "output": 20.00, "cache_read": 0.20, "cache_write": 5.00},
    "claude-sonnet-5-5": {"input": 2.00, "output": 10.00, "cache_read": 0.10, "cache_write": 2.50},
}

usage = {
    "input_tokens": 1000,
    "output_tokens": 400,
    "cache_read_input_tokens": 20000,
    "cache_creation_input_tokens": 0,
}

for model, p in PRICES.items():
    print(model, "per request:", request_cost(usage, p))
    print(model, "per month at 50,000/day:", monthly_cost(50_000, usage, p))
