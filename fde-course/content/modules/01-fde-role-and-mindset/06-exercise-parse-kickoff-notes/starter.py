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


def parse_notes(text):
    """Parse kickoff notes into a dict with keys:
    customer, date, stakeholders, goals, risks, actions."""
    result = {
        "customer": None,
        "date": None,
        "stakeholders": [],
        "goals": [],
        "risks": [],
        "actions": [],
    }
    # TODO: walk through the lines and fill in `result`
    return result


def missing_roles(parsed):
    """Return the required roles ("sponsor", "champion") that no stakeholder has."""
    # TODO
    pass


# --- Try it out (not graded) ---
import json
parsed = parse_notes(NOTES)
print(json.dumps(parsed, indent=2))
print("Missing roles:", missing_roles(parsed))
