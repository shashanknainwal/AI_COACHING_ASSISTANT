---
title: "Exercise: Brute-Force Cosine Top-k and a Chunker"
type: exercise
minutes: 20
hints:
  - "`cosine`: compute both norms with `math.sqrt(sum(x * x for x in v))`. If either is 0, return 0.0 before dividing."
  - "`top_k`: build `(doc_id, round(cosine(query, vec), 4))` pairs, then sort with `key=lambda item: (-item[1], item[0])` so higher scores come first and ties go alphabetically. Slice `[:k]`."
  - "`chunk_words`: split into words, step through start positions with `range(0, len(words), size - overlap)`, and stop after the chunk that reaches the last word."
---

Mira Vasquez, the module's fictional interviewer, says retrieval questions separate candidates fast: "Everyone says 'vector database'. Few can tell me what it computes." Before you reach for an index, you should be able to write the exact search it approximates, in a few minutes, and the chunker that feeds it.

The vectors here are four-dimensional toys for a fictional retailer's help centre, with one empty page whose vector is all zeros, which is the edge case that crashes naive code.

## Your task

**1. `cosine(a, b)`** returns `a·b / (|a|·|b|)`. If either vector has zero length, return `0.0`.

**2. `top_k(query, docs, k)`** scores every doc in `docs` (a dict of id to vector) against `query` and returns the best `k` as a list of `(doc_id, score)`, with scores rounded to 4 decimals. Sort by score, highest first; break ties by `doc_id` alphabetically. If `k` is larger than the corpus, return everything.

**3. `chunk_words(text, size, overlap)`** splits text on whitespace into chunks of `size` words. Each chunk starts `size - overlap` words after the previous one. Stop after the chunk that includes the last word. Empty text gives `[]`. (You may assume `size > 0` and `0 <= overlap < size`.)

## Example

```python
top_k(QUERY, DOCS, 3)
# [("refund-policy", 0.9898), ("return-window", 0.9886), ("gift-cards", 0.365)]

chunk_words("one two three four five six seven eight nine ten", size=4, overlap=1)
# ["one two three four", "four five six seven", "seven eight nine ten"]
```

Press **Run**, then **Submit**.

## After you pass: the scaling question

Be ready for the follow-up: "This is O(n·d) per query. When does that stop being fine, and what do you do?" A good answer: brute force is exact and fine up to roughly hundreds of thousands of vectors with vectorized maths; beyond that, an approximate index such as HNSW trades a little recall for much lower latency, and you measure recall@k against brute force on a sample to check what you lost.

> **Interview tip:** Mention normalization. "If I normalize vectors when I store them, cosine is a dot product, which is what most vector stores optimize."
