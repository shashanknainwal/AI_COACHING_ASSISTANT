---
title: "Entity Resolution: Finding Duplicates That Don't Look Alike"
type: reading
minutes: 17
---

> **By the end of this lesson you will be able to:**
> - Explain why duplicate entities are worse for AI systems than for reports
> - Normalize company names and domains so obvious duplicates match exactly
> - Score fuzzy matches, choose a threshold, and understand the precision/recall trade-off
> - Design a review workflow, including where Claude helps and where it doesn't

## Why duplicates matter more than you think

Cobalt's CRM has `Acme Corp`, `acme corporation`, and `ACME Corporation, Inc.` These are one customer. Duplicates cause:

- **Wrong numbers:** revenue per customer split across three records; customer counts inflated.
- **Bad experiences:** two sales reps calling the same customer in the same week.
- **Confused AI:** ask an assistant "What does Acme pay us?" and it finds three records with three answers. It might pick one, average them, or say something confidently wrong. Retrieval and agent systems (Module 7) inherit every duplicate in the data.

**Entity resolution** is the task of deciding which records refer to the same real-world thing.

## Step 1: normalize so easy matches are exact

Most duplicates differ in boring ways: capitalization, punctuation, legal suffixes, `&` vs `and`. Normalize those away:

```
"ACME Corporation, Inc."  →  "acme"
"Acme Corp"               →  "acme"
"Birch & Co"              →  "birch and"
"Birch and Company LLC"   →  "birch and"    (odd-looking, but both match)
```

A typical company-name normalizer:

1. `casefold()` the text.
2. Replace `&` with `and`.
3. Turn punctuation into spaces and split into words.
4. Remove **trailing** legal suffixes (`inc`, `llc`, `ltd`, `corp`, `corporation`, `co`, `company`…), repeatedly, so `Corp Inc` loses both.
5. Join the remaining words with single spaces.

Removing suffixes only from the *end* matters: `Co-op Grocers` and `Corporate Express` shouldn't lose their first word.

**Domains are great keys.** Two records with website `acme.com` and email `buyer@acme.com` are very likely the same company, even if the names differ completely ("Acme" vs "Acme Industrial Holdings"). Normalize domains by lowercasing, stripping `http://`, `https://`, and `www.`, taking what's after `@` for emails, and cutting any path.

But watch out for **free email domains**. Two contacts with `@gmail.com` addresses are not the same company. Keep an exclusion list.

## Step 2: score the near-misses

Some duplicates survive normalization: typos (`Meridan Valves`), abbreviations (`Intl` vs `International`), word order. For these you need a **similarity score** between 0 and 1.

Python's standard library includes one in `difflib`:

```python
from difflib import SequenceMatcher

SequenceMatcher(None, "meridian valves", "meridan valves").ratio()   # 0.97
SequenceMatcher(None, "meridian valves", "northwind bearings").ratio()  # 0.24
```

`ratio()` measures how much of the two strings can be lined up as matching blocks. It's simple and works well for typos. Other common measures:

| Measure | Good at | Weak at |
|---|---|---|
| Sequence ratio (`difflib`) | Typos, small edits | Reordered words |
| Token overlap (Jaccard) | Reordered words | Typos |
| Phonetic (Soundex, Metaphone) | Names that sound alike | Everything else |
| Embedding similarity | Meaning ("IBM" ≈ "International Business Machines") | Cost, explainability |

In practice, combine a couple of cheap signals: exact normalized name, same domain, and a fuzzy name score.

## Step 3: choose a threshold, knowingly

Any threshold makes two kinds of mistakes:

- **False positives:** you merge two different companies. This is usually *worse*: it corrupts data and is hard to undo.
- **False negatives:** you miss a real duplicate. Annoying, but the data is no worse than before.

| Threshold | Pairs flagged | Precision (flagged pairs that are real duplicates) | Recall (real duplicates found) |
|---|---|---|---|
| 0.95 | Few | Very high | Low |
| 0.85 | Moderate | High | Good |
| 0.70 | Many | Lower; "Acme Pumps" vs "Apex Pumps" sneak in | Very high |

Don't pick a threshold by intuition. **Label a sample**: take 50-100 candidate pairs, mark each as same/different by hand (or with the customer), and choose the threshold that gives the precision the customer needs. This is your first taste of evaluation, which Module 8 covers in depth.

## Step 4: the scale problem and blocking

Comparing every record with every other record is *n²/2* comparisons: 50,000 accounts means 1.25 billion pairs. Way too slow.

**Blocking** only compares records that share something cheap: the same first letter of the normalized name, the same ZIP code, or the same domain. You lose a few matches across blocks, and gain a 100x-1000x speedup. On small datasets (like the exercises here), you can compare all pairs.

## Step 5: review and merge

Never auto-merge everything above a threshold on a customer's production data. A safe workflow:

```
all pairs ──► score ──► ≥ 0.95 or same domain ──► auto-merge list (spot-check 20)
                    ──► 0.80-0.95              ──► human review queue
                    ──► < 0.80                 ──► ignore
```

When merging, you need **survivorship rules**: which record's fields survive? Common rules are "most recently updated wins," "the system of record wins" (from the last lesson), or "most complete record wins."

## Where Claude fits

The middle band (pairs that are *maybe* duplicates) is where an LLM can help. Claude can weigh context a string score can't see: "Acme Industrial Holdings (acme.com, Ohio)" vs "Acme (acme.com, Columbus OH)" is clearly the same company to a human reader.

A good pattern:

- Use cheap rules first (normalization, domains, similarity) to handle the 95% of easy cases.
- Send only the ambiguous pairs to Claude, with structured outputs: `{"same_entity": bool, "reason": str}`.
- Keep a human in the loop for anything that will be merged.

This keeps cost low (you're sending hundreds of pairs, not millions) and accuracy high. You'll practice the rules-first, LLM-second pattern in this module's Claude exercise.

> **Key takeaways**
> - Duplicates corrupt numbers and confuse AI systems built on the data.
> - Normalize names (casefold, `&`→`and`, punctuation, trailing suffixes) and domains (excluding free email providers).
> - Fuzzy scores need a threshold chosen from labeled examples; false merges are usually worse than missed ones.
> - Use blocking at scale, a review queue for the middle band, and Claude only for the ambiguous cases.
