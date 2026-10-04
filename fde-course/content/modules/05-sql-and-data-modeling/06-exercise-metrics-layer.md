---
title: "Exercise: Build a Metrics Layer with SQL Views"
type: exercise
minutes: 30
hints:
  - "`VIEWS_SQL` is a script with three `CREATE VIEW ... AS SELECT ...;` statements, separated by semicolons. Later views can select from earlier ones."
  - "Visits view: `FROM visits v JOIN locations l ON l.id = v.location_id`, group by `l.name` and `strftime('%Y-%m', v.visited_at)`. `COUNT(DISTINCT v.member_id)` counts unique visitors."
  - "Revenue view: payments → members → locations via `home_location_id`. `ROUND(SUM(p.amount), 2)`."
  - "KPI view: `FROM v_location_monthly_revenue r LEFT JOIN v_location_monthly_visits v ON v.location = r.location AND v.month = r.month`."
  - "`ROUND(r.revenue / NULLIF(v.unique_visitors, 0), 2)` avoids dividing by zero. A missing visits row gives NULL visitors, so the result is NULL too."
  - "`kpi`: `con.row_factory` is optional. Execute with parameters, `fetchone()`, and build a dict from `cur.description` and the row."
---

Pinecrest's dashboards, weekly email, and soon the AI assistant all need the same monthly numbers per location. Today three people compute them three ways. You'll build the metrics layer: three SQL views that define the numbers once.

## Your task

Write **`VIEWS_SQL`**, a SQL script (run with `con.executescript`) that creates three views:

**1. `v_location_monthly_visits`**
Columns: `location`, `month`, `visits`, `unique_visitors`.
Grain: one row per location (where the visit happened) per month with visits.

**2. `v_location_monthly_revenue`**
Columns: `location`, `month`, `revenue` (rounded to 2).
Grain: one row per **home location** of the paying member, per month with payments.

**3. `v_location_kpis`**
Columns: `location`, `month`, `revenue`, `visits`, `unique_visitors`, `revenue_per_visitor`.
- One row per row of `v_location_monthly_revenue`, with that location-month's visits (or `NULL` if there were none).
- `revenue_per_visitor = ROUND(revenue / unique_visitors, 2)`, or `NULL` when there are no visitors. Use `NULLIF` so it never divides by zero.
- **Build it from the two views**, not from the raw tables: that's how you avoid the payments × visits fan-out.

Then write **`kpi(con, location, month)`**, which returns that location-month's row from `v_location_kpis` as a dict (column name → value), or `None` if there's no row. Use query parameters.

Press **Run** to create the views and print the KPI table, then **Submit**. The tests also check that total revenue in your KPI view exactly equals total payments: no fan-out allowed.
