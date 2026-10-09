---
title: "Entity Resolution: Finding Duplicates That Don't Look Alike"
type: reading
minutes: 3
---

> **By the end of this lesson you will be able to:**
> - Normalize company names and domains so obvious duplicates match exactly
> - Score fuzzy matches and choose a threshold from labeled examples
> - Design a review workflow, including where Claude helps

Cobalt's CRM has `Acme Corp`, `acme corporation` and `ACME Corporation, Inc.`: one customer, three records. Ask Owen's future assistant "What does Acme pay us?" and it finds three answers. Duplicates split revenue, inflate customer counts, send two reps to the same buyer, and every retrieval or agent system (Module 7) inherits them.

## Step 1: normalize so easy matches are exact

```
"ACME Corporation, Inc."  →  "acme"
"Acme Corp"               →  "acme"
"Birch & Co"              →  "birch and"
"Birch and Company LLC"   →  "birch and"    (odd-looking, but both match)
```

1. `casefold()`; replace `&` with `and`.
2. Turn punctuation into spaces and split into words.
3. Remove **trailing** legal suffixes (`inc`, `llc`, `ltd`, `corp`, `corporation`, `co`, `company`), repeatedly, so `Corp Inc` loses both. Only from the end: `Co-op Grocers` keeps its first word.
4. Join with single spaces.

**Domains are strong keys.** Website `acme.com` and email `buyer@acme.com` likely mean the same company even when names differ. Lowercase, strip `http://`, `https://`, `www.`, take what's after `@`, cut any path. **Exclude free email domains**: two `@gmail.com` contacts are not the same company.

## Step 2: score the near-misses

Typos and abbreviations survive normalization. Score similarity from 0 to 1:

```python
from difflib import SequenceMatcher

SequenceMatcher(None, "meridian valves", "meridan valves").ratio()      # 0.97
SequenceMatcher(None, "meridian valves", "northwind bearings").ratio()  # 0.24
```

| Measure | Good at | Weak at |
|---|---|---|
| Sequence ratio (`difflib`) | Typos, small edits | Reordered words |
| Token overlap (Jaccard) | Reordered words | Typos |
| Phonetic (Soundex) | Names that sound alike | Everything else |
| Embeddings | Meaning ("IBM" ≈ "International Business Machines") | Cost, explainability |

Combine cheap signals: exact normalized name, same domain, fuzzy score.

## Step 3: choose a threshold knowingly

- **False positive:** merging two different companies. Usually *worse*: it corrupts data and is hard to undo.
- **False negative:** missing a real duplicate. The data is no worse than before.

A high threshold (0.95) gives high precision, low recall; a low one (0.70) lets "Acme Pumps" vs "Apex Pumps" through. **Label 50–100 candidate pairs** by hand (or with the customer) and pick the threshold that gives the precision they need. That's your first evaluation; Module 8 goes deeper.

## Step 4: blocking at scale

All pairs is *n²/2*: 50,000 accounts is 1.25 billion comparisons. **Blocking** compares only records that share something cheap (first letter, ZIP, domain): a few lost matches for a 100x–1000x speedup.

## Step 5: review, then merge

```
all pairs ──► score ──► ≥ 0.95 or same domain ──► auto-merge list (spot-check 20)
                    ──► 0.80-0.95              ──► human review queue
                    ──► < 0.80                 ──► ignore
```

**Survivorship rules** decide which fields survive a merge: most recently updated, the system of record, or the most complete record.

## Where Claude fits

The middle band is where Claude helps: it can see that "Acme Industrial Holdings (acme.com, Ohio)" and "Acme (acme.com, Columbus OH)" are one company. Rules first for the easy 95%; send only ambiguous pairs to Claude with a structured output like `{"same_entity": bool, "reason": str}`; keep a human approving merges. You send hundreds of pairs, not millions.

> **Key takeaways**
> - Normalize names (casefold, `&`→`and`, punctuation, trailing suffixes) and domains (minus free email providers).
> - Choose thresholds from labeled pairs; false merges are usually worse than missed ones.
> - Block at scale, queue the middle band for review, and use Claude only on ambiguous pairs.
