# Ridgeline Software's help center (fictional): titles and metadata for every article.
DOCS = {
    "KB-101": {"title": "Rolling back a deploy", "product": "cloud", "version": 5, "audience": "public"},
    "KB-102": {"title": "Rotating service account tokens", "product": "cloud", "version": 5, "audience": "public"},
    "KB-104": {"title": "Error E4012: token expired", "product": "cloud", "version": 5, "audience": "public"},
    "KB-108": {"title": "Why sessions time out", "product": "cloud", "version": 4, "audience": "public"},
    "KB-109": {"title": "Clock skew and authentication", "product": "self-hosted", "version": 5, "audience": "internal"},
    "KB-113": {"title": "Reverting a release on self-hosted", "product": "self-hosted", "version": 5, "audience": "public"},
    "KB-117": {"title": "Token lifetimes by plan", "product": "cloud", "version": 4, "audience": "internal"},
    "KB-122": {"title": "Expired invoices and billing holds", "product": "cloud", "version": 5, "audience": "public"},
    "KB-125": {"title": "Blue-green deploys", "product": "cloud", "version": 5, "audience": "public"},
    "KB-131": {"title": "Error E4012 on self-hosted", "product": "self-hosted", "version": 5, "audience": "public"},
    "KB-136": {"title": "Undoing a schema migration", "product": "self-hosted", "version": 4, "audience": "public"},
    "KB-140": {"title": "Expiring API keys (legacy)", "product": "cloud", "version": 3, "audience": "public"},
    "KB-145": {"title": "Re-authenticating the CLI", "product": "cloud", "version": 5, "audience": "public"},
    "KB-150": {"title": "Token scopes reference", "product": "self-hosted", "version": 5, "audience": "public"},
    "KB-160": {"title": "Session cookies and SSO", "product": "cloud", "version": 5, "audience": "internal"},
}

# Top-8 results from Ridgeline's two existing retrievers, best first.
# The keyword retriever is BM25; the vector retriever uses embeddings. Both are precomputed here.
_KEYWORD = {
    "token expired": ["KB-104", "KB-131", "KB-102", "KB-150", "KB-117", "KB-122", "KB-140", "KB-109"],
    "undo a bad deploy": ["KB-125", "KB-101", "KB-136"],
    "E4012": ["KB-104", "KB-131"],
}
_VECTOR = {
    "token expired": ["KB-131", "KB-108", "KB-104", "KB-160", "KB-102", "KB-117", "KB-145", "KB-109"],
    "undo a bad deploy": ["KB-101", "KB-113", "KB-136", "KB-125", "KB-145", "KB-102", "KB-108", "KB-140"],
    "E4012": ["KB-108", "KB-145", "KB-102", "KB-104", "KB-109", "KB-117", "KB-160", "KB-131"],
}


def keyword_search(query):
    """BM25 results for the query: a list of doc ids, best first (may be shorter than 8)."""
    return list(_KEYWORD.get(query, []))


def vector_search(query):
    """Embedding-similarity results for the query: a list of doc ids, best first."""
    return list(_VECTOR.get(query, []))
