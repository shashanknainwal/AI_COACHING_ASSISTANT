"""Lab 1: prompt iteration on 30 labelled tickets, 3 runs per prompt.

    python -m labs.lab1_prompt_iteration.run --prompt labs/lab1_prompt_iteration/prompt_v1.txt
    python -m labs.lab1_prompt_iteration.run --prompt labs/lab1_prompt_iteration/prompt_v2.txt

Defaults: Claude Haiku 5.5, effort low, 3 runs. About 90 calls per prompt.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from app import config
from app.costs import CostMeter
from app.llm import get_client
from labs.common import accuracy_report, classify, latency_cost_summary, load_jsonl, pct, write_json

HERE = Path(__file__).parent
CATEGORIES = ["order_status", "returns", "damaged_item", "billing", "account", "product_question"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--model", default=config.HAIKU)
    ap.add_argument("--effort", default="low")
    ap.add_argument("--tickets", default=str(HERE / "tickets.jsonl"))
    args = ap.parse_args()

    system = Path(args.prompt).read_text(encoding="utf-8").strip()
    tickets = load_jsonl(args.tickets)
    labels = {t["id"]: t["label"] for t in tickets}
    client, meter = get_client(), CostMeter()
    runs, results = [], []
    for r in range(args.runs):
        preds = {}
        for t in tickets:
            pred, res = classify(client, system=system, text=t["text"], categories=CATEGORIES,
                                 model=args.model, effort=args.effort, meter=meter)
            preds[t["id"]] = pred
            results.append(res)
            if pred is None:
                print(f"run {r + 1} {t['id']}: no prediction ({res.error})")
        runs.append(preds)
        print(f"run {r + 1}: done")

    report = accuracy_report(labels, runs)
    usage = latency_cost_summary(results)
    ambiguous = {t["id"] for t in tickets if t.get("ambiguous")}
    print(f"\nprompt {args.prompt} | model {args.model} | effort {args.effort} | runs {args.runs}")
    for k, pr in enumerate(report["per_run"], start=1):
        lo, hi = pr["wilson_95"]
        print(f"  run {k}: {pr['correct']}/{pr['n']} = {pct(pr['accuracy'])} (95% Wilson {pct(lo)} to {pct(hi)}), missing {pr['missing']}")
    print(f"  spread across runs: {pct(report['min_accuracy'])} to {pct(report['max_accuracy'])}")
    flips = report["flipped_tickets"]
    print(f"  tickets that changed label between runs: {len(flips)} {flips} "
          f"({len([f for f in flips if f in ambiguous])} of them marked ambiguous)")
    print(f"  wrong in every run: {report['always_wrong']}")
    print(f"  top confusions: {report['top_confusions']}")
    print(f"  cost ${usage['total_usd']:.4f} total, ${usage['usd_per_1000_calls']:.2f} per 1,000 tickets; "
          f"p50 {usage['p50_latency_s']}s, p95 {usage['p95_latency_s']}s; "
          f"mean output tokens {usage['mean_output_tokens']} (thinking {usage['mean_thinking_tokens']})")
    out = Path("results") / f"lab1_{Path(args.prompt).stem}.json"
    write_json(out, {"prompt": args.prompt, "model": args.model, "effort": args.effort, "runs": runs,
                     "report": report, "usage": usage, "meter": meter.summary()})
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
