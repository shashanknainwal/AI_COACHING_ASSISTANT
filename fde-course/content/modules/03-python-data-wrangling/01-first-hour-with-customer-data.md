---
title: Your First Hour with Customer Data
type: reading
minutes: 7
---

> **By the end of this lesson you will be able to:**
> - Treat "the data is clean" as a hypothesis you test
> - Name the seven kinds of mess in almost every customer dataset
> - Run a first-hour profiling routine and send the right questions back

Owen Bradley, CFO of Cobalt Supply, is replacing an old CRM and billing system and wants Claude to help his sales team. At kickoff he tells you "the data is clean" and sends you CSV exports. Your first hour decides whether you find the problems now or in front of his board.

He means it in good faith; he sees the data through screens that hide its problems. Messy data is the normal case. Find the mess fast, quantify it, fix what you can, and say clearly what you can't.

## The seven kinds of mess

| Kind | What it looks like | Example from Cobalt |
|---|---|---|
| **Missing values** | Blanks, but also `N/A`, `null`, `-`, `none`, `0000-00-00` | 11% of accounts have no industry |
| **Inconsistent formats** | Same thing written different ways | `2026-03-04`, `03/04/2026`, `Mar 4 2026` |
| **Wrong types** | Numbers stored as text, with symbols | `"$1,204.50"`, `"(45.00)"` for a refund |
| **Duplicates** | The same entity entered twice | `Acme Corp` and `ACME Corporation, Inc.` |
| **Invalid values** | Values that can't be right | Order date in 2091; negative quantity |
| **Broken references** | IDs that point to nothing | Invoices for account IDs not in the CRM |
| **Semantic drift** | A field's meaning changed over time | `status = "closed"` meant *won* until 2023, then *won or lost* |

You won't find semantic drift with code. You find it by asking the data owner: "Has the meaning of this field ever changed?"

## The first-hour routine

1. **Shape.** Does the row count match what the customer expects? ("You said 40,000 accounts; I see 52,117.")
2. **Read 20 random rows.** Not the first 20, which are often test data.
3. **Profile every column:** missing count (including disguised blanks), distinct count, most common values (the top value often reveals a default like "Unknown" or "1900-01-01"), and what type it looks like.
4. **Check the keys.** Is the ID unique? Do foreign keys match the other table?
5. **Check the ranges.** Earliest and latest dates, smallest and largest amounts.
6. **Write down questions** for everything you can't explain.

You'll automate step 3 in the next exercise.

## Reading CSV files in Python

```python
import csv
import io

text = """account_id,name,industry,annual_revenue
A-001,Acme Corp,Manufacturing,"1,200,000"
A-002,Birch & Co,,N/A
"""

rows = list(csv.DictReader(io.StringIO(text)))
print(rows[0])   # {'account_id': 'A-001', 'name': 'Acme Corp', ...}
print(len(rows)) # 2
```

- **Every value is a string**, so nothing gets silently mis-converted before you've looked.
- **Quoted fields** handle commas inside values. Never split CSV lines on commas yourself.

For a real file, use `open(path, newline="", encoding="utf-8")`; if you see `Ã©`, try `encoding="cp1252"`.

In pandas, use `pd.read_csv(path, dtype=str, keep_default_na=False)`. Without those two arguments pandas guesses types and turns `"NA"` into missing values, hiding the problems you're looking for. The exercises use the standard library so you see every step.

## Send a first-look note

```
Subject: First look at the CRM export — 4 questions

Thanks Owen, the export arrived fine. First observations:
  • 52,117 accounts (you mentioned ~40k; are inactive accounts included?)
  • 11% have no industry; is there another source for that?
  • 2,140 account IDs appear on invoices but not in the CRM
  • "status" has values closed/won/lost; did "closed" change meaning at some point?
No action needed yet. Tomorrow I'll send a full data-quality summary.
```

> **Key takeaways**
> - "The data is clean" is a hypothesis. Profile before you clean.
> - Seven kinds of mess: missing, inconsistent formats, wrong types, duplicates, invalid values, broken references, semantic drift.
> - Read CSVs as text (`csv.DictReader`, or pandas with `dtype=str`) so nothing is silently converted.
