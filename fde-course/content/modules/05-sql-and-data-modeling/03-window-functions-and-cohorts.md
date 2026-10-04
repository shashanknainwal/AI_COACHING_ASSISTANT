---
title: "Window Functions, Deduping, and Cohorts"
type: reading
minutes: 18
---

> **By the end of this lesson you will be able to:**
> - Explain how a window function differs from `GROUP BY`
> - Use `ROW_NUMBER`, `LAG`, and running `SUM` to answer "first," "previous," and "so far" questions
> - Pick the latest record per key, the most common dedup task in customer databases
> - Build a cohort retention table and explain it to an executive

## GROUP BY collapses; windows don't

`GROUP BY` turns many rows into one row per group. A **window function** computes something across a group of rows *while keeping every row*:

```sql
-- GROUP BY: one row per member
SELECT member_id, COUNT(*) FROM visits GROUP BY member_id;

-- Window: every visit row, plus that member's visit count alongside it
SELECT member_id, visited_at,
       COUNT(*) OVER (PARTITION BY member_id) AS member_visits
FROM visits;
```

The `OVER (...)` clause defines the window:

- `PARTITION BY` splits rows into groups (like `GROUP BY`, but without collapsing).
- `ORDER BY` inside `OVER` orders rows within each partition, which matters for "first," "previous," and "running" calculations.

Window functions work in SQLite, Postgres, Snowflake, BigQuery, and every modern warehouse.

## The four window functions you'll use most

### `ROW_NUMBER()`: first, last, latest

Number rows within each partition:

```sql
SELECT member_id, visited_at, location_id,
       ROW_NUMBER() OVER (PARTITION BY member_id ORDER BY visited_at) AS n
FROM visits;
```

Wrap it in a CTE and keep `n = 1` to get each member's **first** visit:

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

Order by `visited_at DESC` instead and you get the **latest** row per member. This "latest record per key" pattern is how you deduplicate customer tables that keep history: the latest address per customer, the current plan per subscription, the most recent status per ticket.

> Why not just `MIN(visited_at)`? `MIN` gives you the earliest date, but not the *other columns* of that row, like which location the first visit was at. `ROW_NUMBER` keeps the whole row.

### `RANK()` and `DENSE_RANK()`: leaderboards with ties

`RANK` gives tied rows the same number and skips the next (1, 1, 3); `DENSE_RANK` doesn't skip (1, 1, 2). Use them for "top 3 locations by visits," where ties matter.

### `LAG()` and `LEAD()`: compare to the previous or next row

```sql
WITH monthly AS (
    SELECT strftime('%Y-%m', paid_on) AS month, SUM(amount) AS revenue
    FROM payments GROUP BY month
)
SELECT month, revenue,
       LAG(revenue) OVER (ORDER BY month) AS prev_revenue
FROM monthly;
```

The first month has no previous row, so `LAG` returns `NULL`. Month-over-month growth is then `100.0 * (revenue - prev_revenue) / prev_revenue`, and it's also `NULL` for the first month, which is correct: there's no growth to report.

### `SUM() OVER (ORDER BY ...)`: running totals

```sql
SELECT month, new_members,
       SUM(new_members) OVER (ORDER BY month) AS total_members
FROM monthly_signups;
```

With an `ORDER BY` in the window, `SUM` becomes cumulative: each row's total includes all earlier rows.

## CTEs keep complex queries readable

`WITH name AS (...)` defines a named subquery (a **common table expression**) you can use like a table. Build complicated queries as a sequence of small, named steps:

```sql
WITH monthly AS (...),
     with_prev AS (SELECT ..., LAG(...) OVER (...) FROM monthly)
SELECT * FROM with_prev WHERE ...;
```

Each step can be run and checked on its own, which is how you debug a 60-line query without losing your mind. Note that you can't use a window function directly in `WHERE`; compute it in a CTE, then filter in the outer query.

## Cohort retention: the executive's favorite table

A **cohort** is a group of customers who started in the same period. A **retention table** shows what share of each cohort is still active N months later:

```
cohort    size   month 0   month 1   month 2   month 3
2025-10     14      93%       79%       64%       57%
2025-11     18      89%       83%       72%
2025-12     22      91%       77%
2026-01     25      88%
```

How to read it:

- **Rows** are signup months. **Columns** are months since signup.
- Read **across** a row to see how one cohort decays over time.
- Read **down** a column to see whether newer cohorts retain better or worse than older ones at the same age. That's how you tell whether a product change or a new onboarding program worked.
- The table is a **triangle** because recent cohorts haven't had time to reach later months.

Building one takes three steps:

1. Assign each member a cohort (their join month).
2. For each member, find the months in which they were active (for Pinecrest, months with at least one visit).
3. For each cohort and month offset, divide the number of active members by the cohort size.

Month offset is `(year2 − year1) × 12 + (month2 − month1)`. You can do every step in SQL, or (often clearer) pull the distinct `(member, cohort, active_month)` rows with SQL and pivot them in Python. That's what you'll do in the exercise.

**Define "active" with the customer.** "Had a visit" and "had a paid subscription" give very different retention numbers. Neither is wrong, but you must say which one you used.

> **Key takeaways**
> - Window functions compute across rows without collapsing them: `OVER (PARTITION BY ... ORDER BY ...)`.
> - `ROW_NUMBER` + a CTE filter picks the first or latest row per key, the standard dedup pattern.
> - `LAG` compares with the previous row; `SUM() OVER (ORDER BY ...)` gives running totals.
> - Cohort tables show retention by signup month; read across for decay and down for improvement.
