PRIORITY_ORDER = ["must", "should", "could"]

PLAN = [
    {"id": "W1", "title": "Email + PDF ingestion", "days": 6, "priority": "must"},
    {"id": "W2", "title": "Pre-fill 8 core fields", "days": 8, "priority": "must"},
    {"id": "W3", "title": "Low-confidence highlighting", "days": 4, "priority": "should"},
    {"id": "W4", "title": "Adjuster feedback button", "days": 3, "priority": "should"},
    {"id": "W5", "title": "Weekly metrics report", "days": 2, "priority": "could"},
    {"id": "W6", "title": "Dark mode for review screen", "days": 2, "priority": "could"},
]
CAPACITY = 25

REQUESTS = [
    {"id": "CR-3", "title": "Add commercial claims", "days": 6, "priority": "must"},
    {"id": "CR-4", "title": "Fraud score on every claim", "days": 5, "priority": "could"},
    {"id": "CR-5", "title": "Write back to ClaimsPro for all lines of business", "days": 20, "priority": "must"},
]


def plan_load(items):
    return sum(item["days"] for item in items)


def evaluate_change(items, capacity, change):
    rank = PRIORITY_ORDER.index
    load = plan_load(items)
    if load + change["days"] <= capacity:
        return {"decision": "accept", "drop": [], "slip_days": 0}
    if change["priority"] == "could":
        return {"decision": "defer", "drop": [], "slip_days": 0}

    candidates = sorted(
        (i for i in items if rank(i["priority"]) > rank(change["priority"])),
        key=lambda i: (-rank(i["priority"]), -i["days"], i["id"]),
    )
    dropped = []
    for item in candidates:
        dropped.append(item["id"])
        load -= item["days"]
        if load + change["days"] <= capacity:
            return {"decision": "swap", "drop": dropped, "slip_days": 0}

    return {"decision": "slip", "drop": [], "slip_days": plan_load(items) + change["days"] - capacity}


def change_note(change, result):
    cid = change["id"]
    decision = result["decision"]
    if decision == "accept":
        return f"{cid} accepted: fits in current capacity."
    if decision == "defer":
        return f"{cid} deferred to the next phase."
    if decision == "swap":
        return f"{cid} fits if we defer: {', '.join(result['drop'])}."
    return f"{cid} adds {result['slip_days']} days; the deadline moves unless we cut scope."


# --- Try it out (not graded) ---
print(f"Plan load: {plan_load(PLAN)} of {CAPACITY} days\n")
for cr in REQUESTS:
    result = evaluate_change(PLAN, CAPACITY, cr)
    print(f"{cr['id']} ({cr['priority']}, {cr['days']}d): {result}")
    print("   ->", change_note(cr, result) if result else None)
