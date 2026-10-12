import math

V = [normalize(v) for v in ([1, 0], [0, 1], [1, 1], [-1, 0], [2, 1], [1, -1])]


def test_normalize():
    """normalize() returns a unit vector and rejects the zero vector"""
    n = normalize([3, 4])
    assert n is not None and abs(n[0] - 0.6) < 1e-9 and abs(n[1] - 0.8) < 1e-9, f"[3, 4] -> [0.6, 0.8], got {n}"
    try:
        normalize([0, 0])
    except ValueError:
        return
    raise AssertionError("a zero vector has no direction: raise ValueError")


def test_brute_force_exact_cosine():
    """brute_force() ranks by cosine, normalises the query, and counts every comparison"""
    ids, comps = brute_force([10, 0], V, 3)
    assert ids[0] == 0, f"[1, 0] is the closest direction to [10, 0]; got {ids}"
    assert ids == [0, 4, 2], "[1, 1] and [1, -1] tie on cosine with [10, 0]: break ties by lower id"
    assert comps == 6, "brute force compares the query with every vector"


def test_ivf_lists_partition_the_corpus():
    """Every vector lands in exactly one IVF list, the one with its nearest centroid"""
    docs, _ = make_corpus(n=300, queries=1)
    vecs = [normalize(d) for d in docs]
    idx = IVFIndex(vecs, n_lists=12)
    flat = sorted(i for lst in idx.lists for i in lst)
    assert flat == list(range(300)), "each id must appear in exactly one list"
    for c, lst in enumerate(idx.lists):
        for i in lst[:5]:
            best = max(dot(vecs[i], cen) for cen in idx.centroids)
            assert abs(dot(vecs[i], idx.centroids[c]) - best) < 1e-12, f"vector {i} is not in its nearest centroid's list"


def test_ivf_search_cost_and_exactness():
    """search() counts centroids plus scanned vectors, and probing every list equals brute force"""
    docs, qs = make_corpus(n=300, queries=5)
    vecs = [normalize(d) for d in docs]
    idx = IVFIndex(vecs, n_lists=12)
    q = qs[0]
    ids, comps = idx.search(q, 5, 1)
    nearest = max(range(12), key=lambda c: dot(normalize(q), idx.centroids[c]))
    assert comps == 12 + len(idx.lists[nearest]), "comparisons = 12 centroids + the members of the probed list"
    assert set(ids) <= set(idx.lists[nearest]), "with n_probe=1, results come only from the nearest list"
    for q in qs:
        assert idx.search(q, 5, 12)[0] == brute_force(q, vecs, 5)[0], "probing every list must match brute force exactly"
    try:
        idx.search(q, 5, 0)
    except ValueError:
        return
    raise AssertionError("n_probe < 1 makes no sense: raise ValueError")


def test_recall_at_k():
    """recall_at_k() is the share of the exact top-k that was found"""
    assert recall_at_k([1, 2, 3, 9], [1, 2, 3, 4]) == 0.75
    assert recall_at_k([4, 3, 2, 1], [1, 2, 3, 4]) == 1.0, "order doesn't matter for recall@k"
    assert recall_at_k([], [1]) == 0.0


def test_sweep_and_pick():
    """sweep() shows recall and cost rising with n_probe; pick_n_probe() finds the cheapest setting"""
    docs, qs = make_corpus(n=600, queries=12)
    vecs = [normalize(d) for d in docs]
    idx = IVFIndex(vecs, n_lists=20)
    rows = sweep(idx, qs, 10, [1, 3, 20])
    assert rows is not None and [r["n_probe"] for r in rows] == [1, 3, 20], f"one row per n_probe, got {rows}"
    assert rows[-1]["recall"] == 1.0, "probing all 20 lists is exact"
    assert rows[0]["recall"] < rows[-1]["recall"], "one probe should miss some neighbours on this corpus"
    assert rows[0]["avg_comparisons"] < rows[1]["avg_comparisons"] < rows[2]["avg_comparisons"] == 620.0, \
        f"cost rises with n_probe; probing everything costs 20 centroids + 600 vectors. Got {rows}"
    assert pick_n_probe(rows, 1.0) == 20
    assert pick_n_probe([{"n_probe": 4, "recall": 0.97}, {"n_probe": 2, "recall": 0.96}], 0.95) == 2, \
        "return the smallest qualifying n_probe, whatever order the rows are in"
    assert pick_n_probe(rows, 1.01) is None, "nothing reaches the target: None"
