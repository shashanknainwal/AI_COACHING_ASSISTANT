import json

import anthropic


def worker_request(contract_id, text):
    """Request parameters for one worker. Only this contract goes in."""
    return {
        "model": WORKER_MODEL,
        "max_tokens": 2000,
        "system": WORKER_SYSTEM,
        "output_config": {"effort": "low", "format": {"type": "json_schema", "schema": REPORT_SCHEMA}},
        "messages": [{"role": "user", "content": f"<contract id=\"{contract_id}\">\n{text}\n</contract>"}],
    }


def run_worker(client, contract_id, text, budget=WORKER_BUDGET):
    params = worker_request(contract_id, text)
    out = {"contract_id": contract_id, "status": "failed", "report": None, "error": None,
           "usage": {"input_tokens": 0, "output_tokens": 0}}
    counted = client.messages.count_tokens(model=params["model"], system=params["system"], messages=params["messages"])
    if counted.input_tokens > budget:
        out.update(status="skipped", error="over_budget")
        return out
    try:
        r = client.messages.create(**params)
    except anthropic.APIError as e:
        out["error"] = type(e).__name__
        return out
    out["usage"] = {"input_tokens": r.usage.input_tokens, "output_tokens": r.usage.output_tokens}
    if r.stop_reason in ("refusal", "max_tokens"):
        out["error"] = "refused" if r.stop_reason == "refusal" else "max_tokens"
        return out
    try:
        report = json.loads("".join(b.text for b in r.content if b.type == "text"))
    except ValueError:
        report = None
    if not isinstance(report, dict) or report.get("contract_id") != contract_id:
        out["error"] = "bad_report"
        return out
    out.update(status="ok", report=report)
    return out


def assess(report):
    """The procurement rules, applied in code. Returns the list of triggered flags."""
    flags = []
    cap, notice = report.get("liability_cap_eur"), report.get("termination_notice_days")
    fuel = report.get("fuel_surcharge_cap_pct")
    if cap is not None and cap < 50000:
        flags.append("low_liability_cap")
    if notice is not None and notice > 90:
        flags.append("long_notice")
    if report.get("auto_renew") and notice is not None and notice > 60:
        flags.append("auto_renew_trap")
    if fuel is not None and fuel > 15:
        flags.append("high_fuel_cap")
    return flags


def merge(results):
    merged = {"flagged": {}, "clean": [], "failed": [], "skipped": [], "coverage": 0.0}
    for r in results:
        if r["status"] == "ok":
            flags = assess(r["report"])
            if flags:
                merged["flagged"][r["contract_id"]] = flags
            else:
                merged["clean"].append(r["contract_id"])
        else:
            merged[r["status"]].append(r["contract_id"])
    ok = len(merged["flagged"]) + len(merged["clean"])
    merged["coverage"] = round(ok / len(results), 3) if results else 0.0
    return merged


def lead_request(merged):
    return {
        "model": LEAD_MODEL,
        "max_tokens": 4000,
        "system": LEAD_SYSTEM,
        "output_config": {"effort": "medium"},
        "messages": [{"role": "user", "content": "<findings>\n" + json.dumps(merged) + "\n</findings>\n"
                      "Write the briefing for the procurement lead."}],
    }


def cost_usd(model, usage):
    p = PRICES[model]
    return (usage["input_tokens"] * p["input"] + usage["output_tokens"] * p["output"]) / 1_000_000


def run_review(client, contracts):
    results = [run_worker(client, cid, text) for cid, text in contracts.items()]
    merged = merge(results)
    workers = {"input_tokens": sum(r["usage"]["input_tokens"] for r in results),
               "output_tokens": sum(r["usage"]["output_tokens"] for r in results)}
    r = client.messages.create(**lead_request(merged))
    lead = {"input_tokens": r.usage.input_tokens, "output_tokens": r.usage.output_tokens}
    return {
        "merged": merged,
        "summary": "".join(b.text for b in r.content if b.type == "text"),
        "usage": {"workers": workers, "lead": lead},
        "cost_usd": cost_usd(WORKER_MODEL, workers) + cost_usd(LEAD_MODEL, lead),
    }


def compare(review, baseline, truth_risky):
    flagged_fan = set(review["merged"]["flagged"])
    flagged_base = {r["contract_id"] for r in baseline["reports"] if assess(r)}
    seen_base = {r["contract_id"] for r in baseline["reports"]}
    all_ids = set(CONTRACTS)
    return {
        "fanout": {"cost_usd": review["cost_usd"],
                   "recall": len(flagged_fan & set(truth_risky)) / len(truth_risky),
                   "unreviewed_reported": sorted(review["merged"]["failed"] + review["merged"]["skipped"])},
        "baseline": {"cost_usd": cost_usd(LEAD_MODEL, baseline["usage"]),
                     "recall": len(flagged_base & set(truth_risky)) / len(truth_risky),
                     "unreviewed_reported": [],
                     "silently_missing": sorted(all_ids - seen_base)},
    }


# --- Try it out (not graded) ---
review = run_review(client, CONTRACTS)
m = review["merged"]
print("Flagged:", m["flagged"])
print("Failed:", m["failed"], "Skipped:", m["skipped"], "Coverage:", m["coverage"])
print(f"Fan-out tokens: {review['usage']}  cost ${review['cost_usd']:.4f}")
baseline = run_single_agent(client)
print(json.dumps(compare(review, baseline, TRUTH_RISKY), indent=2))
