"""Calibrate the LLM judge against human labels with Cohen's kappa.

    python -m evals.calibrate_judge --items labs/lab3_judge_calibration/answers.jsonl \
        --labels labs/lab3_judge_calibration/my_labels.csv --runs 3

Items: JSONL rows with id, question, reference, answer.
Labels: CSV with columns id,verdict (pass/fail), or JSONL rows with id and verdict.
Label the items yourself BEFORE you run the judge, or you will anchor on it.

The report shows, for each judge run and for the majority vote across runs:
agreement, kappa against your labels, and the confusion counts; plus how often
the judge agreed with itself across runs, and every disagreement with the
judge's rationale so you can decide who was wrong (sometimes it is the label).
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from app import config
from app.costs import CostMeter
from evals.judge import judge, load_rubric
from evals.stats import cohen_kappa, confusion


def load_labels(path: str | Path) -> dict[str, str]:
    p = Path(path)
    labels: dict[str, str] = {}
    if p.suffix == ".csv":
        with p.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                v = (row.get("verdict") or "").strip().lower()
                if v:
                    labels[row["id"].strip()] = v
    else:
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                labels[row["id"]] = row["verdict"].strip().lower()
    bad = {k: v for k, v in labels.items() if v not in ("pass", "fail")}
    if bad:
        raise SystemExit(f"labels must be pass or fail: {bad}")
    return labels


def majority(votes: list[str]) -> str:
    """Majority verdict; ties go to 'fail' (the conservative call for a gate)."""
    c = Counter(votes)
    return "pass" if c["pass"] > c["fail"] else "fail"


def calibration_report(ids: list[str], human: dict[str, str], judge_runs: list[dict[str, str]]) -> dict:
    """Pure function: compare judge verdicts (one dict per run) with human labels.

    Items the judge failed to grade in a run are missing from that run's dict
    and are skipped for that run only.
    """
    per_run = []
    for run in judge_runs:
        common = [i for i in ids if i in run and i in human]
        h = [human[i] for i in common]
        j = [run[i] for i in common]
        per_run.append({"n": len(common),
                        "agreement": sum(a == b for a, b in zip(h, j)) / len(common) if common else 0.0,
                        "kappa": cohen_kappa(h, j) if common else None,
                        "confusion_human_vs_judge": {f"{a}/{b}": n for (a, b), n in confusion(h, j).items()}})
    graded_every_run = [i for i in ids if i in human and all(i in run for run in judge_runs)]
    maj = {i: majority([run[i] for run in judge_runs]) for i in graded_every_run}
    h = [human[i] for i in graded_every_run]
    m = [maj[i] for i in graded_every_run]
    self_agree = [i for i in graded_every_run if len({run[i] for run in judge_runs}) == 1]
    return {
        "items": len(ids),
        "per_run": per_run,
        "majority": {"n": len(graded_every_run),
                     "agreement": sum(a == b for a, b in zip(h, m)) / len(h) if h else 0.0,
                     "kappa": cohen_kappa(h, m) if h else None},
        "judge_self_agreement": len(self_agree) / len(graded_every_run) if graded_every_run else 0.0,
        "unstable_items": [i for i in graded_every_run if i not in self_agree],
        "disagreements": [i for i in graded_every_run if maj[i] != human[i]],
        "human_pass_rate": (sum(v == "pass" for v in h) / len(h)) if h else None,
        "judge_pass_rate": (sum(v == "pass" for v in m) / len(m)) if m else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", default="labs/lab3_judge_calibration/answers.jsonl")
    ap.add_argument("--labels", default="labs/lab3_judge_calibration/my_labels.csv")
    ap.add_argument("--rubric", default=None)
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--model", default=config.JUDGE_MODEL)
    ap.add_argument("--effort", default="low")
    ap.add_argument("--out", default="results/judge_calibration.json")
    args = ap.parse_args()

    from app.llm import get_client

    items = [json.loads(l) for l in Path(args.items).read_text(encoding="utf-8").splitlines() if l.strip()]
    human = load_labels(args.labels)
    missing = [it["id"] for it in items if it["id"] not in human]
    if missing:
        raise SystemExit(f"label every item first; missing: {', '.join(missing)}")
    client, meter, rubric = get_client(), CostMeter(), load_rubric(args.rubric)
    runs: list[dict[str, str]] = []
    rationales: dict[str, list[str]] = {}
    for r in range(args.runs):
        run: dict[str, str] = {}
        for it in items:
            verdict, res = judge(client, question=it["question"], reference=it["reference"], answer=it["answer"],
                                 rubric=rubric, model=args.model, effort=args.effort, meter=meter)
            if verdict is None:
                print(f"run {r + 1} {it['id']}: judge error ({res.error})")
                continue
            run[it["id"]] = verdict["verdict"]
            rationales.setdefault(it["id"], []).append(f"run {r + 1} {verdict['verdict']}: {verdict['rationale']}")
        runs.append(run)

    ids = [it["id"] for it in items]
    report = calibration_report(ids, human, runs)
    report.update({"model": args.model, "effort": args.effort, "runs": args.runs,
                   "cost_usd": round(meter.total_usd, 6), "usage": meter.summary(),
                   "disagreement_rationales": {i: rationales.get(i, []) for i in report["disagreements"]}})
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(report, indent=2), encoding="utf-8")

    for k, pr in enumerate(report["per_run"], start=1):
        print(f"run {k}: n={pr['n']} agreement {pr['agreement']:.0%} kappa {pr['kappa']:.2f} {pr['confusion_human_vs_judge']}")
    mj = report["majority"]
    print(f"majority of {args.runs}: agreement {mj['agreement']:.0%} kappa {mj['kappa']:.2f}; "
          f"judge agreed with itself on {report['judge_self_agreement']:.0%} of items")
    print(f"disagreements: {report['disagreements'] or 'none'}; spend ${meter.total_usd:.4f}; wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
