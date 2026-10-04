---
title: "Exercise: Scope the Engagement"
type: exercise
minutes: 40
hints:
  - "`baseline`: count distinct dates for `per_day`; use `statistics.median` for the median and nearest rank (`sorted_values[math.ceil(0.9 * n) - 1]`) for p90."
  - "Booleans add up like numbers: `sum(h[\"breached\"] for h in history) / len(history)`. Group by tier with `setdefault(tier, []).append(breached)`."
  - "`prioritize`: sort the optional asks with `key=lambda a: (-a[\"value\"] / a[\"effort_days\"], a[\"effort_days\"], a[\"id\"])`, then add each one that still fits. Skip asks that don't fit and keep going."
  - "`success_metrics` targets: half the median handling time (`round(x * 0.5, 1)`), half the breach rate (`round(x / 2, 3)`), and an automation rate of 0.4 from a baseline of 0.0."
  - "`draft_brief`: put `json.dumps(facts, indent=2, sort_keys=True)` between `<engagement_facts>` tags, pass `output_config` with the schema, and raise `RuntimeError` on a refusal."
---

First deliverable: a scoped plan the sponsor can sign. You'll measure where NorthStar is today, decide what fits in 20 days, set measurable targets, and have Claude draft the brief from **your** numbers.

Data: `northstar.EXCEPTION_HISTORY` (30 days of handled exceptions) and `northstar.ASKS` (every stakeholder request from discovery). `BRIEF_SCHEMA` and `BUDGET_DAYS = 20` are given.

## Your task

**1. `baseline(history)`** returns:

```python
{"per_day": 39.8,                 # exceptions per distinct date, 1 decimal
 "median_handle_minutes": 25,     # statistics.median of handle_minutes
 "p90_handle_minutes": 63,        # nearest rank: sorted[ceil(0.9 * n) - 1]
 "ops_hours_per_day": 20.4,       # total handle_minutes / days / 60, 1 decimal
 "breach_rate": 0.207,            # share with breached True, 3 decimals
 "breach_rate_by_tier": {"platinum": 0.39, ...},   # 3 decimals
 "by_type": {"DELAY": 567, ...}}  # count per type
```

**2. `prioritize(asks, budget_days)`**:
- Every `must_have` ask is in scope, in list order. If together they exceed the budget, raise `ValueError("must-haves need 13 days but the budget is 10")`.
- Then consider the other asks from best to worst **value per day** (`value / effort_days`). Break ties with the smaller `effort_days`, then the `id`. Add each one that still fits the remaining budget; skip the ones that don't.
- Return `{"in_scope": [ids in the order added], "out_of_scope": [sorted ids], "days_used": n, "days_left": n}`.

**3. `success_metrics(base)`** returns three targets:

```python
[{"metric": "median_handle_minutes", "baseline": 25, "target": 12.5},    # half, 1 decimal
 {"metric": "sla_breach_rate", "baseline": 0.207, "target": 0.103},      # half, 3 decimals
 {"metric": "automation_rate", "baseline": 0.0, "target": 0.4}]
```

**4. `draft_brief(client, facts)`** asks Claude to draft the brief:
- `model=MODEL`, `max_tokens` ≥ 1024, and `output_config` with `effort: "medium"` and the `BRIEF_SCHEMA` JSON format.
- One user message containing `json.dumps(facts, indent=2, sort_keys=True)` between `<engagement_facts>` and `</engagement_facts>` tags, with an instruction to use only those numbers.
- Return the parsed dict. On a refusal, raise `RuntimeError`.

Press **Run** to see the baseline, the scope decision and the draft brief, then **Submit**. Which out-of-scope ask will be hardest to say no to, and how would you phrase it?
