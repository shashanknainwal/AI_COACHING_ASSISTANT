---
title: "Window Functions, Deduping, and Cohorts"
type: reading
minutes: 6
---

> **By the end of this lesson you will be able to:**
> - Explain how a window function differs from `GROUP BY`
> - Use `ROW_NUMBER`, `LAG` and running `SUM` for "first," "previous" and "so far" questions
> - Pick the latest record per key
> - Build a cohort retention table and explain it to an executive

Tom wants to know whether new Pinecrest members stick around longer than they used to, and where each member first checked in. Window functions answer both.

## GROUP BY collapses; windows don't

```sql
-- Every visit row, with that member's visit count alongside
SELECT member_id, visited_at,
       COUNT(*) OVER (PARTITION BY member_id) AS member_visits
FROM visits;
```

`PARTITION BY` groups rows without collapsing them; `ORDER BY` inside `OVER` orders each partition.

## The window functions you'll use most

**`ROW_NUMBER()`: first, last, latest.** Number rows per partition in a CTE, then keep `n = 1`:

```sql
WITH ranked AS (
    SELECT member_id, visited_at, location_id,
           ROW_NUMBER() OVER (PARTITION BY member_id ORDER BY visited_at) AS n
    FROM visits
)
SELECT member_id, visited_at AS first_visit, location_id
FROM ranked
WHERE n = 1;
```

Order by `visited_at DESC` for the **latest** row per key: the standard dedup for history tables. `MIN(visited_at)` gives the date but not the other columns of that row, like the location; `ROW_NUMBER` keeps the whole row.

**`RANK()` / `DENSE_RANK()`: ties.** `RANK` gives 1, 1, 3; `DENSE_RANK` gives 1, 1, 2.

**`LAG()` / `LEAD()`: previous or next row.**

```sql
WITH monthly AS (
    SELECT strftime('%Y-%m', paid_on) AS month, SUM(amount) AS revenue
    FROM payments GROUP BY month
)
SELECT month, revenue,
       LAG(revenue) OVER (ORDER BY month) AS prev_revenue
FROM monthly;
```

Growth is `100.0 * (revenue - prev_revenue) / prev_revenue`. For the first month `LAG` is `NULL`, so growth is `NULL`: correct, since there's nothing to compare against.

**`SUM() OVER (ORDER BY ...)`: running totals.** `SUM(new_members) OVER (ORDER BY month)` adds all earlier rows to each row.

**CTEs** (`WITH a AS (...), b AS (...)`) let you build long queries in small steps you can run alone. A window function can't go in `WHERE`; compute it in a CTE, then filter.

## Cohort retention

A **cohort** is the customers who started in the same period. A retention table shows the share still active N months later:

```
cohort    size   month 0   month 1   month 2   month 3
2025-10     14      93%       79%       64%       57%
2025-11     18      89%       83%       72%
2025-12     22      91%       77%
2026-01     25      88%
```

- Read **across** a row: how one cohort decays.
- Read **down** a column: whether newer cohorts retain better than older ones at the same age. This is how you tell if an onboarding change worked.

To build it: (1) assign each member a cohort (join month); (2) find the months each member was active (for Pinecrest, months with a visit); (3) divide active members by cohort size per cohort and month offset, where offset is `(year2 − year1) × 12 + (month2 − month1)`. In the exercise you pull `(member, cohort, active_month)` rows with SQL and pivot in Python.

**Agree the definition of "active" with the customer.** "Had a visit" and "had a paid subscription" give very different numbers. Say which one you used.

> **Key takeaways**
> - Windows compute across rows without collapsing: `OVER (PARTITION BY ... ORDER BY ...)`.
> - `ROW_NUMBER` + a CTE filter picks the first or latest row per key.
> - `LAG` compares with the previous row; `SUM() OVER (ORDER BY ...)` is a running total.
> - Cohort tables: across for decay, down for improvement.
