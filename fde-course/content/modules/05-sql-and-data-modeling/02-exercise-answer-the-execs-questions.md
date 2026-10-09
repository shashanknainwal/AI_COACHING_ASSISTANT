---
title: "Exercise: Answer the COO's Five Questions"
type: exercise
minutes: 30
hints:
  - "Start every query from the table that holds the thing you're counting: subscriptions for members' status, payments for revenue, visits for visits."
  - "Q1: join `subscriptions → members → locations`, filter `status = 'active'`, `GROUP BY l.name`, `ORDER BY active_members DESC, l.name`."
  - "Q2: `strftime('%Y-%m', paid_on)` gives the month. Filter with `paid_on >= '2026-01-01' AND paid_on < '2026-04-01'`, and `ROUND(SUM(amount), 2)`."
  - "Q3: filter visits to March in `WHERE`, group by location name, then `HAVING COUNT(*) < 200`. Order by visits ascending."
  - "Q4: `FROM members m JOIN locations l ... LEFT JOIN visits v ON v.member_id = m.id WHERE v.id IS NULL`, then group by location."
  - "Q5: `SUM(s.status = 'cancelled')` counts cancellations in SQLite (a true comparison is 1). Multiply by `100.0` before dividing so you get decimals, and `ROUND(..., 1)`."
---

Pinecrest's COO, Tom Haddad, sent five questions before Thursday's leadership meeting. He wants numbers he can trust, and he's going to ask how you got them. Write one SQL query for each.

Each query is a Python string constant. The `run(con, sql)` helper (already written) executes it and returns a list of tuples. The tests check the **exact rows, columns and order**, so read each question's spec carefully.

## The questions

**Q1_ACTIVE_BY_LOCATION**: "How many active members does each location have?"
Columns: `location`, `active_members`. A member belongs to their **home location**. Count subscriptions with `status = 'active'`. Order by `active_members` descending, then `location`.

**Q2_MONTHLY_REVENUE**: "What was our revenue each month this quarter?"
Columns: `month` (`'YYYY-MM'`), `revenue` (sum of `payments.amount`, rounded to 2 decimals). Only January through March 2026. Order by month.

**Q3_QUIET_LOCATIONS**: "Which locations had fewer than 200 visits in March 2026?"
Columns: `location`, `visits`. Count visits by the **location where the visit happened** (`visits.location_id`). Order by `visits` ascending.

**Q4_NEVER_VISITED**: "How many members have never visited, per home location?"
Columns: `location`, `never_visited`. Only include locations with at least one such member. Order by `never_visited` descending, then `location`.

**Q5_CHURN_BY_LOCATION**: "Where are we losing members?"
Columns: `location`, `members` (all subscriptions), `cancelled`, `churn_pct` (`100 × cancelled ÷ members`, rounded to 1 decimal). One row per home location. Order by `churn_pct` descending.

Finally, **`biggest_churn_location(con)`** returns the name of the location with the highest churn, using your Q5 query.

Press **Run** to print all five answers. Read them together: what's the story you'd tell Tom? Then **Submit**.

> **The FDE habit:** when you send numbers to an executive, include the query (or a one-line definition) with each one. "Active = subscriptions with status active, by home location." It prevents a week of "your number doesn't match my dashboard" arguments.
