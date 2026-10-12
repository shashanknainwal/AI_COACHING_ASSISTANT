import json

import anthropic


def worker_request(contract_id, text):
    """Request parameters for one worker. Only this contract goes in."""
    # TODO
    pass


def run_worker(client, contract_id, text, budget=WORKER_BUDGET):
    """One worker call. Returns {"contract_id", "status", "report", "error", "usage"}. Never raises."""
    # TODO
    pass


def assess(report):
    """The procurement rules, applied in code. Returns the list of triggered flags."""
    # TODO
    return []


def merge(results):
    """{"flagged": {id: [flags]}, "clean": [...], "failed": [...], "skipped": [...], "coverage": float}"""
    # TODO
    pass


def lead_request(merged):
    """Request parameters for the one lead call. It sees the findings, never the contracts."""
    # TODO
    pass


def cost_usd(model, usage):
    # TODO
    return 0.0


def run_review(client, contracts):
    """Fan out, merge, one lead call. Returns {"merged", "summary", "usage": {"workers", "lead"}, "cost_usd"}."""
    # TODO
    pass


def compare(review, baseline, truth_risky):
    """Cost and recall for the fan-out and the single-agent baseline."""
    # TODO
    pass


# --- Try it out (not graded) ---
review = run_review(client, CONTRACTS)
if review:
    m = review["merged"]
    print("Flagged:", m["flagged"])
    print("Failed:", m["failed"], "Skipped:", m["skipped"], "Coverage:", m["coverage"])
    print(f"Fan-out tokens: {review['usage']}  cost ${review['cost_usd']:.4f}")
    baseline = run_single_agent(client)
    print(json.dumps(compare(review, baseline, TRUTH_RISKY), indent=2))
else:
    print("run_review returned nothing yet.")
