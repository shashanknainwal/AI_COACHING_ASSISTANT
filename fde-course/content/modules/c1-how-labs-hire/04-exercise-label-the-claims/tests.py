import copy


def _src(kind, sid):
    return {"kind": kind, "independent_id": sid}


def _claim(text, *sources):
    return {"text": text, "sources": list(sources)}


def test_company_source_is_official():
    """A company source makes a claim official, whatever else is there"""
    got = label_claim(_claim("x", _src("company", "careers")))
    assert got == "official", f"one company source should give 'official', got {got!r}"
    got = label_claim(_claim("x", _src("candidate", "a"), _src("company", "posting")))
    assert got == "official", f"a company source anywhere in the list should give 'official', got {got!r}"


def test_three_independent_sources_are_reported():
    """Three distinct independent sources make a claim reported"""
    claim = _claim("x", _src("candidate", "a"), _src("guide", "b"), _src("news", "c"))
    got = label_claim(claim)
    assert got == "reported", f"candidate + guide + news with 3 different ids should give 'reported', got {got!r}"


def test_one_or_two_sources_are_anecdotal():
    """One or two independent sources make a claim anecdotal"""
    got = label_claim(_claim("x", _src("candidate", "a")))
    assert got == "anecdotal", f"one candidate source should give 'anecdotal', got {got!r}"
    got = label_claim(_claim("x", _src("candidate", "a"), _src("news", "b")))
    assert got == "anecdotal", f"two independent sources should give 'anecdotal', got {got!r}"


def test_repeated_ids_count_once():
    """The same independent_id counts once, even across kinds"""
    claim = _claim("x", _src("guide", "blog"), _src("guide", "blog"), _src("news", "blog"), _src("candidate", "a"))
    got = label_claim(claim)
    assert got == "anecdotal", (
        f"ids 'blog', 'blog', 'blog', 'a' are only 2 distinct sources, so expected 'anecdotal', got {got!r}. "
        "Count distinct independent_id values, not list entries."
    )


def test_no_usable_sources_is_unsupported():
    """No sources, or only unknown kinds, means unsupported"""
    got = label_claim(_claim("x"))
    assert got == "unsupported", f"a claim with no sources should give 'unsupported', got {got!r}"
    got = label_claim(_claim("x", _src("friend", "f1"), _src("rumour", "r1"), _src("friend", "f2")))
    assert got == "unsupported", f"unknown source kinds should be ignored, so expected 'unsupported', got {got!r}"


def test_prep_priorities_order_and_drop():
    """prep_priorities() orders official, reported, anecdotal and drops unsupported"""
    claims = [
        _claim("A anecdotal", _src("candidate", "a")),
        _claim("B unsupported"),
        _claim("C reported", _src("candidate", "a"), _src("guide", "b"), _src("news", "c")),
        _claim("D official", _src("company", "posting")),
        _claim("E anecdotal", _src("guide", "z")),
        _claim("F official", _src("company", "careers")),
    ]
    got = prep_priorities(claims)
    want = ["D official", "F official", "C reported", "A anecdotal", "E anecdotal"]
    assert got == want, f"expected {want!r}, got {got!r} (ties keep their original order)"


def test_prep_priorities_edge_cases():
    """prep_priorities() handles an empty list and doesn't modify its input"""
    got = prep_priorities([])
    assert got == [], f"an empty pile of notes should give [], got {got!r}"
    claims = [_claim("late", _src("candidate", "a")), _claim("first", _src("company", "c"))]
    before = copy.deepcopy(claims)
    got = prep_priorities(claims)
    assert isinstance(got, list), "implement prep_priorities first: it should return a list"
    assert claims == before, "the input list was changed; use sorted() instead of .sort()"
