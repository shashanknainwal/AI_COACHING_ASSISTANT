"""Shared helpers for the labs. The pure functions here are unit tested."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from app.costs import CostMeter
from app.llm import CallResult, call
from evals.stats import percentile, wilson_interval

ROOT = Path(__file__).resolve().parent.parent


def load_jsonl(path: str | Path) -> list[dict]:
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]


def category_schema(categories: list[str]) -> dict:
    return {
        "type": "object",
        "properties": {"category": {"type": "string", "enum": categories}},
        "required": ["category"],
        "additionalProperties": False,
    }


def classify(client, *, system: str, text: str, categories: list[str], model: str, effort: str,
             meter: CostMeter | None = None) -> tuple[str | None, CallResult]:
    """One structured-output classification. Returns (category or None, CallResult)."""
    res = call(client, system=system, user=f"<ticket>\n{text}\n</ticket>", model=model, effort=effort,
               max_tokens=2048, schema=category_schema(categories), meter=meter)
    if res.ok and isinstance(res.parsed, dict):
        return res.parsed.get("category"), res
    return None, res


def accuracy_report(labels: dict[str, str], runs: list[dict[str, str | None]]) -> dict:
    """Pure: per-run accuracy with Wilson intervals, run-to-run spread and flips.

    `runs` is a list of {ticket_id: predicted label or None}. None means the
    call errored or refused; it counts as neither right nor wrong here and is
    reported in `missing`.
    """
    per_run = []
    for run in runs:
        scored = {i: p for i, p in run.items() if p is not None and i in labels}
        correct = sum(p == labels[i] for i, p in scored.items())
        lo, hi = wilson_interval(correct, len(scored)) if scored else (0.0, 1.0)
        per_run.append({"correct": correct, "n": len(scored), "accuracy": correct / len(scored) if scored else 0.0,
                        "wilson_95": [round(lo, 4), round(hi, 4)], "missing": sum(p is None for p in run.values())})
    ids = sorted(labels)
    flips = [i for i in ids if len({run.get(i) for run in runs if run.get(i) is not None}) > 1]
    always_wrong = [i for i in ids if all(run.get(i) is not None and run.get(i) != labels[i] for run in runs)]
    mistakes = Counter((labels[i], p) for run in runs for i, p in run.items()
                       if p is not None and i in labels and p != labels[i])
    accs = [r["accuracy"] for r in per_run]
    return {
        "per_run": per_run,
        "mean_accuracy": sum(accs) / len(accs) if accs else 0.0,
        "min_accuracy": min(accs) if accs else 0.0,
        "max_accuracy": max(accs) if accs else 0.0,
        "flipped_tickets": flips,
        "always_wrong": always_wrong,
        "top_confusions": [{"label": a, "predicted": b, "count": n} for (a, b), n in mistakes.most_common(5)],
    }


def latency_cost_summary(results: list[CallResult]) -> dict:
    """Pure: totals and per-call figures from a list of CallResults."""
    if not results:
        return {"calls": 0}
    lat = [r.latency_s for r in results if r.error is None or r.refused]
    total = sum(r.cost_usd for r in results)
    out_tokens = [r.usage.get("output_tokens", 0) for r in results if r.usage]
    thinking = [r.usage.get("thinking_tokens", 0) for r in results if r.usage]
    cache_read = sum(r.usage.get("cache_read_input_tokens", 0) for r in results if r.usage)
    return {
        "calls": len(results),
        "total_usd": round(total, 6),
        "usd_per_call": round(total / len(results), 6),
        "usd_per_1000_calls": round(1000 * total / len(results), 4),
        "p50_latency_s": round(percentile(lat, 50), 2) if lat else None,
        "p95_latency_s": round(percentile(lat, 95), 2) if lat else None,
        "mean_output_tokens": round(sum(out_tokens) / len(out_tokens), 1) if out_tokens else 0,
        "mean_thinking_tokens": round(sum(thinking) / len(thinking), 1) if thinking else 0,
        "cache_read_tokens_total": cache_read,
        "errors": sum(1 for r in results if r.error and not r.refused),
        "refusals": sum(1 for r in results if r.refused),
    }


def write_json(path: str | Path, data: dict) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")


def pct(x: float) -> str:
    return f"{100 * x:.1f}%"
