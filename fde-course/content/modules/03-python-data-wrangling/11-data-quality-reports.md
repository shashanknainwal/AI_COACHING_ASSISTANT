---
title: Data-Quality Reports That Drive Action
type: reading
minutes: 14
---

> **By the end of this lesson you will be able to:**
> - Describe data quality with six standard dimensions instead of "the data is bad"
> - Express quality checks as rules (data), not scattered code
> - Set severity thresholds based on what the data is used for
> - Write a data-quality report that gets problems fixed at the source

## "The data is bad" helps no one

At some point every FDE has to tell a customer their data has problems. Said vaguely, it sounds like an excuse or an insult. Said precisely, with numbers, examples, and a suggested owner, it's one of the most valuable things you can deliver. Customers often learn more about their own operations from a good data-quality report than from the project itself.

## Six dimensions of data quality

| Dimension | Question | Example check |
|---|---|---|
| **Completeness** | Is the value there? | Email is present |
| **Validity** | Does it have the right form? | Email matches a pattern; revenue is numeric |
| **Uniqueness** | Is each entity recorded once? | Account ID appears once |
| **Consistency** | Do related values agree? | CRM plan matches billing plan |
| **Timeliness** | Is it up to date? | Last updated within 90 days |
| **Accuracy** | Is it actually true? | Address matches the real address (needs a reference source) |

The first four you can check with code. Timeliness needs timestamps. Accuracy usually needs a trusted reference or a human, so you'll mostly sample it.

## Rules as data

Instead of writing a function per check, describe checks as **data**:

```python
RULES = [
    {"name": "email present",     "column": "email",      "check": "required"},
    {"name": "email format",      "column": "email",      "check": "regex", "pattern": r"[^@\s]+@[^@\s]+\.[a-z]{2,}"},
    {"name": "account id unique", "column": "account_id", "check": "unique"},
    {"name": "industry allowed",  "column": "industry",   "check": "allowed", "values": ["Manufacturing", "Retail"]},
]
```

One small engine evaluates any list of rules. Benefits:

- The customer can read and agree on the rules (it's practically a document).
- Adding a check is one line, not new code.
- You can re-run the same rules every week and track whether quality is improving.

**One important design choice:** keep completeness and validity separate. A *validity* rule like "email format" should only look at rows where the email is present. Otherwise every missing email is counted twice (once as missing, once as invalid), and the report overstates the problem.

## Severity depends on the use case

A 95% pass rate is fine for one field and a disaster for another. Set thresholds based on what the data feeds:

| Rule | Used for | Acceptable pass rate |
|---|---|---|
| Account ID unique | Joins, AI assistant answers | 100%: duplicates cause wrong answers |
| Email format | Marketing emails | 98% |
| Industry present | Segmenting reports | 90% |

A simple scheme you'll implement: **critical** below 90%, **warning** below 98%, **ok** otherwise. In real engagements, agree thresholds per rule with the customer.

## Anatomy of a good report

```markdown
# Cobalt CRM data quality — Mar 12

1,000 rows checked against 6 rules.

| Rule              | Checked | Failed | Pass rate | Severity |
|-------------------|---------|--------|-----------|----------|
| email present     |   1,000 |    130 |     87.0% | critical |
| email format      |     870 |    104 |     88.0% | critical |
| industry allowed  |     890 |     44 |     95.1% | warning  |
| ...

Critical: 2, warnings: 1, ok: 3
```

Then, under the table, for each critical item:

- **Examples:** 3-5 real failing values ("jim@acme", "sales at birchco.com").
- **Likely cause:** "The web form doesn't validate emails."
- **Suggested owner and action:** "Marketing ops: add validation to the form; we'll exclude invalid emails from the pilot."

Put the worst problems first. Busy readers stop after the first few rows.

## Writing it without blame

The people reading the report often created the data, or manage the people who did. Keep the tone factual and forward-looking:

> ❌ "Your CRM is full of garbage emails."
> ✅ "12% of emails don't match a valid format, mostly from the 2019-2021 web form. Adding validation to the form would prevent new ones; we've excluded the existing ones from the pilot."

## Make it repeatable

The first report is a snapshot. The real value comes from running the same rules weekly:

- Trends show whether fixes are working ("email validity: 88% → 93% → 97%").
- New problems get caught early, before they reach the AI system.
- It becomes a **data contract**: an agreement about what "good data" means for this project.

On your own machine, libraries like `pandera` and Great Expectations implement rules-as-data at scale. The idea is exactly what you'll build in the next exercise.

> **Key takeaways**
> - Describe quality with dimensions: completeness, validity, uniqueness, consistency, timeliness, accuracy.
> - Write checks as rules (data) evaluated by one engine; keep completeness and validity separate.
> - Severity thresholds depend on how the data is used.
> - Lead with the worst problems, give examples, a likely cause and an owner, and avoid blame.
