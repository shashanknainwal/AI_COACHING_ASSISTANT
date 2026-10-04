---
title: "Text-to-SQL with Claude, Safely"
type: reading
minutes: 15
---

> **By the end of this lesson you will be able to:**
> - Explain when text-to-SQL is a great fit and when it's the wrong tool
> - Give Claude the schema context it needs to write correct queries
> - Run generated SQL behind the guardrails from the last exercise
> - Evaluate a text-to-SQL feature before a customer relies on it

## The appeal

"Ask your data anything in plain English" is one of the most requested AI features in enterprise deployments. A Pinecrest manager types *"Which location had the most visits in March?"* and gets an answer without waiting for the data team. Claude is very good at writing SQL when it understands the schema.

It's also one of the easiest features to get subtly wrong. A plausible-looking query that double-counts revenue is worse than no answer, because people trust it.

## Good fit vs. wrong tool

| Good fit | Wrong tool |
|---|---|
| Exploratory questions by people who'll sanity-check the answer | Official metrics for board decks (use the metrics layer) |
| A clean, well-named schema or set of views | Hundreds of cryptic legacy tables |
| Read-only access to a replica | Anything that writes data |
| Users who can see the SQL and the result | Fully automated decisions with no human looking |

A strong pattern combines this with the previous lessons: point text-to-SQL at your **metrics-layer views** rather than raw tables. Then "revenue" always means the agreed definition.

## Giving Claude the right context

The model can only use tables and columns it knows about. Put the schema in the system prompt:

```text
You write SQLite queries for Pinecrest Fitness's reporting database.

Schema:
CREATE TABLE locations (id INTEGER PRIMARY KEY, name TEXT NOT NULL, ...);
CREATE TABLE visits (...);
CREATE VIEW v_location_kpis AS ...;

Rules:
- Write a single read-only SELECT query (SQLite dialect).
- Prefer the v_* views for revenue and visit metrics.
- "Active member" means a subscription with status = 'active'.
- If the question can't be answered from this schema, say so in the explanation and return SELECT NULL.
```

Things that measurably improve accuracy:

- **The real `CREATE` statements,** including views. Pull them from the database itself (`sqlite_master`, or `information_schema` elsewhere) so they never drift from reality.
- **Business definitions** for ambiguous terms ("active," "churn," "revenue").
- **The dialect.** SQLite, Postgres, Snowflake, and BigQuery differ in date functions and more.
- **A few sample values** for categorical columns (`status IN ('active', 'cancelled')`), so Claude doesn't guess `'Active'` or `'canceled'`.

The schema is long and identical on every request, so it's a perfect candidate for **prompt caching**, which makes repeated requests much cheaper once the prefix is cached.

## Getting structured output

Ask for both the SQL and an explanation, with structured outputs, so your code never has to dig a query out of prose:

```python
SQL_SCHEMA = {
    "type": "object",
    "properties": {"sql": {"type": "string"}, "explanation": {"type": "string"}},
    "required": ["sql", "explanation"],
    "additionalProperties": False,
}
```

Show the explanation and the SQL to the user next to the result. A manager who reads "counts visits by the location where they happened, in March 2026" can catch a misunderstanding before acting on it.

## Never execute without guardrails

Treat generated SQL exactly like SQL typed by an untrusted user, because the question came from a user:

```
question ──► Claude ──► {sql, explanation}
                           │
                     is_read_only? ── no ──► refuse (PermissionError)
                           │ yes
                     row limit + read-only connection + timeout
                           │
                     execute ── error? ──► return the error, don't crash
                           │
                     rows (PII masked) + SQL + explanation ──► user
```

All the layers from the last lesson apply: a read-only database user, the keyword check, row limits, timeouts, and PII masking. A user typing *"delete all cancelled members"* should get a polite refusal, never a deleted table, even if the model happily writes the `DELETE`.

Generated SQL will sometimes fail (a misspelled column, wrong dialect). Catch database errors and return them gracefully. A good next step is to send the error back to Claude once and ask for a corrected query, a small "self-repair" loop.

## Evaluate before launch

Build a small **evaluation set** of 20-50 real questions from the customer's users, each with the correct answer (computed by you, by hand or from the metrics layer). Run the feature over all of them and measure how many results match. Keep the set, and re-run it whenever you change the prompt, the schema, or the model. Module 8 turns this into a proper evaluation harness; the habit starts here.

> **Key takeaways**
> - Text-to-SQL suits exploration on clean schemas, ideally your metrics-layer views; not official metrics or writes.
> - Give Claude real CREATE statements, business definitions, the dialect, and sample values; cache the schema prompt.
> - Use structured outputs for `{sql, explanation}` and show both to the user.
> - Run generated SQL behind every guardrail, handle errors gracefully, and evaluate on real questions before launch.
