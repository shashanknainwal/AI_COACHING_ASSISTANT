import json
from fde_datasets import incident

# Possible root causes the team is arguing about (given). Set ROOT_CAUSE to one key once the data convinces you.
CAUSES = {
    "anthropic_outage": "The Claude API was having an outage",
    "traffic_spike": "Ticket volume spiked and overwhelmed the service",
    "prompt_prefix_changes_every_request": "The system prompt changed on every request, so prompt caching stopped working",
    "bad_model_output": "The model started returning invalid output",
}


def parse_lines(lines):
    records, skipped = [], 0
    for line in lines:
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            skipped += 1
            continue
        if not isinstance(record, dict) or "ts" not in record or "event" not in record:
            skipped += 1
            continue
        records.append(record)
    records.sort(key=lambda r: r["ts"])
    return records, skipped


def request_timeline(records, request_id):
    timeline = []
    for r in records:
        if r.get("request_id") != request_id:
            continue
        line = f"{r['ts'][11:19]} {r['event']}"
        if r["event"] == "llm_error":
            line += f" {r['error_type']} (attempt {r['attempt']})"
        elif r["event"] == "llm_call":
            line += f" {r['latency_ms']}ms"
        elif r["event"] == "http_request":
            line += f" {r['status']}"
        timeline.append(line)
    return timeline


def by_version(records):
    stats = {}
    for r in records:
        if r["event"] not in ("llm_call", "llm_error"):
            continue
        s = stats.setdefault(r["version"], {"calls": [], "errors": 0})
        if r["event"] == "llm_error":
            s["errors"] += 1
        else:
            s["calls"].append(r)
    report = {}
    for version, s in stats.items():
        calls, n = s["calls"], len(s["calls"])
        report[version] = {
            "calls": n,
            "errors": s["errors"],
            "cache_hit_rate": round(sum(c["cache_read_tokens"] > 0 for c in calls) / n, 3),
            "cache_write_rate": round(sum(c["cache_write_tokens"] > 0 for c in calls) / n, 3),
            "avg_cost_usd": round(sum(c["cost_usd"] for c in calls) / n, 6),
            "avg_latency_ms": round(sum(c["latency_ms"] for c in calls) / n),
        }
    return report


def incident_summary(records):
    versions = by_version(records)
    bad = max(versions, key=lambda v: versions[v]["errors"])
    deploys = [r for r in records if r["event"] == "deploy"]
    i = next(i for i, d in enumerate(deploys) if d["version"] == bad)
    good = deploys[i - 1]["version"]
    rollback = next(d for d in deploys[i + 1:] if d["version"] != bad)
    first_error = next(r for r in records if r["event"] == "llm_error")
    extra = (versions[bad]["avg_cost_usd"] - versions[good]["avg_cost_usd"]) * versions[bad]["calls"]
    return {
        "bad_version": bad,
        "deployed_at": deploys[i]["ts"][11:19],
        "rolled_back_at": rollback["ts"][11:19],
        "first_error_at": first_error["ts"][11:19],
        "failed_requests": sum(1 for r in records if r["event"] == "http_request" and r["status"] >= 500),
        "extra_cost_usd": round(extra, 4),
    }


ROOT_CAUSE = "prompt_prefix_changes_every_request"


# --- Try it out (not graded) ---
parsed = parse_lines(incident.LOG_LINES)
if parsed:
    records, skipped = parsed
    print(f"{len(records)} records, {skipped} unparseable lines skipped")
    for r in records:
        if r["event"] == "deploy":
            print(f"   deploy {r['ts']} {r['version']}: {r['change']}")
    print("\nOne failed request:")
    for line in request_timeline(records, "req-1166") or []:
        print("  ", line)
    print("\nBy version:")
    for version, s in (by_version(records) or {}).items():
        print(f"   {version}: {s}")
    print("\nSummary:", incident_summary(records))
print("Root cause:", CAUSES.get(ROOT_CAUSE, "not chosen yet"))
