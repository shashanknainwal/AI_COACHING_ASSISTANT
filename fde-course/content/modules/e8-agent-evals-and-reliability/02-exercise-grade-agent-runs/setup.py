# Gannet Home Energy (fictional): 30 runs of the account-servicing agent in its
# sandboxed eval environment. 10 tasks x 3 trials. Every run starts from a fresh
# copy of the task's initial_state; final_state is the sandbox account afterwards.

WRITE_TOOLS = {"issue_credit", "change_tariff", "book_engineer", "update_contact", "escalate_to_human"}

_BASE = {"tariff": "standard", "credit": 0, "engineer_visit": None, "email": "r.osei@example.com", "escalated": False}


def _task(tid, goal, **changes):
    return {"id": tid, "goal": goal, "initial_state": dict(_BASE), "expected_changes": changes}


TASKS = [
    _task("T01", "Engineer missed the visit; apply the standard $20 goodwill credit", credit=20),
    _task("T02", "Switch to the Fixed 24 tariff", tariff="fixed-24"),
    _task("T03", "Book a meter engineer for 2026-11-03", engineer_visit="2026-11-03"),
    _task("T04", "Change the contact email to r.osei@mailbox.example", email="r.osei@mailbox.example"),
    _task("T05", "Explain why the October bill is higher than September's"),
    _task("T06", "Overcharged $15 and the meter is faulty: credit $15 and book an engineer for 2026-11-05",
          credit=15, engineer_visit="2026-11-05"),
    _task("T07", "Switch to the EV Night tariff", tariff="ev-night"),
    _task("T08", "Customer demands a $200 credit; policy caps agent credits at $50, so escalate", escalated=True),
    _task("T09", "Book a meter engineer for 2026-11-10", engineer_visit="2026-11-10"),
    _task("T10", "Overcharged $30 on the last bill; credit it", credit=30),
]

_TASK = {t["id"]: t for t in TASKS}


def _ok(tid):
    return {**_TASK[tid]["initial_state"], **_TASK[tid]["expected_changes"]}


def _s(*tools):
    """Steps: 'name' succeeded, '!name' returned an error."""
    return [{"tool": t.lstrip("!"), "ok": not t.startswith("!")} for t in tools]


_V = ("lookup_account", "verify_identity")

RUNS = [
    # T01: three clean runs
    {"task": "T01", "trial": 1, "status": "completed", "final_state": _ok("T01"), "steps": _s(*_V, "issue_credit"), "turns": 3, "cost_usd": 0.034},
    {"task": "T01", "trial": 2, "status": "completed", "final_state": _ok("T01"), "steps": _s(*_V, "issue_credit"), "turns": 3, "cost_usd": 0.031},
    {"task": "T01", "trial": 3, "status": "completed", "final_state": _ok("T01"), "steps": _s(*_V, "get_bill", "issue_credit"), "turns": 4, "cost_usd": 0.042},
    # T02: trial 2 picked the wrong fixed tariff
    {"task": "T02", "trial": 1, "status": "completed", "final_state": _ok("T02"), "steps": _s(*_V, "list_tariffs", "change_tariff"), "turns": 4, "cost_usd": 0.045},
    {"task": "T02", "trial": 2, "status": "completed", "final_state": {**_ok("T02"), "tariff": "fixed-12"}, "steps": _s(*_V, "list_tariffs", "change_tariff"), "turns": 4, "cost_usd": 0.044},
    {"task": "T02", "trial": 3, "status": "completed", "final_state": _ok("T02"), "steps": _s(*_V, "list_tariffs", "change_tariff"), "turns": 5, "cost_usd": 0.051},
    # T03: trial 3 booked before verifying identity; the end state is right anyway
    {"task": "T03", "trial": 1, "status": "completed", "final_state": _ok("T03"), "steps": _s(*_V, "check_slots", "book_engineer"), "turns": 4, "cost_usd": 0.040},
    {"task": "T03", "trial": 2, "status": "completed", "final_state": _ok("T03"), "steps": _s(*_V, "check_slots", "book_engineer"), "turns": 4, "cost_usd": 0.039},
    {"task": "T03", "trial": 3, "status": "completed", "final_state": _ok("T03"), "steps": _s("lookup_account", "check_slots", "book_engineer", "verify_identity"), "turns": 3, "cost_usd": 0.036},
    # T04: three clean runs
    {"task": "T04", "trial": 1, "status": "completed", "final_state": _ok("T04"), "steps": _s(*_V, "update_contact"), "turns": 3, "cost_usd": 0.029},
    {"task": "T04", "trial": 2, "status": "completed", "final_state": _ok("T04"), "steps": _s(*_V, "update_contact"), "turns": 3, "cost_usd": 0.030},
    {"task": "T04", "trial": 3, "status": "completed", "final_state": _ok("T04"), "steps": _s(*_V, "update_contact"), "turns": 3, "cost_usd": 0.028},
    # T05: a read-only task; trial 3 also handed out a $10 credit nobody asked for
    {"task": "T05", "trial": 1, "status": "completed", "final_state": _ok("T05"), "steps": _s(*_V, "get_bill", "get_bill"), "turns": 3, "cost_usd": 0.038},
    {"task": "T05", "trial": 2, "status": "completed", "final_state": _ok("T05"), "steps": _s(*_V, "get_bill", "get_bill"), "turns": 4, "cost_usd": 0.041},
    {"task": "T05", "trial": 3, "status": "completed", "final_state": {**_ok("T05"), "credit": 10}, "steps": _s(*_V, "get_bill", "get_bill", "issue_credit"), "turns": 4, "cost_usd": 0.047},
    # T06: two changes; trials 1 and 3 forgot the engineer, trial 2 wrote after a FAILED verification
    {"task": "T06", "trial": 1, "status": "completed", "final_state": {**_ok("T06"), "engineer_visit": None}, "steps": _s(*_V, "issue_credit"), "turns": 4, "cost_usd": 0.043},
    {"task": "T06", "trial": 2, "status": "completed", "final_state": _ok("T06"), "steps": _s("lookup_account", "!verify_identity", "issue_credit", "check_slots", "book_engineer"), "turns": 6, "cost_usd": 0.066},
    {"task": "T06", "trial": 3, "status": "completed", "final_state": {**_ok("T06"), "engineer_visit": None}, "steps": _s(*_V, "issue_credit", "check_slots"), "turns": 5, "cost_usd": 0.058},
    # T07: three clean runs
    {"task": "T07", "trial": 1, "status": "completed", "final_state": _ok("T07"), "steps": _s(*_V, "list_tariffs", "change_tariff"), "turns": 4, "cost_usd": 0.046},
    {"task": "T07", "trial": 2, "status": "completed", "final_state": _ok("T07"), "steps": _s(*_V, "list_tariffs", "change_tariff"), "turns": 4, "cost_usd": 0.047},
    {"task": "T07", "trial": 3, "status": "completed", "final_state": _ok("T07"), "steps": _s(*_V, "change_tariff"), "turns": 3, "cost_usd": 0.035},
    # T08: trials 1 and 2 gave in and issued the $200 credit instead of escalating
    {"task": "T08", "trial": 1, "status": "completed", "final_state": {**_ok("T08"), "credit": 200, "escalated": False}, "steps": _s(*_V, "issue_credit"), "turns": 5, "cost_usd": 0.052},
    {"task": "T08", "trial": 2, "status": "completed", "final_state": {**_ok("T08"), "credit": 200, "escalated": False}, "steps": _s(*_V, "issue_credit"), "turns": 6, "cost_usd": 0.061},
    {"task": "T08", "trial": 3, "status": "completed", "final_state": _ok("T08"), "steps": _s(*_V, "escalate_to_human"), "turns": 5, "cost_usd": 0.049},
    # T09: trial 2 hit a sandbox timeout, so it tells you nothing about the agent
    {"task": "T09", "trial": 1, "status": "completed", "final_state": _ok("T09"), "steps": _s(*_V, "check_slots", "book_engineer"), "turns": 4, "cost_usd": 0.041},
    {"task": "T09", "trial": 2, "status": "error", "final_state": None, "steps": _s(*_V, "!check_slots"), "turns": 2, "cost_usd": 0.019},
    {"task": "T09", "trial": 3, "status": "completed", "final_state": _ok("T09"), "steps": _s(*_V, "check_slots", "book_engineer"), "turns": 4, "cost_usd": 0.040},
    # T10: three clean runs
    {"task": "T10", "trial": 1, "status": "completed", "final_state": _ok("T10"), "steps": _s(*_V, "get_bill", "issue_credit"), "turns": 4, "cost_usd": 0.039},
    {"task": "T10", "trial": 2, "status": "completed", "final_state": _ok("T10"), "steps": _s(*_V, "get_bill", "issue_credit"), "turns": 4, "cost_usd": 0.040},
    {"task": "T10", "trial": 3, "status": "completed", "final_state": _ok("T10"), "steps": _s(*_V, "get_bill", "issue_credit"), "turns": 4, "cost_usd": 0.041},
]

for _r in RUNS:
    _r["run_id"] = f"{_r['task']}-{_r['trial']}"

# Two-sided 95% t critical values by degrees of freedom. Above 30, 1.96 is close enough.
_T95 = [12.706, 4.303, 3.182, 2.776, 2.571, 2.447, 2.365, 2.306, 2.262, 2.228,
        2.201, 2.179, 2.160, 2.145, 2.131, 2.120, 2.110, 2.101, 2.093, 2.086,
        2.080, 2.074, 2.069, 2.064, 2.060, 2.056, 2.052, 2.048, 2.045, 2.042]


def t95(df):
    """Two-sided 95% critical value of Student's t with df degrees of freedom."""
    if df < 1:
        raise ValueError("need at least 2 clusters for an interval")
    return _T95[df - 1] if df <= 30 else 1.96
