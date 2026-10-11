"""CI gate: compare a results file with the baseline and exit non-zero on regression.

    python -m evals.gate --current results/latest.json
    python -m evals.gate --current results/latest.json --update-baseline   # after a reviewed change

Policy lives in evals/gate_policy.json. Two modes for the pass-rate check:
- "point": fail if the pass rate dropped by more than max_drop. Simple, but
  with a small golden set it also fails on noise. Run more trials to shrink it.
- "interval": fail only if the whole 95% Wilson interval of the current run
  sits below the baseline pass rate. Fewer false alarms, misses small drops.
Either way, say which one you chose and why in your decision record.

`evaluate_gate` is a pure function and is unit tested.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def evaluate_gate(current: dict, baseline: dict, policy: dict) -> tuple[bool, list[str], list[str]]:
    """Return (ok, failures, notes). Never raises on missing optional fields."""
    failures: list[str] = []
    notes: list[str] = []
    rate = current.get("pass_rate")
    if rate is None:
        return False, ["no pass rate in the results file (did every trial error?)"], notes

    summary = current.get("summary") or {}
    lo, hi = (summary.get("wilson_95") or [None, None])
    if lo is not None:
        notes.append(f"pass rate {rate:.1%} (95% Wilson {lo:.1%} to {hi:.1%}) over {summary.get('trials')} trials")

    min_rate = policy.get("min_pass_rate")
    if min_rate is not None and rate < min_rate:
        failures.append(f"pass rate {rate:.1%} is below the floor of {min_rate:.0%}")

    base = baseline.get("pass_rate")
    if base is None:
        notes.append("no baseline yet: only absolute thresholds were checked")
    else:
        mode = policy.get("mode", "point")
        if mode == "interval":
            if hi is not None and hi < base:
                failures.append(f"regression: the whole interval ({lo:.1%} to {hi:.1%}) is below the baseline {base:.1%}")
            elif rate < base:
                notes.append(f"pass rate {rate:.1%} is under the baseline {base:.1%} but within noise (interval mode)")
        else:
            max_drop = policy.get("max_drop", 0.05)
            if rate < base - max_drop:
                failures.append(f"regression: pass rate {rate:.1%} fell more than {max_drop:.0%} below the baseline {base:.1%}")

    if policy.get("critical_must_pass_every_run", True) and current.get("critical_failures"):
        failures.append(f"critical cases failed: {', '.join(current['critical_failures'])}")

    max_err = policy.get("max_error_rate")
    if max_err is not None and current.get("error_rate", 0.0) > max_err:
        failures.append(f"error rate {current['error_rate']:.1%} is above {max_err:.0%}")

    max_cost = policy.get("max_cost_per_case_usd")
    per_case = (current.get("cost") or {}).get("agent_per_case_usd")
    if max_cost is not None and per_case is not None and per_case > max_cost:
        failures.append(f"cost per case ${per_case:.4f} is above ${max_cost:.4f}")

    max_p95 = policy.get("max_p95_latency_s")
    p95 = (current.get("latency_s") or {}).get("p95")
    if max_p95 is not None and p95 is not None and p95 > max_p95:
        failures.append(f"p95 latency {p95:.1f}s is above {max_p95:.1f}s")

    return not failures, failures, notes


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--current", default="results/latest.json")
    ap.add_argument("--baseline", default="evals/baseline.json")
    ap.add_argument("--policy", default="evals/gate_policy.json")
    ap.add_argument("--update-baseline", action="store_true")
    args = ap.parse_args(argv)

    current = json.loads(Path(args.current).read_text(encoding="utf-8"))
    if args.update_baseline:
        keep = {k: current.get(k) for k in ("timestamp", "model", "effort", "judge_model", "pass_rate",
                                            "summary", "error_rate", "cost", "latency_s")}
        Path(args.baseline).write_text(json.dumps(keep, indent=2), encoding="utf-8")
        print(f"baseline updated from {args.current}: pass rate {current.get('pass_rate')}")
        return 0

    baseline = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    policy = json.loads(Path(args.policy).read_text(encoding="utf-8"))
    ok, failures, notes = evaluate_gate(current, baseline, policy)
    for n in notes:
        print(f"note: {n}")
    for f in failures:
        print(f"FAIL: {f}")
    print("gate: PASS" if ok else "gate: FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
