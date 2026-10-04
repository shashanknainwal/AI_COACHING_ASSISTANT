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
    if run is None:
        checks = {name: False for name in CHECKS}
        return {"checks": checks, "pass": False}
    expect, decision = case["expect"], run["decision"] or {}
    ok_calls = [a["tool"] for a in run["audit"] if not a["is_error"]]
    all_calls = [a["tool"] for a in run["audit"]]
    checks = {
        "decided": run["decision"] is not None,
        "action": decision.get("action") == expect["action"],
        "priority": decision.get("priority") == expect["priority"],
        "notified": "notify_customer" in ok_calls if expect["must_notify"] else True,
        "no_forbidden": not any(t in expect["forbidden"] for t in all_calls),
    }
    return {"checks": checks, "pass": all(checks.values())}


def run_suite(client, cases, approver):
    rows = []
    for case in cases:
        run, error = None, None
        try:
            run = run_triage(client, case["shipment_id"], approver)
        except Exception as e:
            error = f"{type(e).__name__}: {e}"
        rows.append({"id": case["id"], "type": case["type"], "expected_priority": case["expect"]["priority"],
                     "run": run, "error": error, "grades": grade(case, run)})
    return rows


def report(rows):
    failed, by_type = {}, {}
    for row in rows:
        for name, ok in row["grades"]["checks"].items():
            if not ok:
                failed[name] = failed.get(name, 0) + 1
        by_type.setdefault(row["type"], []).append(row["grades"]["pass"])
    p1 = [r["grades"]["checks"]["priority"] for r in rows if r["expected_priority"] == "P1"]
    runs = [r["run"] for r in rows if r["run"] is not None]
    return {
        "n": len(rows),
        "pass_rate": round(sum(r["grades"]["pass"] for r in rows) / len(rows), 3),
        "failed_checks": failed,
        "by_type": {t: round(sum(v) / len(v), 3) for t, v in by_type.items()},
        "p1_recall": round(sum(p1) / len(p1), 3) if p1 else None,
        "avg_cost_usd": round(sum(r["cost_usd"] for r in runs) / len(runs), 4) if runs else None,
        "avg_steps": round(sum(r["steps"] for r in runs) / len(runs), 2) if runs else None,
    }


def ship_decision(rep, min_pass_rate=0.9, min_p1_recall=1.0, max_cost_usd=0.05):
    reasons = []
    if rep["pass_rate"] < min_pass_rate:
        reasons.append(f"pass rate {rep['pass_rate']:.3f} is below {min_pass_rate:.3f}")
    if rep["p1_recall"] is not None and rep["p1_recall"] < min_p1_recall:
        reasons.append(f"P1 recall {rep['p1_recall']:.3f} is below {min_p1_recall:.3f}")
    if rep["avg_cost_usd"] is not None and rep["avg_cost_usd"] > max_cost_usd:
        reasons.append(f"average cost ${rep['avg_cost_usd']:.4f} is above ${max_cost_usd:.4f}")
    return {"ship": not reasons, "reasons": reasons}


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
