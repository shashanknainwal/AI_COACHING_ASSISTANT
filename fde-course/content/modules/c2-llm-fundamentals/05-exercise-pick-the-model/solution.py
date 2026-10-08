def _qualifying(candidates, min_quality, max_latency_ms, budget_per_1k):
    """Candidates that meet every constraint (all limits are inclusive)."""
    return [
        c for c in candidates
        if c["quality"] >= min_quality
        and c["p95_latency_ms"] <= max_latency_ms
        and c["cost_per_1k_requests"] <= budget_per_1k
    ]


def choose_model(candidates, min_quality, max_latency_ms, budget_per_1k):
    """Return the name of the cheapest qualifying model, or None."""
    ok = _qualifying(candidates, min_quality, max_latency_ms, budget_per_1k)
    if not ok:
        return None
    best = min(ok, key=lambda c: (c["cost_per_1k_requests"], -c["quality"], c["name"]))
    return best["name"]


def explain_choice(candidates, min_quality, max_latency_ms, budget_per_1k):
    """Return a one-line explanation of the choice."""
    ok = _qualifying(candidates, min_quality, max_latency_ms, budget_per_1k)
    name = choose_model(candidates, min_quality, max_latency_ms, budget_per_1k)
    if name is None:
        return f"No model qualifies: 0 of {len(candidates)} meet quality >= {min_quality:.2f}, p95 <= {max_latency_ms} ms, cost <= ${budget_per_1k:.2f}/1k"
    c = next(c for c in candidates if c["name"] == name)
    return (
        f"{name}: quality {c['quality']:.2f}, p95 {c['p95_latency_ms']} ms, "
        f"${c['cost_per_1k_requests']:.2f}/1k requests ({len(ok)} of {len(candidates)} qualified)"
    )


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
