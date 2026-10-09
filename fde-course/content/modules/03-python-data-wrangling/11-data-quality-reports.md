---
title: Data-Quality Reports That Drive Action
type: reading
minutes: 5
---

> **By the end of this lesson you will be able to:**
> - Describe data quality with six dimensions instead of "the data is bad"
> - Express checks as rules (data) and set severity by use case
> - Write a report that gets problems fixed at the source

Owen asked for a data-quality summary for his board pack. Some of it is bad news about data his own teams entered. Said vaguely, it sounds like an excuse; said precisely, with numbers and an owner, it gets fixed.

## Six dimensions

| Dimension | Question | Example check |
|---|---|---|
| **Completeness** | Is the value there? | Email is present |
| **Validity** | Right form? | Email matches a pattern |
| **Uniqueness** | Recorded once? | Account ID appears once |
| **Consistency** | Do related values agree? | CRM plan matches billing plan |
| **Timeliness** | Up to date? | Updated within 90 days |
| **Accuracy** | Actually true? | Address is real (needs a reference) |

Code checks the first four. Accuracy needs a reference or a human, so you sample it.

## Rules as data

```python
RULES = [
    {"name": "email present",     "column": "email",      "check": "required"},
    {"name": "email format",      "column": "email",      "check": "regex", "pattern": r"[^@\s]+@[^@\s]+\.[a-z]{2,}"},
    {"name": "account id unique", "column": "account_id", "check": "unique"},
    {"name": "industry allowed",  "column": "industry",   "check": "allowed", "values": ["Manufacturing", "Retail"]},
]
```

One small engine evaluates any list; the customer can read and agree the rules.

**Keep completeness and validity separate.** "Email format" checks only rows where an email is present; otherwise every missing email counts twice and the report overstates the problem.

## Severity depends on use

A duplicate account ID breaks joins and assistant answers, so it needs 100%; industry for segmenting can live with 90%. The exercise uses **critical** below 90%, **warning** below 98%, **ok** otherwise. On real engagements, agree thresholds per rule.

## Anatomy of a good report

```markdown
# Cobalt CRM data quality — Mar 12

1,000 rows checked against 6 rules.

| Rule              | Checked | Failed | Pass rate | Severity |
|-------------------|---------|--------|-----------|----------|
| email present     |   1,000 |    130 |     87.0% | critical |
| email format      |     870 |    104 |     88.0% | critical |
| industry allowed  |     890 |     44 |     95.1% | warning  |

Critical: 2, warnings: 1, ok: 3
```

Under the table, for each critical item: **3–5 real failing values**, a **likely cause** ("the web form doesn't validate emails"), and a **suggested owner and action**. Worst problems first; busy readers stop early.

## No blame

The readers often created the data. Instead of "Your CRM is full of garbage emails", write: "12% of emails don't match a valid format, mostly from the 2019–2021 web form. Adding validation would prevent new ones; we've excluded the existing ones from the pilot."

## Make it repeatable

Weekly runs show trends ("88% → 93% → 97%") and turn the rules into a **data contract**. `pandera` and Great Expectations do this at scale.

> **Key takeaways**
> - Use the six dimensions, not "the data is bad".
> - Rules as data, one engine; completeness and validity counted separately.
> - Severity follows use. Lead with the worst, with examples, cause and owner, and no blame.
