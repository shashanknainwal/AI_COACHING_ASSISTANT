---
title: "Exercise: Brute Force Versus IVF, Measured"
type: exercise
minutes: 40
hints:
  - "`normalize`: divide by the square root of the sum of squares. Check for zero before you divide."
  - "`brute_force`: normalise the query, score every vector with `dot`, and sort by `(-score, id)` so ties go to the lower id. Comparisons is simply `len(vectors)`."
  - "`IVFIndex.__init__`: for each vector, pick the centroid with the highest dot product (ties to the lower centroid index) and append the vector's id to that list."
  - "`search`: rank centroids by dot with the normalised query, take the first `n_probe`, gather their members, then score only those the same way as brute force. Comparisons = all centroids (you scored each one) + the members you scored."
  - "`sweep`: compute the exact answer once per query with `brute_force`, then for each `n_probe` average recall and comparisons over the queries. `pick_n_probe` filters rows that meet the target and takes the minimum `n_probe`."
---

Noor is back. Lumenfold's "related articles" feature searches about 40 million article embeddings, and the vector store's index settings were copied from a blog post. An editor complained that an obvious related story never shows up. Noor's question is simple: "How much recall are we giving up for speed, and is the setting right?" Noor and Lumenfold are fictional.

You can't measure that on 40 million vectors in a browser. You can measure it on a small corpus with the same mechanics. You'll write exact cosine search, a toy IVF index (k-means clusters plus probing), and a sweep that reports **recall@k against brute force** and the **number of comparisons** for each `n_probe` setting. Comparisons are a stand-in for latency that doesn't depend on how fast your laptop is.

`kmeans` and `make_corpus` are given. The corpus is synthetic: clustered 12-dimensional vectors, standing in for real embeddings.

## Your task

1. **`normalize(v)`** returns `v` scaled to length 1. A zero vector raises `ValueError`.
2. **`brute_force(query, vectors, k)`**: `vectors` are already unit length; normalise the query, score all vectors by dot product (equal to cosine for unit vectors) and return `(ids, comparisons)`. `ids` is the top `k`, best first, ties broken by lower id; `comparisons = len(vectors)`.
3. **`IVFIndex(vectors, n_lists)`**: the centroids come from `kmeans`. Put each vector's id into the list of its nearest centroid (highest dot product, ties to the lower centroid index).
4. **`IVFIndex.search(query, k, n_probe)`**: rank centroids by dot product with the normalised query, probe the best `n_probe`, score only their members, and return `(ids, comparisons)` with `comparisons = number of centroids + vectors scored`. `n_probe < 1` raises `ValueError`. Probing every list must give exactly the brute-force answer.
5. **`recall_at_k(approx_ids, exact_ids)`**: the share of the exact ids that the approximate search found (order doesn't matter; an empty exact list gives 1.0).
6. **`sweep(index, queries, k, probes)`**: one row per `n_probe`, in the order given: `{"n_probe": p, "recall": mean recall (4 dp), "avg_comparisons": mean comparisons (1 dp)}`.
7. **`pick_n_probe(rows, target_recall)`**: the smallest `n_probe` whose recall meets the target, or `None`.

With 1,200 vectors and 40 lists, the demo prints something like:

```
{'n_probe': 1, 'recall': 0.73..., 'avg_comparisons': 76.5}
{'n_probe': 8, 'recall': 0.99..., 'avg_comparisons': 277.4}
```

Press **Run**, then **Submit**.

## Defend it

These are original practice questions in the style of a deep dive:

- "Why does one probe miss a quarter of the neighbours?" A query near a cluster border has true neighbours in the next cluster. More lists make each list smaller, so you need more probes for the same recall.
- "Comparisons aren't latency." True. Real latency also depends on memory layout, SIMD, quantised vectors and the cache. Measure p95 on the real store too. The shape of the curve is what transfers.
- "How would you set `n_probe` in production?" Sweep on real queries against brute force on a sample, pick the cheapest setting that meets the recall target, and re-check it when the corpus grows or the embedding model changes.
- "Would you quantise these vectors?" Try int8, or binary with full-precision rescoring, and add the recall loss to the same sweep.
