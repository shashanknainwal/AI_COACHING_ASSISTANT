"""Exact cosine search versus a toy IVF index, measured as recall against cost."""
import math
import random


# ---- Given: a tiny spherical k-means and a synthetic corpus -----------------------------
def kmeans(vectors, n_lists, iters=6, seed=7):
    """Return n_lists unit-length centroids (deterministic). Vectors must already be normalised."""
    rng = random.Random(seed)
    centroids = [list(v) for v in rng.sample(vectors, n_lists)]
    for _ in range(iters):
        sums = [[0.0] * len(vectors[0]) for _ in centroids]
        for v in vectors:
            best = max(range(len(centroids)), key=lambda c: sum(a * b for a, b in zip(v, centroids[c])))
            sums[best] = [s + x for s, x in zip(sums[best], v)]
        for c, s in enumerate(sums):
            n = math.sqrt(sum(x * x for x in s))
            if n > 0:
                centroids[c] = [x / n for x in s]
    return centroids


def make_corpus(n=1200, dims=12, topics=24, queries=30, seed=11):
    """Clustered article embeddings plus queries that sit near random topics (not normalised)."""
    rng = random.Random(seed)
    centres = [[rng.gauss(0, 1) for _ in range(dims)] for _ in range(topics)]
    docs = [[c + rng.gauss(0, 0.8) for c in rng.choice(centres)] for _ in range(n)]
    qs = [[c + rng.gauss(0, 0.9) for c in rng.choice(centres)] for _ in range(queries)]
    return docs, qs


# ---- Your code ----------------------------------------------------------------------------
def normalize(v):
    """Return v scaled to length 1. A zero vector raises ValueError."""
    n = math.sqrt(sum(x * x for x in v))
    if n == 0:
        raise ValueError("cannot normalise a zero vector")
    return [x / n for x in v]


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def brute_force(query, vectors, k):
    """Exact top-k by cosine. vectors are unit length; the query may not be.
    Returns (ids, comparisons): ids best first, ties broken by lower id; comparisons = len(vectors)."""
    q = normalize(query)
    scored = sorted(((-dot(q, v), i) for i, v in enumerate(vectors)))
    return [i for _, i in scored[:k]], len(vectors)


class IVFIndex:
    def __init__(self, vectors, n_lists, seed=7):
        """Cluster the (unit-length) vectors and put each id in the list of its nearest centroid."""
        self.vectors = vectors
        self.centroids = kmeans(vectors, n_lists, seed=seed)
        self.lists = [[] for _ in self.centroids]
        for i, v in enumerate(vectors):
            best = max(range(len(self.centroids)), key=lambda c: (dot(v, self.centroids[c]), -c))
            self.lists[best].append(i)

    def search(self, query, k, n_probe):
        """Probe the n_probe nearest centroids, score only their members.
        Returns (ids, comparisons) where comparisons = number of centroids + vectors scored."""
        if n_probe < 1:
            raise ValueError("n_probe must be at least 1")
        q = normalize(query)
        order = sorted(range(len(self.centroids)), key=lambda c: (-dot(q, self.centroids[c]), c))
        candidates = [i for c in order[:n_probe] for i in self.lists[c]]
        scored = sorted((-dot(q, self.vectors[i]), i) for i in candidates)
        return [i for _, i in scored[:k]], len(self.centroids) + len(candidates)


def recall_at_k(approx_ids, exact_ids):
    """Share of the exact top-k that the approximate search found."""
    if not exact_ids:
        return 1.0
    return len(set(approx_ids) & set(exact_ids)) / len(exact_ids)


def sweep(index, queries, k, probes):
    """For each n_probe: mean recall@k against brute force (4 dp) and mean comparisons (1 dp)."""
    exact = [brute_force(q, index.vectors, k) for q in queries]
    rows = []
    for p in probes:
        recalls, comps = [], []
        for q, (ids, _) in zip(queries, exact):
            got, c = index.search(q, k, p)
            recalls.append(recall_at_k(got, ids))
            comps.append(c)
        rows.append({"n_probe": p, "recall": round(sum(recalls) / len(recalls), 4),
                     "avg_comparisons": round(sum(comps) / len(comps), 1)})
    return rows


def pick_n_probe(rows, target_recall):
    """Smallest n_probe whose recall meets the target, or None."""
    ok = [r["n_probe"] for r in rows if r["recall"] >= target_recall]
    return min(ok) if ok else None


# --- Try it out (not graded) ---
if normalize([1.0]) is None:
    print("Implement normalize() first, then press Run again.")
else:
    docs, queries = make_corpus()
    vectors = [normalize(d) for d in docs]
    index = IVFIndex(vectors, n_lists=40)
    rows = sweep(index, queries, k=10, probes=[1, 2, 4, 8])
    if rows:
        print("brute force compares", len(vectors), "vectors per query")
        for r in rows:
            print(r)
        print("smallest n_probe for recall >= 0.95:", pick_n_probe(rows, 0.95))
