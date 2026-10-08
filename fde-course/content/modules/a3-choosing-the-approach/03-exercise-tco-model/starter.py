SONNET_PRICES = {"input": 2.00, "output": 10.00, "cache_write": 2.50, "cache_read": 0.20}
BATCH_DISCOUNT = 0.5  # the Batch API bills every token type at half price

# Harborview Mutual (fictional): 40,000 claim documents a month.
OPTIONS = [
    {
        "name": "status_quo",
        "one_time": 0,
        "monthly_fixed": 0,
        "go_live_month": 1,
        "prices": None,
        "workload": {"requests": 40_000, "review_rate": 1.0, "review_minutes": 8, "reviewer_hourly": 42},
    },
    {
        "name": "buy_isv",
        "one_time": 40_000,
        "monthly_fixed": 60_000,
        "go_live_month": 2,
        "prices": None,
        "workload": {"requests": 40_000, "review_rate": 0.30, "review_minutes": 4, "reviewer_hourly": 42},
    },
    {
        "name": "build_api",
        "one_time": 250_000,
        "monthly_fixed": 18_000,
        "go_live_month": 4,
        "prices": SONNET_PRICES,
        "workload": {
            "requests": 40_000, "prefix_tokens": 6_000, "caching": True, "cache_hit_rate": 0.95,
            "input_tokens": 4_000, "output_tokens": 800, "batch_share": 0.6,
            "review_rate": 0.15, "review_minutes": 4, "reviewer_hourly": 42,
        },
    },
]


def monthly_api_cost(workload, prices):
    """Monthly model spend in dollars, rounded to 2 decimals. prices=None means no LLM."""
    # TODO
    pass


def monthly_review_cost(workload):
    """Monthly human review cost in dollars, rounded to 2 decimals."""
    # TODO
    pass


def monthly_run_cost(option):
    """Steady-state monthly cost once live: fixed + API + review, rounded to 2 decimals."""
    # TODO
    pass


def cumulative_costs(option, months=12, baseline=None):
    """Cumulative cost at the end of each month (list of length `months`, each rounded to 2 decimals)."""
    # TODO
    pass


def compare(options, months=12, baseline_name=None):
    """Rank options by total cost over the horizon, with break-even month against the baseline."""
    # TODO
    pass


# --- Try it out (not graded) ---
if __name__ == "__main__":
    print("API cost, build option:", monthly_api_cost(OPTIONS[2]["workload"], OPTIONS[2]["prices"]))
    print("Review cost, status quo:", monthly_review_cost(OPTIONS[0]["workload"]))
    for row in compare(OPTIONS, months=12, baseline_name="status_quo") or []:
        print(row)
