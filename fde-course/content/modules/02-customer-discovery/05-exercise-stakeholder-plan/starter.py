QUADRANT_ORDER = ["manage closely", "keep satisfied", "keep informed", "monitor"]

CADENCE = {
    "manage closely": "weekly 1:1",
    "keep satisfied": "biweekly update",
    "keep informed": "weekly email",
    "monitor": "monthly note",
}

LUMEN = [
    {"name": "Joan Pierce", "title": "VP Claims", "influence": 5, "interest": 4, "stance": "supporter", "role": "sponsor"},
    {"name": "Marcus Lee", "title": "Claims Ops Lead", "influence": 3, "interest": 5, "stance": "supporter", "role": "champion"},
    {"name": "Ravi Shah", "title": "CISO", "influence": 5, "interest": 2, "stance": "skeptic", "role": "gatekeeper"},
    {"name": "Adjuster team", "title": "Claims Adjusters", "influence": 2, "interest": 5, "stance": "neutral", "role": "user"},
    {"name": "Dee Ortiz", "title": "Finance BP", "influence": 2, "interest": 2, "stance": "neutral", "role": None},
    {"name": "Tom Bray", "title": "IT Director", "influence": 4, "interest": 3, "stance": "neutral", "role": "gatekeeper"},
]


def quadrant(s):
    """Return the power/interest quadrant for one stakeholder."""
    # TODO
    pass


def engagement_plan(stakeholders):
    """Return [{"name", "quadrant", "cadence"}, ...] sorted by priority."""
    # TODO
    pass


def risks(stakeholders):
    """Return the list of stakeholder risks to act on."""
    # TODO
    pass


# --- Try it out (not graded) ---
for row in engagement_plan(LUMEN) or []:
    print(f"{row['name']:<15} {row['quadrant']:<16} {row['cadence']}")
print()
print("Risks:", risks(LUMEN))
