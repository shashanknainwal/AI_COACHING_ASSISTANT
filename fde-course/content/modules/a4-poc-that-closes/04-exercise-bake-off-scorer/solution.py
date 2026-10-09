import math

# EVAL_CASE_IDS, RESULTS, PRICING and CONSTRAINTS (Ellery Bank bake-off) are loaded for you.


def check_same_cases(case_ids, results):
    """Coverage problems per candidate: missing, unknown and duplicate case ids. Clean candidates are left out."""
    expected = set(case_ids)
    problems = {}
    for name, records in results.items():
        ids = [r["id"] for r in records]
        got = set(ids)
        missing = [c for c in case_ids if c not in got]
        unknown = sorted(got - expected)
        duplicates = sorted({i for i in ids if ids.count(i) > 1})
        if missing or unknown or duplicates:
            problems[name] = {"missing": missing, "unknown": unknown, "duplicates": duplicates}
    return problems


def percentile(values, p):
    """Nearest-rank percentile: the ceil(p/100 * n)-th smallest value. None for an empty list."""
    if not values:
        return None
    ordered = sorted(values)
    k = max(1, math.ceil(p / 100 * len(ordered)))
    return ordered[k - 1]


def wilson_interval(passes, n, z=1.96):
    """95% Wilson score interval, as (low, high) rounded to 3 decimals. (0.0, 1.0) when n is 0."""
    if n == 0:
        return (0.0, 1.0)
    p = passes / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (round(center - half, 3), round(center + half, 3))


def score_candidate(records, pricing, case_ids):
    """Quality with an interval, error rate, cost per task and p95 latency for one candidate."""
    wanted = set(case_ids)
    kept = {}
    for r in records:
        if r["id"] in wanted and r["id"] not in kept:
            kept[r["id"]] = r
    rows = list(kept.values())
    scored = [r for r in rows if r["error"] is None]
    passes = sum(1 for r in scored if r["correct"])
    errors = len(case_ids) - len(scored)
    cost = sum(r["input_tokens"] * pricing["input_per_mtok"] + r["output_tokens"] * pricing["output_per_mtok"]
               for r in rows) / 1_000_000
    return {
        "n": len(scored),
        "passes": passes,
        "accuracy": round(passes / len(scored), 3) if scored else None,
        "ci": wilson_interval(passes, len(scored)),
        "errors": errors,
        "error_rate": round(errors / len(case_ids), 3) if case_ids else None,
        "cost_per_task": round(cost / len(rows), 6) if rows else None,
        "p95_ms": percentile([r["latency_ms"] for r in rows], 95),
    }


def _reasons(s, c):
    out = []
    if s["accuracy"] is None:
        out.append("no scored cases")
    elif c.get("min_accuracy") is not None and s["accuracy"] < c["min_accuracy"]:
        out.append(f"accuracy {s['accuracy']:.1%} below {c['min_accuracy']:.1%}")
    if c.get("max_cost_per_task") is not None and s["cost_per_task"] is not None and s["cost_per_task"] > c["max_cost_per_task"]:
        out.append(f"cost ${s['cost_per_task']:.4f} per task above ${c['max_cost_per_task']:.4f}")
    if c.get("max_p95_ms") is not None and s["p95_ms"] is not None and s["p95_ms"] > c["max_p95_ms"]:
        out.append(f"p95 latency {s['p95_ms']} ms above {c['max_p95_ms']} ms")
    if c.get("max_error_rate") is not None and s["error_rate"] is not None and s["error_rate"] > c["max_error_rate"]:
        out.append(f"error rate {s['error_rate']:.1%} above {c['max_error_rate']:.1%}")
    return out


def pick_winner(scores, constraints):
    """Filter on hard constraints, find the quality leader, treat overlapping intervals as tied, pick the cheapest tied."""
    disqualified = {}
    eligible = []
    for name in sorted(scores):
        reasons = _reasons(scores[name], constraints)
        if reasons:
            disqualified[name] = reasons
        else:
            eligible.append(name)
    if not eligible:
        return {"winner": None, "leader": None, "tied": [], "disqualified": disqualified}
    leader = min(eligible, key=lambda n: (-scores[n]["accuracy"], scores[n]["cost_per_task"], n))
    floor = scores[leader]["ci"][0]
    tied = sorted(n for n in eligible if scores[n]["ci"][1] >= floor)
    winner = min(tied, key=lambda n: (scores[n]["cost_per_task"], -scores[n]["accuracy"], n))
    return {"winner": winner, "leader": leader, "tied": tied, "disqualified": disqualified}


# --- Try it out (not graded) ---
print("Coverage problems:", check_same_cases(EVAL_CASE_IDS, RESULTS))
scores = {name: score_candidate(recs, PRICING[name], EVAL_CASE_IDS) for name, recs in RESULTS.items()}
for name, s in scores.items():
    if s:
        print(f"{name:15} {s['passes']}/{s['n']} acc={s['accuracy']} CI={s['ci']} errors={s['errors']} "
              f"cost=${s['cost_per_task']} p95={s['p95_ms']}ms")
decision = pick_winner(scores, CONSTRAINTS) if all(scores.values()) else None
if decision:
    print("Leader on quality:", decision["leader"])
    print("Tied with the leader (within noise):", decision["tied"])
    print("Winner under the constraints:", decision["winner"])
    for name, reasons in decision["disqualified"].items():
        print(f"  out: {name}: {'; '.join(reasons)}")
