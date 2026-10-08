def request_cost(usage, prices):
    """Return the dollar cost of one request, rounded to 6 decimals.

    usage:  dict with input_tokens, output_tokens, cache_read_input_tokens,
            cache_creation_input_tokens (cache keys may be missing or None)
    prices: dict with input, output, cache_read, cache_write in $ per million tokens
    """
    # TODO
    pass


def monthly_cost(requests_per_day, usage, prices, days=30):
    """Return the dollar cost of requests_per_day identical requests for `days` days, rounded to 2 decimals."""
    # TODO
    pass


# --- Try it out (not graded) ---
PRICES = {
    "claude-opus-5-5": {"input": 4.00, "output": 20.00, "cache_read": 0.20, "cache_write": 5.00},
    "claude-sonnet-5-5": {"input": 2.00, "output": 10.00, "cache_read": 0.20, "cache_write": 2.50},
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
