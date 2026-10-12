import math

# Toy 4-dimensional "embeddings". Real ones have hundreds or thousands of dimensions.
DOCS = {
    "refund-policy":   [0.9, 0.1, 0.0, 0.1],
    "return-window":   [0.8, 0.3, 0.1, 0.0],
    "shipping-times":  [0.1, 0.9, 0.2, 0.0],
    "gift-cards":      [0.3, 0.0, 0.9, 0.1],
    "careers":         [0.0, 0.1, 0.1, 0.9],
    "empty-page":      [0.0, 0.0, 0.0, 0.0],
}
QUERY = [0.85, 0.2, 0.05, 0.05]   # "how do I get my money back?"


def cosine(a, b):
    """Cosine similarity of two equal-length vectors. Return 0.0 if either has zero length."""
    # TODO
    pass


def top_k(query, docs, k):
    """Return the k most similar docs as [(doc_id, score rounded to 4)], best first, ties by doc_id."""
    # TODO
    pass


def chunk_words(text, size, overlap):
    """Split text into chunks of `size` words, each starting `size - overlap` words after the last."""
    # TODO
    pass


# --- Try it out (not graded) ---
print("top 3:", top_k(QUERY, DOCS, 3))
print("chunks:", chunk_words("one two three four five six seven eight nine ten", size=4, overlap=1))
