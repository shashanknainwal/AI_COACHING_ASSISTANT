import anthropic
from fde_datasets.northstar_agent import run_triage   # NorthStar's production version of your agent (given)

client = anthropic.Anthropic()


def _case(cid, sid, typ, action, priority, must_notify=True, forbidden=()):
    return {"id": cid, "shipment_id": sid, "type": typ,
            "expect": {"action": action, "priority": priority, "must_notify": must_notify, "forbidden": list(forbidden)}}


# Labeled by Marcus Bell (ops team lead): what a good coordinator would do for each shipment (given).
EVAL_CASES = [
    _case("E-01", "NS-2017", "CUSTOMS_HOLD", "escalate_customs", "P1"),
    _case("E-02", "NS-2001", "DELAY", "notify_and_ticket", "P1"),
    _case("E-03", "NS-2006", "PICKUP_MISSED", "reroute", "P1"),
    _case("E-04", "NS-2018", "DELAY", "notify_and_ticket", "P1"),
    _case("E-05", "NS-2014", "CUSTOMS_HOLD", "escalate_customs", "P2"),
    _case("E-06", "NS-2003", "DAMAGE", "open_claim", "P2"),
    _case("E-07", "NS-2008", "ADDRESS_ISSUE", "request_address", "P2"),
    _case("E-08", "NS-2011", "DELAY", "notify_only", "P2"),
    _case("E-09", "NS-2005", "DELAY", "notify_only", "P2"),
    _case("E-10", "NS-2016", "DAMAGE", "open_claim", "P2"),
    _case("E-11", "NS-2019", "ADDRESS_ISSUE", "request_address", "P3"),
    _case("E-12", "NS-2002", "DELIVERED", "no_action", "P3", must_notify=False, forbidden=["notify_customer", "create_ops_ticket"]),
    _case("E-13", "NS-9999", "UNKNOWN", "escalate", "P3", must_notify=False, forbidden=["notify_customer"]),
]
CHECKS = ["decided", "action", "priority", "notified", "no_forbidden"]


def approve_reroutes(request):
    return True


def grade(case, run):
    """{"checks": {five named booleans in CHECKS order}, "pass": bool}; run is None if the agent crashed."""
    # TODO
    pass


def run_suite(client, cases, approver):
    """Run the agent on every case; one row per case."""
    # TODO
    pass


def report(rows):
    """The numbers the ship decision is based on."""
    # TODO
    pass


def ship_decision(rep, min_pass_rate=0.9, min_p1_recall=1.0, max_cost_usd=0.05):
    """{"ship": bool, "reasons": [...]}"""
    # TODO
    pass


# --- Try it out (not graded) ---
rows = run_suite(client, EVAL_CASES, approve_reroutes)
if rows:
    rep = report(rows)
    print("Report:", rep)
    for row in rows:
        if not row["grades"]["pass"]:
            failed = [k for k, v in row["grades"]["checks"].items() if not v]
            decision = row["run"]["decision"] if row["run"] else row["error"]
            print(f"   {row['id']} ({row['type']}) failed {failed}: {decision}")
    print("Ship?", ship_decision(rep) if rep else None)
