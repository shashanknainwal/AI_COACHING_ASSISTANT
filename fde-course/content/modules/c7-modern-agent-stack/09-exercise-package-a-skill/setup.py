"""Hidden setup: a toy skill router, a competing skill, and the eval cases. All fictional."""
import re

BODY_MAX_LINES = 60  # this course's packaging rule, stricter than the general "under 500 lines" guidance

COMPETING_SKILLS = [
    {
        "name": "carrier-invoices",
        "description": (
            "Check carrier invoices against agreed rates. Use when someone asks about an invoice, a bill, "
            "being billed twice, a surcharge charged on an invoice, rates, or a credit note from a carrier."
        ),
    },
]

_STOP = set("""about above after again against also because been before being below between both could does doing
down during each from further have having here into itself just more most other over same should some such than
that their them then there these they this those through under until very what when where which while will with
would your yours you our ours we us the and for are but not can how why who whom its it's what's""".split())


def parse_skill_md(text):
    """Split SKILL.md into (frontmatter dict, body). Supports single-line 'key: value' frontmatter."""
    if not isinstance(text, str) or not text.startswith("---\n"):
        return {}, text or ""
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text
    meta = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            v = v.strip()
            if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
                v = v[1:-1]
            meta[k.strip()] = v
    body = text[end + 4:].lstrip("\n")
    return meta, body


def _tokens(text):
    words = re.findall(r"[a-z]+", text.lower())
    out = set()
    for w in words:
        if len(w) < 4 or w in _STOP:
            continue
        out.add(w[:-1] if w.endswith("s") and len(w) > 4 else w)
    return out


def route(query, skills):
    """A toy stand-in for how a model picks a skill from names and descriptions.

    It scores word overlap between the query and each description and picks the best skill
    if it overlaps on at least two words and beats the runner-up. A real model judges meaning,
    not words, so a real trigger eval runs the model (see the capstone kit). The discipline is
    the same: a fixed set of should-trigger and should-not-trigger queries, run on every change.
    """
    q = _tokens(query)
    scored = sorted(((len(q & _tokens(s["description"])), s["name"]) for s in skills), reverse=True)
    if not scored or scored[0][0] < 2 or (len(scored) > 1 and scored[1][0] == scored[0][0]):
        return None
    return scored[0][1]


SKILL_NAME = "shipment-exceptions"

TRIGGER_CASES = [
    ("Shipment CV-1042 is stuck in a customs hold at the port. What do we do now?", SKILL_NAME),
    ("The container arrived damaged at the depot and the pallets are crushed. Next steps?", SKILL_NAME),
    ("Driver missed the pickup window for this morning's collection", SKILL_NAME),
    ("A truck broke down and the delivery will be two days late. How should ops handle the delay?", SKILL_NAME),
    ("The consignee refused the delivery at the dock. What's the playbook?", SKILL_NAME),
    ("Brask Haulage billed us twice for the same fuel surcharge on last month's invoice", "carrier-invoices"),
    ("Can you check this carrier invoice against our agreed rates?", "carrier-invoices"),
    ("Write a short poem about trains", None),
    ("What time is it in Lyon right now?", None),
]

BEHAVIOUR_CASES = [
    ({"code": "CUS-HOLD", "hold_days": 1}, {"category": "customs_hold", "first_action": "request_missing_documents", "escalate": False}),
    ({"code": "CUS-HOLD", "hold_days": 5}, {"category": "customs_hold", "first_action": "request_missing_documents", "escalate": True}),
    ({"code": "DMG", "value_eur": 2500}, {"category": "damage", "first_action": "photograph_and_file_claim", "escalate": False}),
    ({"code": "DMG", "value_eur": 18000}, {"category": "damage", "first_action": "photograph_and_file_claim", "escalate": True}),
    ({"code": "PU-MISS", "customer_tier": "standard"}, {"category": "missed_pickup", "first_action": "rebook_next_slot", "escalate": False}),
    ({"code": "PU-MISS", "customer_tier": "gold"}, {"category": "missed_pickup", "first_action": "rebook_next_slot", "escalate": True}),
    ({"code": "LATE", "delay_hours": 20}, {"category": "delay", "first_action": "notify_consignee", "escalate": False}),
    ({"code": "LATE", "delay_hours": 60}, {"category": "delay", "first_action": "notify_consignee", "escalate": True}),
    ({"code": "REF"}, {"category": "refused_delivery", "first_action": "contact_shipper", "escalate": True}),
    ({"code": "XYZ"}, {"category": "unknown", "first_action": "route_to_duty_manager", "escalate": True}),
]

PLAYBOOK_NOTES = """Cindervale exception playbook (ops wiki export, fictional)
- Codes: CUS-HOLD customs hold, DMG damage, PU-MISS missed pickup, LATE delay, REF refused delivery.
- Customs hold: ask the shipper for the missing documents first. Escalate if held more than 3 days.
- Damage: photograph and file a claim before unloading anything else. Escalate if goods value over EUR 10,000.
- Missed pickup: rebook the next slot. Escalate for gold-tier customers.
- Delay: notify the consignee with a new ETA. Escalate if more than 48 hours late.
- Refused delivery: contact the shipper and always escalate.
- Anything else: route to the duty manager and escalate.
"""
