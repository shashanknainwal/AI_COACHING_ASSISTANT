import math


def test_cosine_basics():
    """cosine() is 1 for the same direction, 0 for orthogonal, -1 for opposite"""
    assert cosine([1, 0], [3, 0]) is not None, "cosine() returned None"
    assert abs(cosine([1, 0], [3, 0]) - 1.0) < 1e-9, "length doesn't matter: same direction is 1.0"
    assert abs(cosine([1, 0], [0, 2])) < 1e-9, "orthogonal vectors score 0"
    assert abs(cosine([1, 2], [-1, -2]) + 1.0) < 1e-9, "opposite vectors score -1"
    assert abs(cosine([1, 2, 3], [4, 5, 6]) - 32 / (math.sqrt(14) * math.sqrt(77))) < 1e-9, "a.b / (|a| |b|)"


def test_cosine_zero_vector():
    """cosine() returns 0.0 instead of dividing by zero"""
    assert cosine([0, 0], [1, 1]) == 0.0 and cosine([1, 1], [0, 0]) == 0.0, "a zero vector has no direction: return 0.0"


def test_top_k_ranking():
    """top_k() returns the best matches first with scores rounded to 4"""
    got = top_k(QUERY, DOCS, 3)
    assert isinstance(got, list) and len(got) == 3, f"return a list of k pairs, got {got!r}"
    assert [d for d, _ in got] == ["refund-policy", "return-window", "gift-cards"], f"got {got}"
    assert got[0] == ("refund-policy", round(cosine(QUERY, DOCS["refund-policy"]), 4)), f"scores are rounded to 4 decimals: {got[0]}"
    assert top_k(QUERY, DOCS, 10)[-1][0] == "empty-page", "k larger than the corpus returns everything; the zero vector scores 0"


def test_top_k_ties():
    """top_k() breaks ties by doc_id so results are stable"""
    docs = {"b": [1, 0], "a": [2, 0], "c": [0, 1]}
    assert top_k([1, 0], docs, 2) == [("a", 1.0), ("b", 1.0)], f"equal scores sort by doc_id: got {top_k([1, 0], docs, 2)}"


def test_chunk_words():
    """chunk_words() makes overlapping word windows and stops at the end"""
    text = "one two three four five six seven eight nine ten"
    got = chunk_words(text, size=4, overlap=1)
    assert got == ["one two three four", "four five six seven", "seven eight nine ten"], f"got {got!r}"
    assert chunk_words(text, size=4, overlap=0) == ["one two three four", "five six seven eight", "nine ten"]
    assert chunk_words("a b c", size=5, overlap=2) == ["a b c"], "short text is one chunk"
    assert chunk_words("", size=3, overlap=1) == [], "empty text has no chunks"
