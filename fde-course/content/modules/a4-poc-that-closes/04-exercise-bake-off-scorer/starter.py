import math

# EVAL_CASE_IDS, RESULTS, PRICING and CONSTRAINTS (Ellery Bank bake-off) are loaded for you.
# print(RESULTS["opus-rubric"][0]) or print(CONSTRAINTS) to look at them.


def check_same_cases(case_ids, results):
    """Coverage problems per candidate: missing, unknown and duplicate case ids. Clean candidates are left out."""
    # TODO
    pass


def percentile(values, p):
    """Nearest-rank percentile: the ceil(p/100 * n)-th smallest value. None for an empty list."""
    # TODO
    pass


def wilson_interval(passes, n, z=1.96):
    """95% Wilson score interval, as (low, high) rounded to 3 decimals. (0.0, 1.0) when n is 0."""
    # TODO
    pass


def score_candidate(records, pricing, case_ids):
    """Quality with an interval, error rate, cost per task and p95 latency for one candidate."""
    # TODO
    pass


def pick_winner(scores, constraints):
    """Filter on hard constraints, find the quality leader, treat overlapping intervals as tied, pick the cheapest tied."""
    # TODO
    pass


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
