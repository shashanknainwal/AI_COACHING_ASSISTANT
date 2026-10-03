def score(request):
    """Return impact * urgency / effort, rounded to 2 decimals. Blocked requests score 0."""
    if request["blocked"]:
        return 0
    return round(request["impact"] * request["urgency"] / request["effort"], 2)


def plan_sprint(requests, capacity):
    """Return the ids of the requests to work on this sprint, in priority order."""
    ranked = sorted(requests, key=lambda r: (-score(r), r["effort"], r["id"]))
    plan = []
    remaining = capacity
    for r in ranked:
        if score(r) <= 0:
            continue
        if r["effort"] <= remaining:
            plan.append(r["id"])
            remaining -= r["effort"]
    return plan


backlog = [
    {"id": "BH-1", "title": "Fax intake OCR for referrals", "impact": 4, "urgency": 3, "effort": 5, "blocked": False},
    {"id": "BH-2", "title": "SSO login for clinic staff", "impact": 3, "urgency": 5, "effort": 2, "blocked": False},
    {"id": "BH-3", "title": "Auto-extract insurance member IDs", "impact": 5, "urgency": 4, "effort": 3, "blocked": False},
    {"id": "BH-4", "title": "EHR write-back integration", "impact": 5, "urgency": 5, "effort": 8, "blocked": True},
    {"id": "BH-5", "title": "Dashboard color tweaks", "impact": 1, "urgency": 2, "effort": 1, "blocked": False},
]

for r in backlog:
    print(r["id"], score(r))

print("Plan:", plan_sprint(backlog, capacity=10))
