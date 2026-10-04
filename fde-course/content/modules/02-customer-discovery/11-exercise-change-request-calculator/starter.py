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
    """Total engineering days in the plan."""
    # TODO
    pass


def evaluate_change(items, capacity, change):
    """Return {"decision", "drop", "slip_days"} for a change request."""
    # TODO
    pass


def change_note(change, result):
    """One-line message to the sponsor describing the result."""
    # TODO
    pass


# --- Try it out (not graded) ---
print(f"Plan load: {plan_load(PLAN)} of {CAPACITY} days\n")
for cr in REQUESTS:
    result = evaluate_change(PLAN, CAPACITY, cr)
    print(f"{cr['id']} ({cr['priority']}, {cr['days']}d): {result}")
    print("   ->", change_note(cr, result) if result else None)
