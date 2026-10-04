---
title: "Exercise: Build a Retention Table"
type: exercise
minutes: 35
hints:
  - "Q_FIRST_VISIT: a CTE with `ROW_NUMBER() OVER (PARTITION BY member_id ORDER BY visited_at, id) AS n`, then `WHERE n = 1 ORDER BY member_id`."
  - "Q_REVENUE_GROWTH: first a CTE `monthly` with month and `ROUND(SUM(amount), 2) AS revenue`, then `LAG(revenue) OVER (ORDER BY month)` in the outer query."
  - "For pct_change, `ROUND(100.0 * (revenue - prev_revenue) / prev_revenue, 1)` is automatically NULL when prev_revenue is NULL."
  - "Q_SIGNUPS: group members by `strftime('%Y-%m', joined_on)` in a CTE, then `SUM(new_members) OVER (ORDER BY month)`."
  - "`month_offset`: split with `int(a[:4]), int(a[5:7])`, then `(y2 - y1) * 12 + (m2 - m1)`."
  - "In `retention_table`, query DISTINCT member_id, join month and visit month. Count cohort sizes from `members` (members with no visits still count in the denominator!)."
---

Pinecrest's COO wants to know: **are new members sticking around longer than they used to?** That's a cohort retention question. Along the way you'll also build three window-function queries the team asked for.

## Your task

**Q_FIRST_VISIT**: each member's first visit.
Columns: `member_id`, `first_visit` (the `visited_at` value), `location_id` (where that first visit happened). Use `ROW_NUMBER()`; break ties by visit `id`. Order by `member_id`. Members who never visited don't appear.

**Q_REVENUE_GROWTH**: month-over-month revenue.
Columns: `month`, `revenue` (rounded to 2), `prev_revenue` (the previous month's revenue, `NULL` for the first month), `pct_change` (rounded to 1, `NULL` for the first month). All months, in order.

**Q_SIGNUPS**: new and cumulative members.
Columns: `month` (from `joined_on`), `new_members`, `total_members` (running total). In order.

**`month_offset(a, b)`**: months from `"YYYY-MM"` string `a` to `b`. `month_offset("2025-11", "2026-02")` → `3`.

**`retention_table(con, last_month="2026-03")`** returns a dict:

```python
{
    "2025-10": {"size": 14, "pct": [93, 79, 64, 57, 50, 43]},
    "2025-11": {"size": 18, "pct": [...]},
    ...
}
```

- A member's **cohort** is the month they joined (`joined_on`).
- A member is **active in a month** if they have at least one visit in it.
- `size` is the number of members in the cohort, **including members who never visited**.
- `pct[k]` is the percentage of the cohort active in the month `k` months after their join month, `round(100 × active ÷ size)` as an integer, for every `k` from 0 up to `last_month`.

(The numbers in the example above are illustrative; your table will show Pinecrest's real ones.)

Press **Run** to print all three queries and the retention triangle, then **Submit**.
