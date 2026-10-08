RRF_K = 60


def rrf(rankings, k=RRF_K, weights=None):
    """Reciprocal rank fusion.

    rankings: lists of doc ids, best first. Score = sum of weight / (k + rank), rank from 1.
    Returns [(doc_id, score rounded to 6 places)], best first; ties by best single rank, then doc id.
    """
    # TODO
    pass


def matches(meta, filters):
    """True if meta satisfies every filter. A list value means "any of"; a missing field never matches."""
    # TODO
    pass


def apply_filter(ranking, docs, filters):
    """The ids in ranking, in order, that have metadata in docs and match the filters."""
    # TODO
    pass


def hybrid_search(query, filters=None, k=5, weights=None):
    """Filter keyword_search and vector_search results, fuse them with rrf, return the top k ids."""
    # TODO
    pass


# --- Try it out (not graded) ---
customer = {"product": "cloud", "version": [4, 5], "audience": "public"}
for q in ["token expired", "undo a bad deploy", "E4012"]:
    print(f"{q!r}")
    print("   keyword:", keyword_search(q)[:5])
    print("   vector: ", vector_search(q)[:5])
    fused = hybrid_search(q)
    print("   hybrid: ", fused)
    filtered = hybrid_search(q, filters=customer)
    if filtered:
        print("   hybrid, cloud customer:", [f"{d} {DOCS[d]['title']}" for d in filtered])
