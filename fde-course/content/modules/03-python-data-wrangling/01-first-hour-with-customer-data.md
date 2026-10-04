---
title: Your First Hour with Customer Data
type: reading
minutes: 14
---

> **By the end of this lesson you will be able to:**
> - Explain why "the data is clean" is a hypothesis you test, not a fact you accept
> - Name the seven kinds of mess you'll find in almost every customer dataset
> - Run a first-hour profiling routine and know which questions to send back to the customer

## The most expensive sentence in FDE work

*"Don't worry, the data is clean."*

You'll hear it in almost every kickoff. It's said in good faith, by someone who uses the data through a screen that hides its problems. Then you open the export and find dates in three formats, a "phone" column containing email addresses, and 4% of customer IDs duplicated.

This isn't the customer's fault, and it isn't unusual. Data from real businesses has been typed by hundreds of people over years, migrated between systems, and patched by scripts nobody remembers. **Messy data is the normal case.** Your job is to find the mess fast, quantify it, fix what you can, and tell the customer clearly about what you can't.

## Meet Cobalt Supply

Throughout this module you'll work with **Cobalt Supply**, an industrial parts distributor. They're replacing two old systems (a CRM and a billing system) and want Claude to help their sales team. Before anything AI-powered can work, their data has to be understood and cleaned. They've sent you CSV exports, and the next exercises use real-looking samples of them.

## The seven kinds of mess

| Kind | What it looks like | Example from Cobalt |
|---|---|---|
| **Missing values** | Blanks, but also `N/A`, `null`, `-`, `none`, `0000-00-00` | 11% of accounts have no industry |
| **Inconsistent formats** | Same thing written different ways | `2026-03-04`, `03/04/2026`, `Mar 4 2026` |
| **Wrong types** | Numbers stored as text, with symbols | `"$1,204.50"`, `"(45.00)"` for a refund |
| **Duplicates** | The same entity entered twice | `Acme Corp` and `ACME Corporation, Inc.` |
| **Invalid values** | Values that can't be right | Order date in 2091; negative quantity |
| **Broken references** | IDs that point to nothing | Invoices for account IDs not in the CRM |
| **Semantic drift** | A field's meaning changed over time | `status = "closed"` meant *won* until 2023, then *lost or won* |

The last one is the sneakiest. You won't find it with code; you find it by asking people. "Has the meaning of this field ever changed?" is one of the best questions you can ask a data owner.

## The first-hour routine

Before you write any cleaning code, spend an hour just *looking*. Here's a routine that works on any tabular dataset.

**1. Get the shape.** How many rows and columns? Does the row count match what the customer expects? ("You said 40,000 accounts; I see 52,117. Is that expected?")

**2. Read 20 random rows.** Not the first 20, which are often test data or the oldest records. Random ones. You'll spot most formatting problems by eye.

**3. Profile every column:**
- How many values are missing (including the disguised missing values above)?
- How many distinct values? A "country" column with 214 distinct values in a US-only business needs a look.
- What are the most common values? The top value often reveals a default ("Unknown," "1900-01-01").
- What type does it *look* like: integers, decimals, dates, or text?

**4. Check the keys.** Is the ID column actually unique? Do foreign keys (like `account_id` on invoices) match the other table?

**5. Check the ranges.** Earliest and latest dates, smallest and largest amounts. Outliers are either data errors or the most interesting rows in the dataset.

**6. Write down questions.** Everything you can't explain becomes a question for the data owner.

You'll build an automated version of step 3 in the next exercise.

## Reading CSV files in Python

The standard library's `csv` module is all you need for most exports:

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

Two things to notice:

- **Every value is a string**, including numbers. `"1,200,000"` is text until you clean it. That's a feature: it means nothing gets silently mis-converted.
- **Quoted fields** handle commas inside values. Never split CSV lines on commas yourself.

For a real file, use `open("accounts.csv", newline="", encoding="utf-8")` instead of `io.StringIO`. If you see strange characters like `Ã©`, the file is probably in a different encoding; try `encoding="cp1252"` or `"latin-1"`, and ask the customer which system produced it.

### The same in pandas

On your own machine you'll often use pandas for larger files. The equivalents:

```python
import pandas as pd

df = pd.read_csv("accounts.csv", dtype=str, keep_default_na=False)  # everything as text, like csv
df.shape                      # (rows, columns)
df.sample(20)                 # 20 random rows
df["industry"].value_counts() # most common values
df["account_id"].is_unique    # key check
```

`dtype=str` and `keep_default_na=False` are worth remembering. Without them, pandas guesses types and converts strings like `"NA"` to missing values on its own, which can hide exactly the problems you're trying to find. In this course's exercises we use the standard library so you can see every step, and so your code runs instantly in the browser.

## Communicating what you find

At the end of your first hour, send the data owner a short note. It builds trust and surfaces answers you can't get from the data:

```
Subject: First look at the CRM export — 4 questions

Thanks Dana, the export arrived fine. First observations:
  • 52,117 accounts (you mentioned ~40k; are inactive accounts included?)
  • 11% have no industry; is there another source for that?
  • 2,140 account IDs appear on invoices but not in the CRM
  • "status" has values closed/won/lost; did "closed" change meaning at some point?
No action needed yet. Tomorrow I'll send a full data-quality summary.
```

> **Key takeaways**
> - Treat "the data is clean" as a hypothesis. Messy data is the normal case.
> - Look for the seven kinds of mess: missing, inconsistent formats, wrong types, duplicates, invalid values, broken references, semantic drift.
> - Profile before you clean: shape, random rows, per-column profile, keys, ranges, questions.
> - Read CSVs with `csv.DictReader` (or pandas with `dtype=str`) so nothing is silently converted.
