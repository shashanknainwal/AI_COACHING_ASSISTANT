import math

# TASKS, RUNS, WRITE_TOOLS and t95(df) are loaded for you.


def end_state_diff(run, task):
    """Sorted list of fields where the run's final state differs from the target state."""
    # TODO: target = initial_state updated with expected_changes. Compare every field
    # that appears in either the target or the final state.
    pass


def trajectory_violations(run):
    """Every write-tool call made before a successful verify_identity."""
    # TODO: walk the steps in order (numbered from 1).
    pass


def grade_run(run, task):
    """{"run_id", "task", "grade": "pass" | "fail" | "error", "reasons": [...]}"""
    # TODO
    pass


def pass_at_k(c, n, k):
    """Chance that at least one of k trials passes, from c passes in n trials."""
    # TODO: math.comb
    pass


def pass_hat_k(c, n, k):
    """Chance that all k trials pass, from c passes in n trials."""
    # TODO
    pass


def clustered_interval(groups):
    """Mean of all values with a cluster-robust 95% interval; one inner list per cluster."""
    # TODO
    pass


def report(runs, tasks, k=3):
    # TODO: see the spec for every key.
    pass


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
