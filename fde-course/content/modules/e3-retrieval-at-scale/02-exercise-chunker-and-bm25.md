---
title: "Exercise: A Chunker and BM25 From Scratch"
type: exercise
minutes: 40
hints:
  - "`chunk_text`: validate first, then `words = text.split()` and `step = size - overlap`. Loop with `start = 0`; append `words[start:start + size]`; break as soon as `start + size >= len(words)`, otherwise `start += step`."
  - "`chunk_corpus`: `for n, piece in enumerate(chunk_text(doc[\"text\"], size, overlap), 1)` and build the id with `f\"{doc['id']}#{n}\"`."
  - "In `__init__`, build `self.tfs = [Counter(tokenize(c[\"title\"] + \" \" + c[\"text\"])) for c in chunks]`, then `self.lengths` from `sum(tf.values())`. Count document frequency with another `Counter`, updating it with `tf.keys()` for each chunk."
  - "`score`: `norm = k1 * (1 - b + b * length / avgdl)`; for each term in `set(tokenize(query))`, take `f = tf.get(term, 0)`, skip it when `f == 0`, otherwise add `idf[term] * f * (k1 + 1) / (f + norm)`."
  - "`search`: score every chunk, keep scores above 0 as `(id, round(score, 4))`, sort with `key=lambda h: -h[1]` (a stable sort keeps chunk order for ties), and slice `[:k]`."
---

Leo Martins, a Staff engineer you're pairing with this week, forwards a take-home in the style applied AI teams send out. The fictional customer is **Ridgeline Software**. Their on-call engineers search runbooks during incidents, and the current search is a substring match that returns nothing for "token expired" because the runbook says "expired token". Leo's note: "Before anyone mentions embeddings, build the lexical baseline properly. Half the candidates I review can't write BM25 without a library, and the other half can't explain why their chunk boundaries are where they are. Do both."

Everything is plain Python. The six runbooks are already loaded as `RUNBOOKS`, a list of `{"id", "title", "text"}`.

## Your task

**1. `chunk_text(text, size, overlap)`** splits text into windows of `size` words, where each window shares `overlap` words with the previous one.

- Split on any whitespace (`text.split()`) and rejoin each window with single spaces.
- Windows start at `0, step, 2*step, ...` where `step = size - overlap`.
- **Stop after the first window that reaches the last word.** Don't emit a tail window that is fully inside the previous one.
- The last window may be shorter than `size`. No words means `[]`.
- Return `[{"start": word_offset, "text": "..."}]`.
- Raise `ValueError` unless `size >= 1` and `0 <= overlap < size` (otherwise the loop never advances).

**2. `chunk_corpus(docs, size, overlap)`** chunks every doc and returns dicts with `id` (`"RB-01#1"`, numbered from 1 within each doc), `doc_id`, `title`, `start` and `text`.

**3. `tokenize(text)`** returns lowercase `[a-z0-9]+` words, minus `STOPWORDS`. No stemming this time.

**4. `class BM25`**, built from a list of chunks, with `k1=1.2` and `b=0.75` by default. Index each chunk's **title plus text** (`title + " " + text`), so a chunk that never repeats its subject still matches it.

- `self.tfs`: a `Counter` of tokens per chunk. `self.lengths`: token count per chunk. `self.avgdl`: the mean length.
- `self.idf[t] = log(1 + (N - df + 0.5) / (df + 0.5))`, where `N` is the number of chunks and `df` the number of chunks containing `t`. This smoothed form never goes negative.
- `score(query, i)` sums, over each **distinct** query term with frequency `f > 0` in chunk `i`:

```
idf[t] * f * (k1 + 1) / (f + k1 * (1 - b + b * length_i / avgdl))
```

- `search(query, k=5)` returns up to `k` tuples `(chunk_id, score rounded to 4 places)` with a score above 0, highest first. Ties keep chunk order.

## What the formula is doing

| Part | Effect | Why you care |
|---|---|---|
| `idf` | Rare terms count more than common ones | `e4012` should outweigh `token` |
| `f * (k1 + 1) / (f + ...)` | Term frequency **saturates**: the 10th mention adds little | Keyword-stuffed pages can't buy the top spot |
| `1 - b + b * length / avgdl` | Long chunks need more matches to score the same | A 2,000-word page doesn't win just by containing everything |

`k1` controls how fast frequency saturates; `b` controls how much length matters (`b=0` turns length normalisation off). Interviewers like asking what happens at the extremes, so the tests check both.

## Example

```python
chunk_text("w0 w1 w2 w3 w4 w5 w6 w7 w8 w9", 4, 1)
# [{"start": 0, "text": "w0 w1 w2 w3"},
#  {"start": 3, "text": "w3 w4 w5 w6"},
#  {"start": 6, "text": "w6 w7 w8 w9"}]

INDEX.search("E4012 after rotation", k=3)
# [("RB-02#2", 4.6415), ("RB-02#1", 4.2696), ("RB-01#2", 0.9326)]
```

Press **Run** and look at `"undo a bad deploy"`. BM25 finds the rollback runbook only through the word "deploy"; "undo" and "roll back" never meet. That gap is what the next exercise fixes with a second retriever. Then press **Submit**.

> **Interview angle.** In the style of a deep-dive follow-up: "Your chunks are 40 words with 10 overlapping. Defend those numbers." A good answer names the tradeoff (small chunks match precisely but lose context; overlap protects facts that straddle a boundary but duplicates text and inflates the index) and says how you'd choose with data: try two or three settings and compare recall@k on a labelled query set (lesson 4).
