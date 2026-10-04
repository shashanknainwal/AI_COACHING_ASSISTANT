import math

# Eval results for the triage system (given): one row per ticket, with its expected category.
# Baseline = the prompt in production today. Candidate = a new prompt that "scores higher".
_CATEGORIES = {"T-01": "order_status", "T-02": "order_status", "T-03": "returns", "T-04": "returns", "T-05": "damaged_item",
               "T-06": "damaged_item", "T-07": "damaged_item", "T-08": "billing", "T-09": "billing", "T-10": "billing",
               "T-11": "account", "T-12": "account", "T-13": "account", "T-14": "other", "T-15": "other", "T-16": "other",
               "T-17": "damaged_item", "T-18": "order_status", "T-19": "other", "T-20": "billing"}
_BASELINE_FAILS = {"T-07", "T-10", "T-12", "T-13", "T-16", "T-17"}
_CANDIDATE_FAILS = {"T-03", "T-05", "T-07", "T-10", "T-16"}
BASELINE = [{"id": i, "category": c, "pass": i not in _BASELINE_FAILS} for i, c in _CATEGORIES.items()]
CANDIDATE = [{"id": i, "category": c, "pass": i not in _CANDIDATE_FAILS} for i, c in _CATEGORIES.items()]
MUST_PASS = ["T-07", "T-13"]                 # a sparking lamp and a fraud report: never misroute these
CRITICAL_CATEGORIES = ["damaged_item", "account"]

# Five trials of each agent case (given): the same input, run five times.
AGENT_TRIALS = {
    "A-1": [True, True, True, True, True],
    "A-2": [True, False, True, True, True],
    "A-3": [False, False, False, False, False],
    "A-4": [True, True, False, True, False],
    "A-5": [True, True, True, True, True],
}


def wilson_interval(passes, n, z=1.96):
    """95% Wilson score interval for a pass rate, as (low, high) rounded to 3 decimals."""
    # TODO
    pass


def diff_runs(baseline, candidate):
    """{"regressions": [ids that passed before and fail now], "fixes": [ids that failed before and pass now]}."""
    # TODO
    pass


def gate(baseline, candidate, must_pass, critical, tolerance=0.02):
    """{"ship": bool, "reasons": [why not]}."""
    # TODO
    pass


def consistency(trials):
    """{"pass_at_k", "pass_all_k", "flaky"} over repeated trials."""
    # TODO
    pass


# --- Try it out (not graded) ---
for name, rows in [("baseline", BASELINE), ("candidate", CANDIDATE)]:
    passes = sum(r["pass"] for r in rows)
    print(f"{name:<9} {passes}/{len(rows)} pass, 95% interval {wilson_interval(passes, len(rows))}")
print("diff:", diff_runs(BASELINE, CANDIDATE))
print("gate:", gate(BASELINE, CANDIDATE, MUST_PASS, CRITICAL_CATEGORIES))
print("agent consistency over 5 trials:", consistency(AGENT_TRIALS))
