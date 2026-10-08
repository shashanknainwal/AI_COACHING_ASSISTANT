RRF_K = 60


def rrf(rankings, k=RRF_K, weights=None):
    if weights is None:
        weights = [1.0] * len(rankings)
    scores, best = {}, {}
    for ranking, weight in zip(rankings, weights):
        for rank, doc_id in enumerate(ranking, 1):
            scores[doc_id] = scores.get(doc_id, 0.0) + weight / (k + rank)
            best[doc_id] = min(best.get(doc_id, rank), rank)
    fused = [(doc_id, round(score, 6)) for doc_id, score in scores.items()]
    fused.sort(key=lambda item: (-item[1], best[item[0]], item[0]))
    return fused


def matches(meta, filters):
    for key, wanted in (filters or {}).items():
        if key not in meta:
            return False
        if isinstance(wanted, list):
            if meta[key] not in wanted:
                return False
        elif meta[key] != wanted:
            return False
    return True


def apply_filter(ranking, docs, filters):
    return [doc_id for doc_id in ranking if doc_id in docs and matches(docs[doc_id], filters)]


def hybrid_search(query, filters=None, k=5, weights=None):
    lexical = apply_filter(keyword_search(query), DOCS, filters)
    dense = apply_filter(vector_search(query), DOCS, filters)
    return [doc_id for doc_id, _ in rrf([lexical, dense], weights=weights)[:k]]


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
