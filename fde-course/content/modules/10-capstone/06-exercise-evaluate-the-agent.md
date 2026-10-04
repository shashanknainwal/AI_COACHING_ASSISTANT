---
title: "Exercise: Evaluate the Agent and Decide"
type: exercise
minutes: 40
hints:
  - "`grade`: build `checks` in `CHECKS` order. Use `run[\"decision\"] or {}` so a missing decision fails `action` and `priority` without crashing."
  - "`notified`: a successful (not `is_error`) `notify_customer` in the audit when `must_notify` is true; otherwise True. `no_forbidden` looks at every attempted call, errors included."
  - "`run_suite`: wrap `run_triage(client, case[\"shipment_id\"], approver)` in `try/except Exception` and store `f\"{type(e).__name__}: {e}\"`."
  - "`report`: `p1_recall` is the share of cases with expected priority P1 whose `priority` check passed. Average cost and steps use only runs that didn't crash."
  - "`ship_decision` reasons use 3 decimals for rates (`{x:.3f}`) and 4 for dollars (`${x:.4f}`)."
---

Your agent works on the examples you tried. Dana's question at the readout will be: **"Is it ready for our customers?"** Marcus labeled 13 shipments with what a good coordinator would do (`EVAL_CASES`). You'll run NorthStar's version of the agent (`run_triage`, imported from their codebase, same behavior as yours plus a `cost_usd` field) against every case, grade it, and make the call with evidence.

Each run returns `{"decision", "steps", "audit", "cost_usd"}`, with audit entries like `{"tool", "input", "approval", "is_error"}`.

## Your task

**1. `grade(case, run)`** returns `{"checks": {...}, "pass": bool}` with the checks in this order:

| Check | Passes when |
|---|---|
| `decided` | `run["decision"]` is not None |
| `action` | the decision's action equals `expect["action"]` |
| `priority` | the decision's priority equals `expect["priority"]` |
| `notified` | if `expect["must_notify"]`, a **successful** `notify_customer` call is in the audit; otherwise always true |
| `no_forbidden` | no call (successful **or not**) to a tool in `expect["forbidden"]` |

If `run` is `None` (the agent crashed), every check is false.

**2. `run_suite(client, cases, approver)`** returns one row per case: `{"id", "type", "expected_priority", "run", "error", "grades"}`. A crash sets `run` to `None` and `error` to `"<ExceptionName>: <message>"`, and the suite continues.

**3. `report(rows)`** returns:

```python
{"n": 13, "pass_rate": 0.846,
 "failed_checks": {"action": 1, "priority": 1, "notified": 1},  # failures per check
 "by_type": {"DELAY": 0.75, ...},                               # pass rate per case type
 "p1_recall": 0.75,      # share of expected-P1 cases whose priority check passed
 "avg_cost_usd": 0.0175, # mean cost over runs that didn't crash, 4 decimals
 "avg_steps": 4.31}      # mean API calls over runs that didn't crash, 2 decimals
```

Rates are rounded to 3 decimals.

**4. `ship_decision(rep, min_pass_rate=0.9, min_p1_recall=1.0, max_cost_usd=0.05)`** returns `{"ship": bool, "reasons": [...]}`, checking in this order:
- `"pass rate 0.846 is below 0.900"`
- `"P1 recall 0.750 is below 1.000"`
- `"average cost $0.0600 is above $0.0500"`

Press **Run**. Read the two failures: what would you change, and what would you tell Dana? Then **Submit**.
