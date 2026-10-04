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
    high_influence = s["influence"] >= 3
    high_interest = s["interest"] >= 3
    if high_influence and high_interest:
        return "manage closely"
    if high_influence:
        return "keep satisfied"
    if high_interest:
        return "keep informed"
    return "monitor"


def engagement_plan(stakeholders):
    ordered = sorted(
        stakeholders,
        key=lambda s: (QUADRANT_ORDER.index(quadrant(s)), -s["influence"], s["name"]),
    )
    return [{"name": s["name"], "quadrant": quadrant(s), "cadence": CADENCE[quadrant(s)]} for s in ordered]


def risks(stakeholders):
    found = []
    roles = {s["role"] for s in stakeholders}
    if "sponsor" not in roles:
        found.append("no sponsor")
    if "champion" not in roles:
        found.append("no champion")
    if any(s["role"] == "sponsor" and s["stance"] != "supporter" for s in stakeholders):
        found.append("sponsor is not a supporter")
    for s in stakeholders:
        if s["stance"] == "skeptic" and s["influence"] >= 4:
            found.append(f"high-influence skeptic: {s['name']}")
    return found


# --- Try it out (not graded) ---
for row in engagement_plan(LUMEN) or []:
    print(f"{row['name']:<15} {row['quadrant']:<16} {row['cadence']}")
print()
print("Risks:", risks(LUMEN))
