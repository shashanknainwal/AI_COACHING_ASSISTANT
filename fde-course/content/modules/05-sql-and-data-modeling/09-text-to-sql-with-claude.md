---
title: "Text-to-SQL with Claude, Safely"
type: reading
minutes: 5
---

> **By the end of this lesson you will be able to:**
> - Say when text-to-SQL fits and when it's the wrong tool
> - Give Claude the schema context it needs
> - Run generated SQL behind guardrails
> - Evaluate the feature before a customer relies on it

Tom's location managers want to type *"Which location had the most visits in March?"* and get an answer without waiting for the data team. A plausible query that double-counts revenue is worse than no answer, because people trust it.

## Good fit vs. wrong tool

| Good fit | Wrong tool |
|---|---|
| Exploration by people who'll sanity-check | Official board metrics (use the metrics layer) |
| Clean, well-named views | Hundreds of cryptic legacy tables |
| Read-only replica | Anything that writes |
| Users see the SQL and result | Automated decisions with no human |

Point it at your **metrics-layer views**, so "revenue" always means the agreed definition.

## Giving Claude the right context

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

What improves accuracy:

- **Real `CREATE` statements**, pulled from the database so they never drift.
- **Business definitions** for "active," "churn," "revenue."
- **The dialect** (date functions differ).
- **Sample values** for categorical columns (`status IN ('active', 'cancelled')`), so Claude doesn't guess `'canceled'`.

The long, unchanging schema prompt is ideal for **prompt caching** (Module 6).

## Structured output

Ask for both fields with structured outputs:

```python
SQL_SCHEMA = {
    "type": "object",
    "properties": {"sql": {"type": "string"}, "explanation": {"type": "string"}},
    "required": ["sql", "explanation"],
    "additionalProperties": False,
}
```

Show both next to the result so users can catch a misunderstanding.

## Never execute without guardrails

Generated SQL is untrusted input:

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

*"Delete all cancelled members"* gets a refusal in code, never a deleted table, even if the model writes the `DELETE`. Return database errors gracefully; optionally send one back to Claude for a single repair attempt.

## Evaluate before launch

Collect 20–50 real user questions with correct answers you computed yourself. Measure how many results match, and re-run whenever the prompt, schema or model changes. Module 8 turns this into a full harness.

> **Key takeaways**
> - Text-to-SQL suits exploration on clean views, not official metrics or writes.
> - Give Claude real CREATE statements, definitions, dialect and sample values; cache the schema prompt.
> - Get `{sql, explanation}` as structured output and show both.
> - Guard every query, handle errors, and evaluate on real questions.
