EXPECTED = {
    "customer": "Brightline Health",
    "date": "2026-03-02",
    "stakeholders": [
        {"name": "Dana Ruiz", "title": "VP Operations", "role": "sponsor"},
        {"name": "Sam Okafor", "title": "IT Director", "role": "blocker"},
        {"name": "Priya Nair", "title": "Intake Lead", "role": "champion"},
        {"name": "Leo Park", "title": "Intake Specialist", "role": None},
    ],
    "goals": ["Cut referral intake from 3 days to same-day", "Reduce manual data entry errors"],
    "risks": ["EHR vendor API access needs ~6 weeks of approval"],
    "actions": [
        {"owner": "Sam", "task": "Share sandbox credentials by Friday"},
        {"owner": "FDE", "task": "Profile one month of fax referrals"},
    ],
}

SAMPLE = """Customer: Brightline Health
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

OTHER = """
action items:
* [Marta]  Send last quarter's shipment export

CUSTOMER : NorthStar Logistics
attendees:
* Marta Gomez (COO) [Sponsor]
* Ian Wu (Data Engineer)
"""


def _get():
    p = parse_notes(SAMPLE)
    assert isinstance(p, dict), f"parse_notes should return a dict, got {type(p).__name__}"
    return p


def test_keys():
    """parse_notes() returns exactly the six required keys"""
    p = _get()
    assert set(p) == set(EXPECTED), f"expected keys {sorted(EXPECTED)}, got {sorted(p)}"


def test_customer_and_date():
    """Customer and date are extracted"""
    p = _get()
    assert p["customer"] == "Brightline Health", f"customer: got {p['customer']!r}"
    assert p["date"] == "2026-03-02", f"date: got {p['date']!r}"


def test_stakeholders():
    """Stakeholders have name, title and lowercased role (None when missing)"""
    p = _get()
    for want, got in zip(EXPECTED["stakeholders"], p["stakeholders"]):
        assert got == want, f"expected {want}, got {got}"
    assert len(p["stakeholders"]) == 4, f"expected 4 stakeholders, got {len(p['stakeholders'])}"


def test_goals_and_risks():
    """Goals and risks are lists of clean strings"""
    p = _get()
    assert p["goals"] == EXPECTED["goals"], f"goals: got {p['goals']!r}"
    assert p["risks"] == EXPECTED["risks"], f"risks: got {p['risks']!r}"


def test_actions():
    """Action items are split into owner and task, whitespace trimmed"""
    p = _get()
    assert p["actions"] == EXPECTED["actions"], f"actions: got {p['actions']!r}"


def test_other_order_and_missing_sections():
    """Works with sections in a different order, odd casing, and missing sections"""
    p = parse_notes(OTHER)
    assert p["customer"] == "NorthStar Logistics", f"customer: got {p['customer']!r}"
    assert p["date"] is None, f"date should be None when missing, got {p['date']!r}"
    assert p["goals"] == [] and p["risks"] == [], "missing sections should be empty lists"
    assert p["actions"] == [{"owner": "Marta", "task": "Send last quarter's shipment export"}], f"actions: got {p['actions']!r}"
    assert p["stakeholders"] == [
        {"name": "Marta Gomez", "title": "COO", "role": "sponsor"},
        {"name": "Ian Wu", "title": "Data Engineer", "role": None},
    ], f"stakeholders: got {p['stakeholders']!r}"


def test_missing_roles_none_missing():
    """missing_roles() returns [] when sponsor and champion are present"""
    got = missing_roles(_get())
    assert got == [], f"expected [], got {got!r}"


def test_missing_roles_detects_gaps():
    """missing_roles() lists absent roles in order sponsor, champion"""
    got = missing_roles(parse_notes(OTHER))
    assert got == ["champion"], f"NorthStar has a sponsor but no champion; expected ['champion'], got {got!r}"
    got = missing_roles({"stakeholders": []})
    assert got == ["sponsor", "champion"], f"with no stakeholders expected ['sponsor', 'champion'], got {got!r}"
