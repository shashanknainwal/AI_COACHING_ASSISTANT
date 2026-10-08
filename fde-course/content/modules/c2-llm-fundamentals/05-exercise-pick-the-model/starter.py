def choose_model(candidates, min_quality, max_latency_ms, budget_per_1k):
    """Return the name of the cheapest model that meets quality, latency and budget, or None.

    Ties on cost: higher quality wins, then name alphabetically.
    """
    # TODO
    pass


def explain_choice(candidates, min_quality, max_latency_ms, budget_per_1k):
    """Return a one-line explanation in the exact format from the instructions."""
    # TODO
    pass


# --- Try it out (not graded) ---
eval_table = [
    {"name": "Model A", "quality": 0.96, "p95_latency_ms": 4200, "cost_per_1k_requests": 22.00},
    {"name": "Model B", "quality": 0.93, "p95_latency_ms": 2100, "cost_per_1k_requests": 11.00},
    {"name": "Model C", "quality": 0.81, "p95_latency_ms": 900, "cost_per_1k_requests": 0.55},
    {"name": "Model D", "quality": 0.91, "p95_latency_ms": 2600, "cost_per_1k_requests": 6.00},
]

print(choose_model(eval_table, 0.90, 3000, 15.00))
print(explain_choice(eval_table, 0.90, 3000, 15.00))
print(explain_choice(eval_table, 0.98, 3000, 15.00))
