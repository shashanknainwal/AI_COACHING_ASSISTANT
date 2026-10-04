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
    if n == 0:
        return (0.0, 1.0)
    p = passes / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (round(center - half, 3), round(center + half, 3))


def diff_runs(baseline, candidate):
    before = {r["id"]: r["pass"] for r in baseline}
    regressions = [r["id"] for r in candidate if r["id"] in before and before[r["id"]] and not r["pass"]]
    fixes = [r["id"] for r in candidate if r["id"] in before and not before[r["id"]] and r["pass"]]
    return {"regressions": regressions, "fixes": fixes}


def _pass_rate(rows):
    return sum(r["pass"] for r in rows) / len(rows)


def gate(baseline, candidate, must_pass, critical, tolerance=0.02):
    reasons = []
    passed = {r["id"]: r["pass"] for r in candidate}
    for case_id in must_pass:
        if not passed.get(case_id, False):
            reasons.append(f"must-pass case {case_id} failed")
    before, after = _pass_rate(baseline), _pass_rate(candidate)
    if after < before - tolerance:
        reasons.append(f"pass rate dropped from {before:.3f} to {after:.3f}")
    categories = {r["id"]: r["category"] for r in candidate}
    for case_id in diff_runs(baseline, candidate)["regressions"]:
        if categories[case_id] in critical:
            reasons.append(f"regression in critical category {categories[case_id]}: {case_id}")
    return {"ship": not reasons, "reasons": reasons}


def consistency(trials):
    n = len(trials)
    any_pass = sum(any(t) for t in trials.values())
    all_pass = sum(all(t) for t in trials.values())
    flaky = [case_id for case_id, t in trials.items() if any(t) and not all(t)]
    return {"pass_at_k": round(any_pass / n, 3), "pass_all_k": round(all_pass / n, 3), "flaky": flaky}


# --- Try it out (not graded) ---
for name, rows in [("baseline", BASELINE), ("candidate", CANDIDATE)]:
    passes = sum(r["pass"] for r in rows)
    print(f"{name:<9} {passes}/{len(rows)} pass, 95% interval {wilson_interval(passes, len(rows))}")
print("diff:", diff_runs(BASELINE, CANDIDATE))
print("gate:", gate(BASELINE, CANDIDATE, MUST_PASS, CRITICAL_CATEGORIES))
print("agent consistency over 5 trials:", consistency(AGENT_TRIALS))
