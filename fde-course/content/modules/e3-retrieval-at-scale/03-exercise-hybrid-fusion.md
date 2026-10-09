---
title: "Exercise: Hybrid Retrieval With Rank Fusion and Filters"
type: exercise
minutes: 35
hints:
  - "`rrf`: default `weights` to `[1.0] * len(rankings)`. Loop `for ranking, weight in zip(rankings, weights)` and `for rank, doc_id in enumerate(ranking, 1)`; add `weight / (k + rank)` to a `scores` dict and keep `best[doc_id] = min(...)`."
  - "Round each score to 6 places **before** sorting, then sort with `key=lambda item: (-item[1], best[item[0]], item[0])`."
  - "`matches`: loop over `(filters or {}).items()`. Return False if the key is missing from `meta`; use `meta[key] in wanted` when `wanted` is a list and `==` otherwise. Return True at the end."
  - "`apply_filter` is one list comprehension: keep `doc_id` when `doc_id in docs and matches(docs[doc_id], filters)`."
  - "`hybrid_search`: filter `keyword_search(query)` and `vector_search(query)` separately with `DOCS`, pass both lists to `rrf(..., weights=weights)`, and return the first `k` ids."
---

Ridgeline Software's help center now has two retrievers. BM25 nails exact strings like `E4012` but misses paraphrases. The embedding retriever understands "undo a bad deploy" but ranks the exact error-code article fourth. Leo wants one ranked list from both, and a fix for a bug a customer found: a cloud customer on version 5 saw an **internal** article about self-hosted clock skew.

"Two things I'll ask you in the review," Leo says. "Why reciprocal rank fusion instead of adding the scores, and why you filter before fusing instead of after."

Available to your code: `DOCS` (doc id → `{"title", "product", "version", "audience"}`), `keyword_search(query)` and `vector_search(query)`. Each search returns a list of doc ids, best first.

## Your task

**1. `rrf(rankings, k=60, weights=None)`** fuses ranked lists with **reciprocal rank fusion**:

- Each doc scores `sum(weight_i / (k + rank_i))` over the lists it appears in. Ranks start at **1**. A doc missing from a list gets nothing from it.
- `weights` defaults to `1.0` for every list.
- Return `[(doc_id, score)]` with each score **rounded to 6 places**, best first.
- Ties (equal rounded scores) go to the doc with the better **single best rank** in any list, then to the smaller doc id.

**2. `matches(meta, filters)`** returns True when the doc's metadata satisfies **every** filter:

- A list value means "any of these" (`{"version": [4, 5]}`); anything else must be equal.
- If the doc has no such field, it does not match. Fail closed.
- `None` or `{}` matches everything.

**3. `apply_filter(ranking, docs, filters)`** returns the ids from `ranking`, in order, that have an entry in `docs` and match. An id with no metadata is always dropped, even with no filters: if you can't tell who may see it, nobody sees it. Don't modify the input list.

**4. `hybrid_search(query, filters=None, k=5, weights=None)`** filters the keyword list and the vector list **separately**, fuses them with `rrf` (passing `weights`), and returns the top `k` doc ids.

## Example

```python
rrf([["a", "b"], ["b", "c"]])
# [("b", 0.032522), ("a", 0.016393), ("c", 0.016129)]
#   b = 1/62 + 1/61    a = 1/61    c = 1/62

hybrid_search("token expired", filters={"product": "cloud", "version": [4, 5], "audience": "public"})
# ["KB-104", "KB-102", "KB-108", "KB-122", "KB-145"]
```

## Why the design looks like this

- **Ranks, not scores.** BM25 scores are unbounded (4.6, 7.9, ...); cosine similarities sit in a narrow band (0.71, 0.74, ...). Adding them lets whichever scale is larger dominate. RRF only uses positions, so it needs no score normalisation and no tuning beyond `k`. The constant `k=60` comes from the paper that introduced RRF (Cormack, Clarke and Büttcher, SIGIR 2009); a larger `k` flattens the difference between rank 1 and rank 10.
- **Filter first.** If you fuse, take the top 5, then drop what the customer can't see, "token expired" leaves only 2 results for the cloud customer. Filtering each candidate list first still fills 5 slots. Vector databases make the same distinction between pre-filtering and post-filtering, and approximate indexes can lose recall under very selective filters, so ask how yours handles it.
- **Permissions belong in retrieval, not in the prompt.** "Don't mention internal articles" in a system prompt is a request; a filter is a guarantee. The model can't leak a document it never received.

Press **Run** to compare keyword, vector and hybrid results for three queries, then **Submit**.

> **Interview angle.** In the style of a design follow-up: "Your hybrid search returns stale v3 articles for v5 customers. Where do you fix it?" A strong answer separates the layers: metadata filters (version, product, tenant, permissions) are applied at retrieval time; ranking quality (fusion weights, a reranker) is tuned against a labelled query set; and the prompt never carries an access rule on its own.
