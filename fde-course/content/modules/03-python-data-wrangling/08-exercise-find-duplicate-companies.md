---
title: "Exercise: Find Duplicate Companies"
type: exercise
minutes: 30
hints:
  - "`normalize_company`: `s = name.casefold().replace(\"&\", \" and \")`, then `words = re.sub(r\"[^a-z0-9]+\", \" \", s).split()`. While `words` is non-empty and `words[-1] in SUFFIXES`, pop it."
  - "`domain`: return None for missing values. Lowercase and strip, remove `http://` / `https://` with `re.sub(r\"^https?://\", \"\", s)`, keep the part after `@` if there is one, cut at the first `/`, then remove a leading `www.`."
  - "`similarity`: `round(SequenceMatcher(None, normalize_company(a), normalize_company(b)).ratio(), 2)`."
  - "Loop over pairs with two indexes: `for i in range(len(records)): for j in range(i + 1, len(records)):`."
  - "Decide the reason in order: same normalized name, then same (non-free) domain, then similarity ≥ threshold. If none applies, skip the pair."
  - "Sort the final list with `key=lambda p: (-p[\"score\"], p[\"ids\"])`."
---

Before Cobalt's new system goes live, their CRM accounts need deduplicating. You'll build the candidate-finding step: it doesn't merge anything; it produces a list of likely duplicates, each with a reason, for a human to review.

## The data

```python
{"id": "A-1001", "name": "Acme Corp", "website": "https://www.acme.com/about"}
{"id": "A-1004", "name": "ACME Corporation, Inc.", "website": "buyer@acme.com"}
```

The `website` field is messy: sometimes a URL, sometimes an email address, sometimes blank.

## Your task

**1. `normalize_company(name)`**:
1. `casefold()`, and replace `&` with ` and `
2. Replace every run of characters that aren't `a-z` or `0-9` with a single space, then split into words
3. Remove **trailing** words that are in `SUFFIXES`, repeatedly
4. Join with single spaces

`"ACME Corporation, Inc."` → `"acme"`; `"Birch & Co"` → `"birch and"`; `"Co-op Grocers"` → `"co op grocers"`.

**2. `domain(value)`** returns a normalized domain, or `None` if the value is missing. Lowercase and strip; remove a leading `http://` or `https://`; if there's an `@`, keep what's after it; cut at the first `/`; remove a leading `www.`.

**3. `similarity(a, b)`** returns the `difflib.SequenceMatcher` ratio of the two **normalized** names, rounded to 2 decimals.

**4. `find_duplicates(records, threshold=0.85)`** compares every pair `(i, j)` with `i < j` (input order) and returns candidate pairs:

```python
{"ids": ("A-1001", "A-1004"), "score": 1.0, "reason": "same name"}
```

- `reason` is the **first** of these that applies:
  1. `"same name"`: normalized names are equal
  2. `"same domain"`: both domains are present, equal, and **not** in `FREE_DOMAINS`
  3. `"similar name"`: `similarity` ≥ `threshold`
- Pairs where none apply are skipped. `score` is always the pair's `similarity`.
- Sort by score (highest first), then by `ids`.

Press **Run** to see the review queue for Cobalt, then **Submit**.

> **Look at the results critically.** Would you merge every pair? This list goes to a human reviewer, not straight into the database.
