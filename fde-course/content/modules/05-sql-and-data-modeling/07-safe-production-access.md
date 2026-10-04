---
title: Safe Access to Production Data
type: reading
minutes: 15
---

> **By the end of this lesson you will be able to:**
> - Set up database access that can't damage a customer's production system
> - Explain SQL injection with a concrete example, and prevent it every time
> - Query large tables without slowing down the customer's application
> - Handle personal data (PII) responsibly in queries, logs, and screenshots

## Trust is the asset

Customers give FDEs access to their most sensitive systems. One accidental `DELETE` without a `WHERE`, one query that locks a table during peak hours, or one screenshot with customer emails in a slide deck, and that trust is gone, along with the deal. The habits in this lesson are what let security teams say yes to you quickly.

## Layer 1: access that can't do damage

Defense comes in layers. The strongest layer is the one that doesn't depend on you being careful:

| Practice | Why |
|---|---|
| **Read replica** instead of the primary database | Your heavy queries can't slow down the live application |
| **Read-only database user** | Even a mistaken `UPDATE` is rejected by the database itself |
| **Least privilege** | Only the schemas and tables you need; no access to, say, password hashes |
| **Separate credentials per person or service** | Audit logs show who ran what; access can be revoked individually |
| **Time-boxed access** | Remove access when the engagement or phase ends |

Ask for these during discovery. A request like *"read-only user on the reporting replica, schemas `membership` and `billing`, for the 12-week pilot"* gets approved much faster than "can I have database access?"

In SQLite you can even make a connection read-only from inside: `con.execute("PRAGMA query_only = ON")`. Postgres has `SET default_transaction_read_only = on` and read-only roles.

## Layer 2: guardrails in your own tools

When you build tools that run SQL (a notebook helper, an internal dashboard, a text-to-SQL assistant), add guardrails in code too:

- **Allow only read statements.** Reject anything that isn't a single `SELECT` (or `WITH ... SELECT`). Reject statements containing write or schema keywords. Strip comments first, since comments can hide things.
- **Always limit rows.** Wrap queries as `SELECT * FROM (<query>) LIMIT 1000`, so a forgotten filter doesn't pull ten million rows into memory.
- **Set a statement timeout** (Postgres: `SET statement_timeout = '30s'`) so a runaway query is cancelled automatically.

Keyword checks are a second layer, not a replacement for a read-only user. They can be fooled by unusual syntax, and they sometimes block harmless queries (like a `WHERE note = 'drop off'`). That's an acceptable trade-off for a safety net.

## SQL injection, concretely

Suppose a helper looks up a member by email, using an f-string:

```python
def find_member(con, email):
    return con.execute(f"SELECT * FROM members WHERE email = '{email}'").fetchall()
```

Now someone passes this "email":

```
x' OR '1'='1
```

The query becomes:

```sql
SELECT * FROM members WHERE email = 'x' OR '1'='1'
```

which returns **every member**. With a database that allows multiple statements, the input could even be `x'; DROP TABLE members; --`.

The fix is always the same, in every language and database: **parameters**.

```python
con.execute("SELECT * FROM members WHERE email = ?", (email,))
```

The database receives the SQL and the value separately and never interprets the value as SQL. There's no escaping function that's as safe as parameters; don't try to write one.

This matters even more when the input comes from an LLM. If a user can type into a chat box and Claude turns that into a query value, the user's text is untrusted input.

## Querying big tables politely

Production tables can be huge, and your query competes with the customer's live traffic.

- **Look before you scan.** `SELECT COUNT(*)` first, or check table statistics. Then `LIMIT` while exploring.
- **Filter on indexed columns,** usually IDs and timestamps. `EXPLAIN` (Postgres: `EXPLAIN ANALYZE`) shows whether the database will use an index or scan everything.
- **Sample** for exploration: `TABLESAMPLE` in Postgres and Snowflake, or `WHERE id % 100 = 0`.
- **Run heavy jobs off-peak,** and tell the customer before a big backfill.
- **Never** run `UPDATE` or `DELETE` on a customer database unless it's explicitly your job, and if it is: inside a transaction, with the `WHERE` clause tested as a `SELECT` first, after a backup, with a second person reviewing.

## Personal data (PII)

Membership data contains names, emails, phone numbers, sometimes health or payment information. Treat it carefully:

- **Select only the columns you need.** `SELECT *` pulls PII into your notebook, logs, and memory even when you only needed IDs and dates.
- **Mask in outputs:** `m***@example.com`, `***-***-1234`. Masking should be the default in any tool you build, with unmasked access as a deliberate exception.
- **Aggregate when you can.** Counts and averages usually answer the business question without exposing individuals.
- **Never put real customer data in slides, tickets, or screenshots.** Use masked or synthetic examples.
- **Follow the customer's policies** (and laws like GDPR or HIPAA where they apply) on where data may be stored and who may see it. When in doubt, ask the security team you mapped in Module 2.

In the next exercise you'll build a small safe-query helper with the layer-2 guardrails: read-only checks, automatic row limits, parameters, and PII masking.

> **Key takeaways**
> - Layer 1: read replica, read-only user, least privilege, time-boxed access.
> - Layer 2: allow only single SELECT statements, strip comments, always limit rows, set timeouts.
> - Always use query parameters; never build SQL with string formatting, especially from user or LLM input.
> - Select only needed columns, mask PII by default, aggregate where possible.
