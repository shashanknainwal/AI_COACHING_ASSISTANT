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
    """Today's numbers, before any automation."""
    # TODO
    pass


def prioritize(asks, budget_days):
    """Must-haves first, then the best value per day that still fits the budget."""
    # TODO
    pass


def success_metrics(base):
    """Three measurable targets agreed with the sponsor."""
    # TODO
    pass


def draft_brief(client, facts):
    """Ask Claude to draft the brief from the facts, as structured output."""
    # TODO
    pass


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
