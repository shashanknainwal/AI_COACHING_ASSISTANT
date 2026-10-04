---
title: "SQL Refresher for FDEs (sqlite3 in Python)"
type: reading
minutes: 18
---

> **By the end of this lesson you will be able to:**
> - Explore an unfamiliar database's schema in minutes
> - Write the five query shapes that answer most executive questions
> - Avoid the NULL and join mistakes that produce confidently wrong numbers
> - Run SQL from Python safely with parameters

## Why SQL is still the FDE's most-used language

Most customer data that matters lives in a relational database: the CRM, the billing system, the product's own Postgres, a Snowflake or BigQuery warehouse. When the VP asks "which locations are losing members?", the fastest honest answer is usually a SQL query. FDEs who are fluent in SQL answer in ten minutes what others answer in a week.

## Meet Pinecrest Fitness

**Pinecrest Fitness** runs four gyms. They're piloting your company's AI member-retention assistant, but first their COO wants a few straight answers from their membership database. You have read access to a copy of it:

```
locations      (id, name, city, opened_on)
plans          (id, name, monthly_price)
members        (id, first_name, last_name, email, phone, home_location_id, joined_on)
subscriptions  (id, member_id, plan_id, start_date, end_date, status)
payments       (id, member_id, amount, paid_on)
visits         (id, member_id, location_id, visited_at)
```

Every exercise in this module uses this database. In the course, it's an in-memory SQLite copy loaded with `pinecrest.connect()`.

## Exploring a schema you've never seen

Before writing any query, look around:

```sql
-- SQLite: list tables and their CREATE statements
SELECT name, sql FROM sqlite_master WHERE type = 'table';

-- Columns of one table
PRAGMA table_info(members);

-- Row counts tell you a lot
SELECT COUNT(*) FROM visits;

-- And always look at actual rows
SELECT * FROM subscriptions LIMIT 5;
```

On Postgres the equivalent is `information_schema.columns`; on Snowflake and BigQuery, the `INFORMATION_SCHEMA` views. The habit is the same everywhere: **schema, counts, sample rows, then queries.**

## The five query shapes

Most business questions are one of these five shapes.

**1. Filter and sort:** "Show me cancelled subscriptions, newest first."

```sql
SELECT member_id, end_date
FROM subscriptions
WHERE status = 'cancelled'
ORDER BY end_date DESC;
```

**2. Aggregate by group:** "How many active members per location?"

```sql
SELECT l.name, COUNT(*) AS active_members
FROM subscriptions s
JOIN members m   ON m.id = s.member_id
JOIN locations l ON l.id = m.home_location_id
WHERE s.status = 'active'
GROUP BY l.name
ORDER BY active_members DESC;
```

**3. Filter on an aggregate (HAVING):** "Which locations had fewer than 500 visits in March?"

```sql
SELECT location_id, COUNT(*) AS visits
FROM visits
WHERE visited_at >= '2026-03-01' AND visited_at < '2026-04-01'
GROUP BY location_id
HAVING COUNT(*) < 500;
```

`WHERE` filters rows *before* grouping; `HAVING` filters groups *after*.

**4. Find what's missing (anti-join):** "Which members have never visited?"

```sql
SELECT m.id, m.first_name, m.last_name
FROM members m
LEFT JOIN visits v ON v.member_id = m.id
WHERE v.id IS NULL;
```

A `LEFT JOIN` keeps every member; members with no visits get `NULL` in the visit columns. Filtering on `IS NULL` keeps exactly those.

**5. Bucket by time:** "Revenue by month."

```sql
SELECT strftime('%Y-%m', paid_on) AS month, ROUND(SUM(amount), 2) AS revenue
FROM payments
GROUP BY month
ORDER BY month;
```

Date functions differ between databases (`strftime` in SQLite, `date_trunc('month', ...)` in Postgres and Snowflake), but the idea is identical.

## NULL: where wrong numbers come from

`NULL` means "unknown," and it behaves differently from every other value:

| Expression | Result | Why |
|---|---|---|
| `NULL = NULL` | `NULL` (not true!) | Unknown compared to unknown is unknown |
| `WHERE end_date = NULL` | Matches nothing | Use `WHERE end_date IS NULL` |
| `COUNT(*)` | Counts rows | Including rows with NULLs |
| `COUNT(email)` | Counts non-NULL emails | Silently skips NULLs |
| `AVG(rating)` | Average of non-NULL values | NULLs are excluded, not treated as 0 |
| `col <> 'x'` | Excludes rows where col is NULL | Surprises everyone once |

When a number looks off, check how NULLs are being handled. `COUNT(*)` vs `COUNT(column)` alone causes a surprising number of wrong dashboards.

## The join that multiplies your numbers

You saw fan-out in Module 3; SQL makes it even easier to do by accident:

```sql
-- WRONG: revenue per location, joined to visits too
SELECT m.home_location_id, SUM(p.amount)
FROM members m
JOIN payments p ON p.member_id = m.id
JOIN visits v   ON v.member_id = m.id     -- each payment now repeats once per visit!
GROUP BY m.home_location_id;
```

Each payment row is repeated once for every visit by the same member, so revenue is multiplied. Rule: **aggregate each fact table separately (in a subquery or CTE), then join the aggregates.** You'll practice this when you build a metrics layer.

## Running SQL from Python

The standard library's `sqlite3` module (and the Postgres driver `psycopg`, which has the same shape) works like this:

```python
from fde_datasets import pinecrest

con = pinecrest.connect()
cur = con.execute(
    "SELECT name, monthly_price FROM plans WHERE monthly_price > ? ORDER BY monthly_price",
    (40,),
)
print(cur.fetchall())        # [('Plus', 49.0), ('Premium', 79.0)]
```

**Always pass values as parameters (`?`), never with f-strings.** Building SQL with string formatting opens the door to SQL injection, and you'll see exactly how in the safety lesson. Parameters also handle quoting for you.

Two conveniences:

- `cur.description` gives column names: `[d[0] for d in cur.description]`.
- `con.row_factory = sqlite3.Row` makes rows accessible by column name: `row["name"]`.

**Try it:** the scratchpad on the right connects to Pinecrest and explores the schema. Run it, then write a query for the number of members per plan.

> **Key takeaways**
> - Explore first: schema, row counts, sample rows.
> - Five shapes answer most questions: filter/sort, group, HAVING, anti-join, time bucket.
> - NULL is "unknown": use `IS NULL`, and know the difference between `COUNT(*)` and `COUNT(col)`.
> - Aggregate fact tables separately before joining, and always use query parameters.
