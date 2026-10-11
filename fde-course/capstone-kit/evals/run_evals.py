"""Run the golden set N times against the real model and write a results file.

    python -m evals.run_evals --runs 3 --out results/latest.json
    python -m evals.run_evals --runs 1 --no-judge --limit 4     # cheap smoke test

Each case passes only if every check passes: required tool calls, required
phrases (any of the alternatives), forbidden phrases, and the LLM judge.
Errors (network, max_tokens, judge failure) are counted separately and left
out of the pass rate, so a flaky network doesn't look like a worse prompt.
Refusals count as failures and are also reported on their own.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from app import config
from app.agent import run_agent
from app.costs import CostMeter
from app.tools import LocalTools
from evals.judge import judge, load_rubric
from evals.stats import percentile, summarize_runs, wilson_interval


def load_jsonl(path: str | Path) -> list[dict]:
    rows = []
    for i, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), start=1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{i}: bad JSON: {exc}")
    return rows


def deterministic_checks(case: dict, answer: str, tool_names: list[str]) -> list[str]:
    """Return the names of the checks that failed (empty list = all passed). Pure function."""
    checks = case.get("checks", {})
    failed = []
    low = answer.lower()
    for name in checks.get("must_call", []):
        if name not in tool_names:
            failed.append(f"must_call:{name}")
    for alternatives in checks.get("must_include_any", []):
        if not any(alt.lower() in low for alt in alternatives):
            failed.append(f"must_include_any:{alternatives[0]}")
    for phrase in checks.get("must_not_include", []):
        if phrase.lower() in low:
            failed.append(f"must_not_include:{phrase}")
    return failed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--golden", default="evals/golden.jsonl")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--model", default=config.DEFAULT_MODEL)
    ap.add_argument("--effort", default=config.DEFAULT_EFFORT)
    ap.add_argument("--judge-model", default=config.JUDGE_MODEL)
    ap.add_argument("--rubric", default=None, help="path to a rubric text file (default: evals/judge.py)")
    ap.add_argument("--no-judge", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="only the first N cases")
    ap.add_argument("--out", default="results/latest.json")
    args = ap.parse_args()

    from app.llm import get_client

    client = get_client()
    cases = load_jsonl(args.golden)
    if args.limit:
        cases = cases[: args.limit]
    rubric = load_rubric(args.rubric)
    meter = CostMeter()
    runs: list[dict[str, bool]] = []
    trials, latencies, errors, refusals = [], [], 0, 0
    critical_failures = set()
    agent_cost = 0.0

    for r in range(args.runs):
        run: dict[str, bool] = {}
        for case in cases:
            res = run_agent(case["input"], client=client, tools=LocalTools(), model=args.model,
                            effort=args.effort, meter=meter)
            agent_cost += res.cost_usd
            trial = {"run": r + 1, "id": case["id"], "status": res.status, "answer": res.text,
                     "tools": [t["name"] for t in res.tool_calls], "cost_usd": round(res.cost_usd, 6),
                     "latency_s": round(res.latency_s, 2), "usage": res.usage, "request_ids": res.request_ids}
            if res.status in ("error", "truncated", "max_turns", "context_exceeded"):
                errors += 1
                trial["error"] = res.error
                trials.append(trial)
                continue
            latencies.append(res.latency_s)
            if res.status == "refused":
                refusals += 1
                failed = ["refused"]
            else:
                failed = deterministic_checks(case, res.text, trial["tools"])
                if not args.no_judge and case.get("checks", {}).get("judge", False):
                    verdict, jres = judge(client, question=case["input"], reference=case["reference"],
                                          answer=res.text, rubric=rubric, model=args.judge_model, meter=meter)
                    if verdict is None:
                        errors += 1
                        trial["error"] = f"judge: {jres.error}"
                        trials.append(trial)
                        continue
                    trial["judge"] = verdict
                    if verdict["verdict"] != "pass":
                        failed.append("judge:" + ",".join(verdict.get("failed_lines", [])))
            trial["failed"] = failed
            trial["passed"] = not failed
            run[case["id"]] = not failed
            if failed and case.get("critical"):
                critical_failures.add(case["id"])
            trials.append(trial)
            print(f"run {r + 1} {case['id']}: {'PASS' if not failed else 'FAIL ' + '; '.join(failed)}", flush=True)
        runs.append(run)

    summary = summarize_runs(runs) if any(runs) else None
    total_trials = len(trials)
    scored = sum(len(run) for run in runs)
    out = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model": args.model, "effort": args.effort,
        "judge_model": None if args.no_judge else args.judge_model,
        "golden": args.golden, "cases": len(cases), "runs": args.runs,
        "summary": summary,
        "pass_rate": summary["pass_rate"] if summary else None,
        "errors": errors, "error_rate": errors / total_trials if total_trials else 0.0,
        "refusals": refusals, "refusal_wilson_95": list(wilson_interval(refusals, scored)) if scored else None,
        "critical_failures": sorted(critical_failures),
        "cost": {"total_usd": round(meter.total_usd, 6), "agent_usd": round(agent_cost, 6),
                 "agent_per_case_usd": round(agent_cost / total_trials, 6) if total_trials else 0.0,
                 "usage": meter.summary()},
        "latency_s": {"p50": round(percentile(latencies, 50), 2), "p95": round(percentile(latencies, 95), 2)}
        if latencies else None,
        "trials": trials,
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2), encoding="utf-8")
    if summary:
        lo, hi = summary["wilson_95"]
        print(f"\npass rate {summary['pass_rate']:.1%} over {summary['trials']} trials "
              f"(95% Wilson {lo:.1%} to {hi:.1%}); runs ranged {summary['min_run_rate']:.1%} to "
              f"{summary['max_run_rate']:.1%}; flaky cases: {summary['flaky_cases'] or 'none'}")
    print(f"errors {errors}, refusals {refusals}, total spend ${meter.total_usd:.4f}; wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
