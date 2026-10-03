---
title: "Exercise: Build a Stakeholder Engagement Plan"
type: exercise
minutes: 20
hints:
  - "In `quadrant`, check the high/high case first: `if s[\"influence\"] >= 3 and s[\"interest\"] >= 3: return \"manage closely\"`."
  - "For sorting, give each quadrant a rank with `QUADRANT_ORDER.index(q)`. Then sort with a key tuple: `(rank, -influence, name)`."
  - "Build each plan entry as `{\"name\": ..., \"quadrant\": q, \"cadence\": CADENCE[q]}`."
  - "In `risks`, collect the set of roles first: `roles = {s[\"role\"] for s in stakeholders}`."
  - "The skeptic check is `s[\"stance\"] == \"skeptic\" and s[\"influence\"] >= 4`. Keep skeptics in the same order as the input list."
  - "For the sponsor-stance risk, look at every stakeholder whose role is \"sponsor\". If any of them isn't a \"supporter\", add the risk once."
---

You're three days into the **Lumen Insurance** engagement. You've met everyone and rated them. Now you need two things for your Friday planning:

1. **An engagement plan:** who to engage, how often, and in what priority order.
2. **A risk list:** the stakeholder problems you need to act on this week.

## The data

Each stakeholder is a dictionary:

```python
{
    "name": "Ravi Shah",
    "title": "CISO",
    "influence": 5,          # 1-5
    "interest": 2,           # 1-5
    "stance": "skeptic",     # "supporter" | "neutral" | "skeptic"
    "role": "gatekeeper",    # "sponsor" | "champion" | "user" | "gatekeeper" | None
}
```

## Your task

**1. `quadrant(s)`** returns the stakeholder's quadrant:

| Influence | Interest | Quadrant |
|---|---|---|
| ≥ 3 | ≥ 3 | `"manage closely"` |
| ≥ 3 | < 3 | `"keep satisfied"` |
| < 3 | ≥ 3 | `"keep informed"` |
| < 3 | < 3 | `"monitor"` |

**2. `engagement_plan(stakeholders)`** returns a list of dictionaries `{"name", "quadrant", "cadence"}`:
- `cadence` comes from the `CADENCE` dictionary in the starter code.
- Sort by quadrant priority (`QUADRANT_ORDER`: manage closely first, monitor last), then by **influence, highest first**, then by **name** alphabetically.

**3. `risks(stakeholders)`** returns a list of risk strings, in this order:
1. `"no sponsor"` if nobody has the role `"sponsor"`
2. `"no champion"` if nobody has the role `"champion"`
3. `"sponsor is not a supporter"` if any sponsor's stance isn't `"supporter"`
4. `"high-influence skeptic: <name>"` for **each** skeptic with influence ≥ 4, in input order

A healthy engagement returns `[]`.

Press **Run** to see the plan for Lumen Insurance, then **Submit**.

> **FDE tip:** Paste the output of `risks()` at the top of your weekly internal notes. Each risk should have an owner and an action, like "Meet Ravi re: data flow, Tue."
