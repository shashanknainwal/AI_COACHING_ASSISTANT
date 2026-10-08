SONNET_PRICES = {"input": 2.00, "output": 10.00, "cache_write": 2.50, "cache_read": 0.10}
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
    if prices is None:
        return 0.0
    prefix = workload.get("prefix_tokens", 0)
    if workload.get("caching", False):
        hit = workload.get("cache_hit_rate", 0.0)
        prefix_rate = hit * prices["cache_read"] + (1 - hit) * prices["cache_write"]
    else:
        prefix_rate = prices["input"]
    per_request = (
        prefix * prefix_rate
        + workload.get("input_tokens", 0) * prices["input"]
        + workload.get("output_tokens", 0) * prices["output"]
    ) / 1_000_000
    batch_share = workload.get("batch_share", 0.0)
    discount = 1 - batch_share * (1 - BATCH_DISCOUNT)
    return round(workload.get("requests", 0) * per_request * discount, 2)


def monthly_review_cost(workload):
    """Monthly human review cost in dollars, rounded to 2 decimals."""
    reviewed = workload.get("requests", 0) * workload.get("review_rate", 0.0)
    hours = reviewed * workload.get("review_minutes", 0) / 60
    return round(hours * workload.get("reviewer_hourly", 0), 2)


def monthly_run_cost(option):
    """Steady-state monthly cost once live: fixed + API + review, rounded to 2 decimals."""
    w = option["workload"]
    total = option.get("monthly_fixed", 0) + monthly_api_cost(w, option.get("prices")) + monthly_review_cost(w)
    return round(total, 2)


def cumulative_costs(option, months=12, baseline=None):
    """Cumulative cost at the end of each month (list of length `months`, each rounded to 2 decimals)."""
    run = monthly_run_cost(option)
    legacy = monthly_run_cost(baseline) if baseline is not None else 0.0
    live = option.get("go_live_month", 1)
    out, total = [], option.get("one_time", 0)
    for month in range(1, months + 1):
        total += run if month >= live else legacy
        out.append(round(total, 2))
    return out


def compare(options, months=12, baseline_name=None):
    """Rank options by total cost over the horizon, with break-even month against the baseline."""
    names = [o["name"] for o in options]
    if len(set(names)) != len(names):
        raise ValueError("option names must be unique")
    baseline = None
    if baseline_name is not None:
        matches = [o for o in options if o["name"] == baseline_name]
        if not matches:
            raise ValueError(f"unknown baseline: {baseline_name}")
        baseline = matches[0]
    base_curve = cumulative_costs(baseline, months) if baseline is not None else None

    rows = []
    for o in options:
        is_base = baseline is not None and o["name"] == baseline_name
        curve = cumulative_costs(o, months, None if is_base else baseline)
        be = None
        if base_curve is not None and not is_base:
            be = next((m + 1 for m in range(months) if curve[m] <= base_curve[m]), None)
        rows.append({"name": o["name"], "total": curve[-1], "monthly_run": monthly_run_cost(o), "break_even_month": be})
    rows.sort(key=lambda r: (r["total"], r["name"]))
    for i, r in enumerate(rows, start=1):
        r["rank"] = i
    return rows


# --- Try it out (not graded) ---
if __name__ == "__main__":
    for row in compare(OPTIONS, months=12, baseline_name="status_quo"):
        print(row)
