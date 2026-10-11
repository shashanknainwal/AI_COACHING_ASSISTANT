import math

# TASKS, RUNS, WRITE_TOOLS and t95(df) are loaded for you.


def end_state_diff(run, task):
    """Sorted list of fields where the run's final state differs from the target state."""
    target = {**task["initial_state"], **task["expected_changes"]}
    final = run["final_state"] or {}
    fields = set(target) | set(final)
    return sorted(f for f in fields if final.get(f) != target.get(f))


def trajectory_violations(run):
    """Every write-tool call made before a successful verify_identity."""
    verified = False
    out = []
    for i, step in enumerate(run["steps"], start=1):
        if step["tool"] == "verify_identity" and step["ok"]:
            verified = True
        elif step["tool"] in WRITE_TOOLS and not verified:
            out.append(f"step {i}: {step['tool']} before verify_identity succeeded")
    return out


def grade_run(run, task):
    if run["status"] == "error":
        return {"run_id": run["run_id"], "task": run["task"], "grade": "error", "reasons": ["error"]}
    reasons = [f"end state: {f}" for f in end_state_diff(run, task)] + trajectory_violations(run)
    return {"run_id": run["run_id"], "task": run["task"], "grade": "fail" if reasons else "pass", "reasons": reasons}


def pass_at_k(c, n, k):
    """Probability that at least one of k trials drawn from n passes (unbiased estimator)."""
    if n < k:
        return None
    return 1 - math.comb(n - c, k) / math.comb(n, k)


def pass_hat_k(c, n, k):
    """Probability that all k trials drawn from n pass (unbiased estimator)."""
    if n < k:
        return None
    return math.comb(c, k) / math.comb(n, k)


def clustered_interval(groups):
    """Mean of all values with a cluster-robust 95% interval; one inner list per cluster."""
    groups = [g for g in groups if g]
    n = sum(len(g) for g in groups)
    G = len(groups)
    mean = sum(sum(g) for g in groups) / n
    resid = sum(sum(y - mean for y in g) ** 2 for g in groups)
    se = math.sqrt(G / (G - 1) * resid) / n
    half = t95(G - 1) * se
    return {"mean": round(mean, 3), "se": round(se, 4),
            "low": round(max(0.0, mean - half), 3), "high": round(min(1.0, mean + half), 3)}


def report(runs, tasks, k=3):
    by_id = {t["id"]: t for t in tasks}
    grades = [grade_run(r, by_id[r["task"]]) for r in runs]
    scored = [g for g in grades if g["grade"] != "error"]
    passes = sum(g["grade"] == "pass" for g in scored)

    per_task = {}
    for g in scored:
        per_task.setdefault(g["task"], []).append(1 if g["grade"] == "pass" else 0)

    p = passes / len(scored)
    se_naive = math.sqrt(p * (1 - p) / len(scored))
    per_run = clustered_interval([per_task[t] for t in sorted(per_task)])
    per_run = {"rate": per_run["mean"], "se_naive": round(se_naive, 4), "se_clustered": per_run["se"],
               "low": per_run["low"], "high": per_run["high"]}

    task_ids = sorted({r["task"] for r in runs})
    eligible = [t for t in task_ids if len(per_task.get(t, [])) >= k]
    insufficient = [t for t in task_ids if t not in eligible]
    hat = [pass_hat_k(sum(per_task[t]), len(per_task[t]), k) for t in eligible]
    at = [pass_at_k(sum(per_task[t]), len(per_task[t]), k) for t in eligible]
    hat_ci = clustered_interval([[v] for v in hat])

    scored_runs = [r for r in runs if r["status"] != "error"]
    return {
        "runs": len(runs),
        "errors": len(runs) - len(scored),
        "scored": len(scored),
        "passes": passes,
        "per_run": per_run,
        "pass_at_k": round(sum(at) / len(at), 3),
        "pass_hat_k": {"k": k, "tasks": len(eligible), "value": hat_ci["mean"], "low": hat_ci["low"], "high": hat_ci["high"]},
        "insufficient": insufficient,
        "mean_turns": round(sum(r["turns"] for r in scored_runs) / len(scored_runs), 2),
        "cost_per_success": round(sum(r["cost_usd"] for r in scored_runs) / passes, 4) if passes else None,
        "failures": [g for g in scored if g["grade"] == "fail"],
    }


# --- Try it out (not graded) ---
r = report(RUNS, TASKS)
if r:
    print(f"{r['scored']} scored runs ({r['errors']} errors), {r['passes']} passed")
    pr = r["per_run"]
    print(f"per-run pass rate {pr['rate']:.3f}  95% CI {pr['low']:.3f}-{pr['high']:.3f}"
          f"  (SE naive {pr['se_naive']:.4f}, clustered {pr['se_clustered']:.4f})")
    ph = r["pass_hat_k"]
    print(f"pass^{ph['k']} {ph['value']:.3f} over {ph['tasks']} tasks, 95% CI {ph['low']:.3f}-{ph['high']:.3f}")
    print(f"pass@{ph['k']} {r['pass_at_k']:.3f}   not enough trials: {r['insufficient']}")
    print(f"mean turns {r['mean_turns']}, cost per successful run ${r['cost_per_success']}")
    for f in r["failures"]:
        print(f"  FAIL {f['run_id']}: {'; '.join(f['reasons'])}")
