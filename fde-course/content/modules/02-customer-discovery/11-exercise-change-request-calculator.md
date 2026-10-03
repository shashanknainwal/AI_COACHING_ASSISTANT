---
title: "Exercise: Change-Request Impact Calculator"
type: exercise
minutes: 25
hints:
  - "`plan_load` is `sum(item[\"days\"] for item in items)`."
  - "Compare priorities by their position in `PRIORITY_ORDER`: a lower index means more important. `rank = PRIORITY_ORDER.index`."
  - "Check the cases in this order: accept (fits as-is), then defer (the change is \"could\"), then try a swap, and finally slip."
  - "Swap candidates are items whose rank is strictly greater than the change's rank. Sort them with `key=lambda i: (-rank(i[\"priority\"]), -i[\"days\"], i[\"id\"])` so the least important, largest items go first."
  - "Drop candidates one at a time, subtracting their days from the load, until `load + change[\"days\"] <= capacity`. If you run out of candidates and it still doesn't fit, the decision is \"slip\" with no drops."
  - "For `change_note`, build the swap message with `\", \".join(result[\"drop\"])`."
---

Lumen Insurance's phase 1 plan is full: 25 engineering days of work against 25 days of capacity. Requests keep arriving. You want every request to get the same fair, quick evaluation, plus a draft message for Joan, the sponsor, laying out the trade-off.

## The data

```python
PLAN = [
    {"id": "W1", "title": "Email + PDF ingestion", "days": 6, "priority": "must"},
    {"id": "W2", "title": "Pre-fill 8 core fields", "days": 8, "priority": "must"},
    {"id": "W3", "title": "Low-confidence highlighting", "days": 4, "priority": "should"},
    ...
]
CAPACITY = 25
change = {"id": "CR-3", "title": "Add commercial claims", "days": 6, "priority": "must"}
```

## Your task

**1. `plan_load(items)`** returns the total days in the plan.

**2. `evaluate_change(items, capacity, change)`** returns `{"decision": ..., "drop": [...], "slip_days": n}`. Apply these rules **in order**:

| # | Situation | Result |
|---|---|---|
| 1 | Load + change days ≤ capacity | `"accept"`, drop `[]`, slip `0` |
| 2 | Otherwise, if the change's priority is `"could"` | `"defer"`, drop `[]`, slip `0` |
| 3 | Otherwise, try to make room by dropping items with **strictly lower** priority than the change | `"swap"` with the dropped ids, slip `0` |
| 4 | If dropping every lower-priority item still isn't enough | `"slip"`, drop `[]`, slip = load + change days − capacity |

For the swap, drop candidates in this order: **least important priority first**, then **largest days first**, then **id**. Stop as soon as the change fits.

> **Why a simple rule?** This greedy approach doesn't always find the smallest possible set to drop. For CR-3 it drops W5, W6 and W3, although W5 and W3 alone would do. But it's predictable and easy to explain ("we cut the least important work first"), which matters more when you're making a recommendation to a sponsor. You can always offer a tighter alternative in your message.

**3. `change_note(change, result)`** returns a one-line message for the sponsor:

| Decision | Message |
|---|---|
| accept | `"CR-3 accepted: fits in current capacity."` |
| defer | `"CR-3 deferred to the next phase."` |
| swap | `"CR-3 fits if we defer: W5, W6, W3."` |
| slip | `"CR-3 adds 6 days; the deadline moves unless we cut scope."` |

(Use the change's actual id, the dropped ids in drop order, and the actual slip days.)

Press **Run** to evaluate three real requests against the Lumen plan, then **Submit**.

> **FDE tip:** Never send the calculator's output as the decision. It's your *recommendation*. Send the options to the sponsor and let them choose; then record their decision.
