SKILL_MD = """---
name: shipment-exceptions
description: "Cindervale's playbook for shipment exceptions: customs holds, damaged containers or pallets, a missed pickup, a late delivery or delay, and a refused delivery at the dock. Use when a shipment is stuck, held, damaged, crushed, delayed, late, missed or refused, or when ops asks for the next steps or the playbook for a disruption. Runs a script that classifies the exception and says whether to escalate."
---

# Shipment exceptions

Use this skill to handle one shipment exception from first report to hand-off.

## Steps

1. Get the exception code and the facts the script needs (see references/exception-codes.md).
2. Run `python scripts/classify_exception.py '<event as JSON>'`. It prints the category,
   the first action and whether to escalate. Trust its output over your own reading of the rules.
3. Do the first action. If `escalate` is true, page the duty manager with the shipment ID,
   the category and what you have done so far.
4. Write a short note on the shipment: what happened, what you did, who owns it now.

## When you need more detail

- Codes and the fields each one needs: references/exception-codes.md
- Escalation thresholds and the reasons behind them: references/escalation-rules.md

Read a reference file only when the step above needs it.

## Never

- Promise the customer a delivery date before the carrier confirms it.
- Unload other goods before damage photos exist.
"""

EXCEPTION_CODES_MD = """# Exception codes

| Code | Category | Fields the script needs |
|---|---|---|
| CUS-HOLD | customs_hold | hold_days |
| DMG | damage | value_eur |
| PU-MISS | missed_pickup | customer_tier |
| LATE | delay | delay_hours |
| REF | refused_delivery | none |

Any other code is treated as unknown and goes to the duty manager.

Where the facts come from:
- hold_days: the customs broker's status message.
- value_eur: the commercial invoice attached to the booking.
- customer_tier: the account record (standard, silver or gold).
- delay_hours: the carrier's new ETA minus the booked ETA.
"""

ESCALATION_RULES_MD = """# Escalation rules

These thresholds come from the operations playbook. Change them here and in the script together.

| Category | First action | Escalate when |
|---|---|---|
| customs_hold | request_missing_documents | held more than 3 days |
| damage | photograph_and_file_claim | goods value over EUR 10,000 |
| missed_pickup | rebook_next_slot | customer tier is gold |
| delay | notify_consignee | more than 48 hours late |
| refused_delivery | contact_shipper | always |
| unknown | route_to_duty_manager | always |

Why these numbers:
- Customs holds over 3 days usually mean a document problem the broker can't fix alone.
- Claims over EUR 10,000 need the insurer told within one working day.
- Gold-tier contracts carry penalty clauses for missed collections.
- Delays over 48 hours trigger the consignee's right to refuse the goods.
"""

CLASSIFY_PY = '''import json
import sys

CATEGORIES = {"CUS-HOLD": "customs_hold", "DMG": "damage", "PU-MISS": "missed_pickup",
              "LATE": "delay", "REF": "refused_delivery"}
FIRST_ACTION = {"customs_hold": "request_missing_documents", "damage": "photograph_and_file_claim",
                "missed_pickup": "rebook_next_slot", "delay": "notify_consignee",
                "refused_delivery": "contact_shipper", "unknown": "route_to_duty_manager"}


def classify_exception(event):
    category = CATEGORIES.get(event.get("code"), "unknown")
    if category == "customs_hold":
        escalate = event.get("hold_days", 0) > 3
    elif category == "damage":
        escalate = event.get("value_eur", 0) > 10000
    elif category == "missed_pickup":
        escalate = event.get("customer_tier") == "gold"
    elif category == "delay":
        escalate = event.get("delay_hours", 0) > 48
    else:
        escalate = True
    return {"category": category, "first_action": FIRST_ACTION[category], "escalate": escalate}


if __name__ == "__main__" and len(sys.argv) > 1:
    print(json.dumps(classify_exception(json.loads(sys.argv[1]))))
'''

SKILL_FILES = {
    "SKILL.md": SKILL_MD,
    "references/exception-codes.md": EXCEPTION_CODES_MD,
    "references/escalation-rules.md": ESCALATION_RULES_MD,
    "scripts/classify_exception.py": CLASSIFY_PY,
}


def run_trigger_eval(skill_files, cases):
    """Route every case with our skill plus the competing skills. Returns {"passed", "total", "failures"}."""
    meta, _ = parse_skill_md(skill_files.get("SKILL.md", ""))
    skills = [{"name": meta.get("name", ""), "description": meta.get("description", "")}] + COMPETING_SKILLS
    failures = []
    for query, expected in cases:
        got = route(query, skills)
        if got != expected:
            failures.append({"query": query, "expected": expected, "got": got})
    return {"passed": len(cases) - len(failures), "total": len(cases), "failures": failures}


def run_behaviour_eval(skill_files, cases):
    """Execute the packaged script and check it against each case. Returns {"passed", "total", "failures"}."""
    ns = {"__name__": "skill_script"}
    exec(skill_files.get("scripts/classify_exception.py", ""), ns)
    fn = ns.get("classify_exception")
    failures = []
    for event, expected in cases:
        got = fn(event) if fn else None
        if got != expected:
            failures.append({"event": event, "expected": expected, "got": got})
    return {"passed": len(cases) - len(failures), "total": len(cases), "failures": failures}


# --- Try it out (not graded) ---
meta, body = parse_skill_md(SKILL_FILES["SKILL.md"])
print("name:", meta.get("name"), "| description length:", len(meta.get("description", "")), "| body lines:", len(body.splitlines()))
print("trigger eval:", run_trigger_eval(SKILL_FILES, TRIGGER_CASES))
print("behaviour eval:", run_behaviour_eval(SKILL_FILES, BEHAVIOUR_CASES))
