---
title: Safe Access to Production Data
type: reading
minutes: 6
---

> **By the end of this lesson you will be able to:**
> - Set up access that can't damage a customer's production system
> - Explain SQL injection with a concrete example and prevent it
> - Query large tables without slowing the customer's application
> - Handle personal data (PII) in queries, logs and screenshots

Pinecrest's IT lead will only widen your access beyond the copy if Tom can promise his board that nothing you run can break the live member app or leak member data.

## Layer 1: access that can't do damage

| Practice | Why |
|---|---|
| **Read replica**, not the primary | Heavy queries can't slow the live app |
| **Read-only database user** | The database itself rejects a mistaken `UPDATE` |
| **Least privilege** | Only the schemas you need |
| **Credentials per person or service** | Audit logs show who ran what |
| **Time-boxed access** | Removed when the phase ends |

Ask precisely: *"read-only user on the reporting replica, schemas `membership` and `billing`, for the 12-week pilot"* gets approved far faster than "can I have database access?" Inside a session: SQLite `PRAGMA query_only = ON`; Postgres `SET default_transaction_read_only = on`.

## Layer 2: guardrails in your own tools

- **Allow only a single `SELECT`** (or `WITH ... SELECT`). Strip comments first, then reject write and schema keywords.
- **Always limit rows:** `SELECT * FROM (<query>) LIMIT 1000`.
- **Set a timeout** (Postgres: `SET statement_timeout = '30s'`).

Keyword checks are a safety net, not a replacement for a read-only user: odd syntax can fool them, and they sometimes block harmless text like `'drop off'`.

## SQL injection, concretely

```python
def find_member(con, email):
    return con.execute(f"SELECT * FROM members WHERE email = '{email}'").fetchall()
```

Pass the "email" `x' OR '1'='1` and the query becomes:

```sql
SELECT * FROM members WHERE email = 'x' OR '1'='1'
```

which returns **every member**. Where multiple statements are allowed, `x'; DROP TABLE members; --` is worse. The fix, everywhere:

```python
con.execute("SELECT * FROM members WHERE email = ?", (email,))
```

The value is never interpreted as SQL, and no hand-written escaping is as safe. When Claude turns a user's chat message into a query value, that value is still untrusted input.

## Querying big tables politely

- `COUNT(*)` or table statistics first; `LIMIT` while exploring.
- Filter on indexed columns (IDs, timestamps); check with `EXPLAIN`.
- Sample: `TABLESAMPLE`, or `WHERE id % 100 = 0`.
- Run heavy jobs off-peak and warn the customer first.
- Never `UPDATE` or `DELETE` unless it's your job; then use a transaction, test the `WHERE` as a `SELECT`, take a backup, and get a second reviewer.

## Personal data (PII)

- **Select only needed columns.** `SELECT *` pulls PII into notebooks and logs.
- **Mask by default:** `m***@example.com`, `***-***-1234`; unmasked access is a deliberate exception.
- **Aggregate** when counts answer the question.
- **No real customer data** in slides, tickets or screenshots.
- **Follow the customer's policies** and laws like GDPR or HIPAA; ask the security team you mapped in Module 2.

> **Key takeaways**
> - Layer 1: read replica, read-only user, least privilege, time-boxed access.
> - Layer 2: single SELECT only, comments stripped, rows limited, timeouts set.
> - Always use parameters, especially for user or LLM input.
> - Select only needed columns, mask PII, aggregate where possible.
