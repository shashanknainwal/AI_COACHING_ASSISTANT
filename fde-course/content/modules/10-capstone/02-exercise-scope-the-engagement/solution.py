import json
import math
import statistics
import anthropic
from fde_datasets import northstar

client = anthropic.Anthropic()
MODEL = "claude-opus-5-5"
BUDGET_DAYS = 20
BRIEF_SCHEMA = {
    "type": "object",
    "properties": {
        "problem_statement": {"type": "string"},
        "executive_summary": {"type": "string"},
        "risks": {"type": "array", "items": {"type": "string"}},
        "open_questions": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["problem_statement", "executive_summary", "risks", "open_questions"],
    "additionalProperties": False,
}


def baseline(history):
    days = len({h["date"] for h in history})
    minutes = sorted(h["handle_minutes"] for h in history)
    by_tier, by_type = {}, {}
    for h in history:
        by_tier.setdefault(h["tier"], []).append(h["breached"])
        by_type[h["type"]] = by_type.get(h["type"], 0) + 1
    return {
        "per_day": round(len(history) / days, 1),
        "median_handle_minutes": statistics.median(minutes),
        "p90_handle_minutes": minutes[math.ceil(0.9 * len(minutes)) - 1],
        "ops_hours_per_day": round(sum(minutes) / days / 60, 1),
        "breach_rate": round(sum(h["breached"] for h in history) / len(history), 3),
        "breach_rate_by_tier": {t: round(sum(v) / len(v), 3) for t, v in by_tier.items()},
        "by_type": by_type,
    }


def prioritize(asks, budget_days):
    must = [a for a in asks if a["must_have"]]
    need = sum(a["effort_days"] for a in must)
    if need > budget_days:
        raise ValueError(f"must-haves need {need} days but the budget is {budget_days}")
    in_scope, used = [a["id"] for a in must], need
    rest = sorted((a for a in asks if not a["must_have"]),
                  key=lambda a: (-a["value"] / a["effort_days"], a["effort_days"], a["id"]))
    for a in rest:
        if used + a["effort_days"] <= budget_days:
            in_scope.append(a["id"])
            used += a["effort_days"]
    out = sorted(a["id"] for a in asks if a["id"] not in in_scope)
    return {"in_scope": in_scope, "out_of_scope": out, "days_used": used, "days_left": budget_days - used}


def success_metrics(base):
    return [
        {"metric": "median_handle_minutes", "baseline": base["median_handle_minutes"],
         "target": round(base["median_handle_minutes"] * 0.5, 1)},
        {"metric": "sla_breach_rate", "baseline": base["breach_rate"], "target": round(base["breach_rate"] / 2, 3)},
        {"metric": "automation_rate", "baseline": 0.0, "target": 0.4},
    ]


def draft_brief(client, facts):
    prompt = ("Draft the engagement brief for NorthStar Logistics from these facts. Use only these numbers.\n\n"
              f"<engagement_facts>\n{json.dumps(facts, indent=2, sort_keys=True)}\n</engagement_facts>")
    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
        output_config={"effort": "medium", "format": {"type": "json_schema", "schema": BRIEF_SCHEMA}},
    )
    if response.stop_reason == "refusal":
        raise RuntimeError("the model declined to draft the brief")
    return json.loads(next(b.text for b in response.content if b.type == "text"))


# --- Try it out (not graded) ---
base = baseline(northstar.EXCEPTION_HISTORY)
if base:
    print("Baseline:", json.dumps(base, indent=2))
plan = prioritize(northstar.ASKS, BUDGET_DAYS)
if plan:
    print("\nScope:", plan)
    for ask in northstar.ASKS:
        mark = "IN " if ask["id"] in plan["in_scope"] else "out"
        print(f"   [{mark}] {ask['id']} ({ask['effort_days']}d, value {ask['value']}) {ask['ask']}  - {ask['from']}")
metrics = success_metrics(base) if base else None
if metrics:
    print("\nSuccess metrics:", metrics)
if base and plan and metrics:
    brief = draft_brief(client, {"baseline": base, "scope": plan, "metrics": metrics, "budget_days": BUDGET_DAYS})
    if brief:
        print("\nDraft brief:", json.dumps(brief, indent=2))
