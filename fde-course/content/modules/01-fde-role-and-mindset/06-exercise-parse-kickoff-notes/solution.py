NOTES = """Customer: Brightline Health
Date: 2026-03-02

ATTENDEES:
- Dana Ruiz (VP Operations) [sponsor]
-   Sam Okafor (IT Director) [blocker]
* Priya Nair (Intake Lead) [Champion]
- Leo Park (Intake Specialist)

goals :
- Cut referral intake from 3 days to same-day
- Reduce manual data entry errors

Risks:
- EHR vendor API access needs ~6 weeks of approval

Action Items:
- [Sam] Share sandbox credentials by Friday
- [FDE]   Profile one month of fax referrals
"""

SECTIONS = {"attendees": "stakeholders", "goals": "goals", "risks": "risks", "actionitems": "actions"}
REQUIRED_ROLES = ["sponsor", "champion"]


def _between(s, left, right):
    start = s.find(left)
    end = s.find(right, start + 1)
    if start == -1 or end == -1:
        return None
    return s[start + 1:end].strip()


def _stakeholder(item):
    title = _between(item, "(", ")")
    role = _between(item, "[", "]")
    cut = min([i for i in (item.find("("), item.find("[")) if i != -1], default=len(item))
    return {
        "name": item[:cut].strip(),
        "title": title,
        "role": role.lower() if role else None,
    }


def _action(item):
    owner = _between(item, "[", "]")
    task = item[item.find("]") + 1:].strip() if owner is not None else item
    return {"owner": owner, "task": task}


def parse_notes(text):
    result = {"customer": None, "date": None, "stakeholders": [], "goals": [], "risks": [], "actions": []}
    section = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line[0] in "-*":
            item = line[1:].strip()
            if section == "stakeholders":
                result["stakeholders"].append(_stakeholder(item))
            elif section == "actions":
                result["actions"].append(_action(item))
            elif section in ("goals", "risks"):
                result[section].append(item)
            continue
        key, _, value = line.partition(":")
        norm = key.lower().replace(" ", "")
        if norm in SECTIONS:
            section = SECTIONS[norm]
        elif norm in ("customer", "date"):
            result[norm] = value.strip() or None
    return result


def missing_roles(parsed):
    present = {s["role"] for s in parsed["stakeholders"]}
    return [r for r in REQUIRED_ROLES if r not in present]


import json
parsed = parse_notes(NOTES)
print(json.dumps(parsed, indent=2))
print("Missing roles:", missing_roles(parsed))
