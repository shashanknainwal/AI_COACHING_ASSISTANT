---
title: "SQL Refresher for FDEs (sqlite3 in Python)"
type: reading
minutes: 6
---

> **By the end of this lesson you will be able to:**
> - Explore an unfamiliar schema in minutes
> - Write the five query shapes behind most executive questions
> - Avoid the NULL and join mistakes that produce confidently wrong numbers
> - Run SQL from Python with parameters

Tom Haddad, COO of **Pinecrest Fitness** (four gyms), wants straight answers from his membership database before he trusts your AI retention pilot. You have read access to a copy, and he'll ask how you got every number.

```
locations      (id, name, city, opened_on)
plans          (id, name, monthly_price)
members        (id, first_name, last_name, email, phone, home_location_id, joined_on)
subscriptions  (id, member_id, plan_id, start_date, end_date, status)
payments       (id, member_id, amount, paid_on)
visits         (id, member_id, location_id, visited_at)
```

Every exercise uses it via `pinecrest.connect()`.

## Explore first: schema, counts, sample rows

```sql
SELECT name, sql FROM sqlite_master WHERE type = 'table';  -- tables
PRAGMA table_info(members);                                 -- columns
SELECT COUNT(*) FROM visits;                                -- size
SELECT * FROM subscriptions LIMIT 5;                        -- real rows
```

Elsewhere, use `information_schema`. Docs are often wrong; real rows aren't.

## The five query shapes

**1. Filter and sort:** `WHERE status = 'cancelled' ORDER BY end_date DESC`.

**2. Aggregate by group:** active members per location.

```sql
SELECT l.name, COUNT(*) AS active_members
FROM subscriptions s
JOIN members m   ON m.id = s.member_id
JOIN locations l ON l.id = m.home_location_id
WHERE s.status = 'active'
GROUP BY l.name
ORDER BY active_members DESC;
```

**3. Filter on an aggregate:** locations with fewer than 500 visits in March.

```sql
SELECT location_id, COUNT(*) AS visits
FROM visits
WHERE visited_at >= '2026-03-01' AND visited_at < '2026-04-01'
GROUP BY location_id
HAVING COUNT(*) < 500;
```

`WHERE` filters rows *before* grouping; `HAVING` filters groups *after*.

**4. Anti-join:** members who have never visited.

```sql
SELECT m.id, m.first_name, m.last_name
FROM members m
LEFT JOIN visits v ON v.member_id = m.id
WHERE v.id IS NULL;
```

Unmatched members get `NULL` on the visits side.

**5. Bucket by time:** revenue by month.

```sql
SELECT strftime('%Y-%m', paid_on) AS month, ROUND(SUM(amount), 2) AS revenue
FROM payments GROUP BY month ORDER BY month;
```

Postgres and Snowflake use `date_trunc('month', ...)`.

## NULL: where wrong numbers come from

`NULL` means "unknown":

| Expression | Result |
|---|---|
| `NULL = NULL` | `NULL`, not true |
| `WHERE end_date = NULL` | Matches nothing; use `IS NULL` |
| `COUNT(*)` vs `COUNT(email)` | All rows vs non-NULL emails only |
| `AVG(rating)` | NULLs excluded, not treated as 0 |
| `col <> 'x'` | Also drops rows where col is NULL |

## The join that multiplies your numbers

```sql
-- WRONG: each payment repeats once per visit by the same member
SELECT m.home_location_id, SUM(p.amount)
FROM members m
JOIN payments p ON p.member_id = m.id
JOIN visits v   ON v.member_id = m.id
GROUP BY m.home_location_id;
```

This is fan-out. **Aggregate each fact table separately (in a CTE), then join the aggregates.**

## Running SQL from Python

```python
from fde_datasets import pinecrest

con = pinecrest.connect()
cur = con.execute(
    "SELECT name, monthly_price FROM plans WHERE monthly_price > ? ORDER BY monthly_price",
    (40,),
)
print(cur.fetchall())        # [('Plus', 49.0), ('Premium', 79.0)]
```

**Pass values as `?` parameters, never with f-strings.** That prevents SQL injection (lesson 7). `[d[0] for d in cur.description]` gives column names; `con.row_factory = sqlite3.Row` lets you write `row["name"]`.

**Try it:** run the scratchpad on the right, then write a query for the number of members per plan.

> **Key takeaways**
> - Schema, row counts, sample rows, then queries.
> - Five shapes: filter/sort, group, HAVING, anti-join, time bucket.
> - Use `IS NULL`; know `COUNT(*)` from `COUNT(col)`.
> - Aggregate fact tables separately before joining; always use parameters.
