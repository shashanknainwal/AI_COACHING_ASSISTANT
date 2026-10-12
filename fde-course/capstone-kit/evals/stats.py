"""Small, dependency-free statistics for evals. Every function here is unit tested.

- wilson_interval: an honest range for a pass rate from a small sample
- cohen_kappa: agreement between two labellers (judge vs human) beyond chance
- summarize_runs: pass rate over N repeated runs, run-to-run spread, flaky cases
- percentile: p50 / p95 latency
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Hashable, Sequence


def wilson_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion (95% by default).

    Better than "p plus or minus 1.96 * sqrt(p(1-p)/n)" for small n and for
    rates near 0 or 1: it never goes below 0 or above 1, and 0/20 still gets
    a non-zero upper bound. Returns (0.0, 1.0) when n == 0.
    """
    if n < 0 or successes < 0 or successes > n:
        raise ValueError("need 0 <= successes <= n")
    if n == 0:
        return (0.0, 1.0)
    p = successes / n
    z2 = z * z
    denom = 1 + z2 / n
    centre = (p + z2 / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def cohen_kappa(a: Sequence[Hashable], b: Sequence[Hashable]) -> float:
    """Cohen's kappa for two raters over the same items.

    1.0 is perfect agreement, 0.0 is what chance alone would give, negative is
    worse than chance. When both raters use a single label for everything,
    chance agreement is 1 and kappa is undefined; this returns 1.0 if they
    agree on every item and 0.0 otherwise.
    """
    if len(a) != len(b):
        raise ValueError("raters must label the same number of items")
    n = len(a)
    if n == 0:
        raise ValueError("no items")
    observed = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    expected = sum((ca[label] / n) * (cb[label] / n) for label in set(ca) | set(cb))
    if expected >= 1.0:
        return 1.0 if observed == 1.0 else 0.0
    return (observed - expected) / (1 - expected)


def confusion(a: Sequence[Hashable], b: Sequence[Hashable]) -> dict[tuple, int]:
    """Counts of (label_from_a, label_from_b) pairs."""
    return dict(Counter(zip(a, b)))


def percentile(values: Sequence[float], p: float) -> float:
    """Linear-interpolated percentile, p in [0, 100]. Raises on empty input."""
    if not values:
        raise ValueError("no values")
    if not 0 <= p <= 100:
        raise ValueError("p must be in [0, 100]")
    xs = sorted(values)
    if len(xs) == 1:
        return float(xs[0])
    rank = (len(xs) - 1) * p / 100
    lo, hi = math.floor(rank), math.ceil(rank)
    return float(xs[lo] + (xs[hi] - xs[lo]) * (rank - lo))


def summarize_runs(runs: Sequence[dict[str, bool]]) -> dict:
    """Summarise N runs of the same eval. Each run maps case_id -> passed.

    Cases missing from a run (errors, timeouts) are not counted as passes or
    failures here; report errors separately so a flaky network doesn't look
    like a worse prompt.
    """
    if not runs:
        raise ValueError("no runs")
    per_run = []
    for run in runs:
        n = len(run)
        per_run.append({"passed": sum(run.values()), "n": n, "rate": (sum(run.values()) / n) if n else 0.0})
    total_pass = sum(r["passed"] for r in per_run)
    total_n = sum(r["n"] for r in per_run)
    lo, hi = wilson_interval(total_pass, total_n)
    case_ids = sorted(set().union(*[set(r) for r in runs]))
    flaky = [c for c in case_ids if len({run[c] for run in runs if c in run}) > 1]
    all_runs = [c for c in case_ids if all(run.get(c) is True for run in runs)]
    rates = [r["rate"] for r in per_run]
    return {
        "runs": len(runs),
        "per_run": per_run,
        "pass_rate": total_pass / total_n if total_n else 0.0,
        "wilson_95": [lo, hi],
        "trials": total_n,
        "min_run_rate": min(rates),
        "max_run_rate": max(rates),
        "flaky_cases": flaky,
        "pass_all_runs": len(all_runs),       # pass^k: passed in every run
        "cases": len(case_ids),
    }
