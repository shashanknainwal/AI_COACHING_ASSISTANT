CUSTOMER = {"product": "cloud", "version": [4, 5], "audience": "public"}


def test_rrf_scores():
    """rrf() sums 1 / (k + rank) across lists, with ranks starting at 1"""
    got = rrf([["a", "b"], ["b", "c"]])
    assert got == [("b", 0.032522), ("a", 0.016393), ("c", 0.016129)], \
        f"b = 1/62 + 1/61, a = 1/61, c = 1/62 (rounded to 6 places): got {got}"
    got = rrf([["a", "b"], ["c", "a"]], k=1)
    assert got == [("a", 0.833333), ("c", 0.5), ("b", 0.333333)], f"k=1: a = 1/2 + 1/3: got {got}"
    assert rrf([]) == [] and rrf([[], []]) == [], "no results in, no results out"


def test_rrf_ties():
    """Ties break by best single rank, then by doc id"""
    got = rrf([["p", "q"], ["a", "b", "c", "d", "q"]], k=1)
    assert [d for d, _ in (got or [])] == ["a", "p", "q", "b", "c", "d"], \
        f"a, p and q all score 0.5; a and p were ranked 1st somewhere, q only 2nd; a < p by id: got {got}"
    got = rrf([["x", "y"], ["y", "x"]])
    assert got == [("x", 0.032522), ("y", 0.032522)], \
        f"round before comparing, or float noise decides the order: got {got}"


def test_rrf_weights():
    """weights scale each list's contribution"""
    got = rrf([["a", "b"], ["c", "a"]], weights=[1.0, 3.0])
    assert got == [("a", 0.064781), ("c", 0.04918), ("b", 0.016129)], f"got {got}"


def test_matches():
    """matches() handles exact values, any-of lists and missing fields"""
    meta = DOCS["KB-108"]
    assert matches(meta, {"product": "cloud"}) is True, f"KB-108 is a cloud doc: got {matches(meta, {'product': 'cloud'})}"
    assert matches(meta, {"product": "cloud", "version": [4, 5]}) is True, "a list means any of these values"
    assert matches(meta, {"version": [5]}) is False
    assert matches(meta, {"audience": "internal"}) is False
    assert matches(meta, {"region": "eu"}) is False, "a field the doc doesn't have can't match (fail closed)"
    assert matches(meta, {}) is True and matches(meta, None) is True, "no filters match everything"


def test_apply_filter():
    """apply_filter() keeps order and drops docs with no metadata"""
    ranking = ["KB-131", "KB-999", "KB-108", "KB-104", "KB-160"]
    got = apply_filter(ranking, DOCS, CUSTOMER)
    assert got == ["KB-108", "KB-104"], f"got {got}"
    assert apply_filter(ranking, DOCS, None) == ["KB-131", "KB-108", "KB-104", "KB-160"], \
        "an id with no metadata is dropped even with no filters"
    assert ranking == ["KB-131", "KB-999", "KB-108", "KB-104", "KB-160"], "don't modify the input list"


def test_hybrid_search():
    """hybrid_search() fuses keyword and vector results"""
    got = hybrid_search("token expired")
    assert got == ["KB-131", "KB-104", "KB-102", "KB-117", "KB-109"], f"got {got}"
    assert hybrid_search("E4012", k=3) == ["KB-104", "KB-131", "KB-108"], \
        "the exact error code comes from the keyword list even though the vector list ranks it 4th"
    assert hybrid_search("undo a bad deploy", weights=[3.0, 1.0]) == ["KB-125", "KB-101", "KB-136", "KB-113", "KB-145"]
    assert hybrid_search("a query nobody indexed") == []


def test_hybrid_search_filters_before_fusing():
    """Filters apply to each list before fusion, so a strict filter still fills k slots"""
    got = hybrid_search("token expired", filters=CUSTOMER)
    assert got == ["KB-104", "KB-102", "KB-108", "KB-122", "KB-145"], \
        f"filter each list first, then fuse; filtering the fused top 5 would leave only 2 results: got {got}"
    assert hybrid_search("token expired", filters={"audience": "internal"}) == ["KB-117", "KB-109", "KB-160"], \
        "fewer than k matching docs means fewer than k results"
    assert hybrid_search("undo a bad deploy", filters={"product": "self-hosted"}) == ["KB-136", "KB-113"]
