import copy


def _r(id, impact, urgency, effort, blocked=False):
    return {"id": id, "title": f"Request {id}", "impact": impact, "urgency": urgency, "effort": effort, "blocked": blocked}


def test_score_basic():
    """score() computes impact × urgency ÷ effort"""
    got = score(_r("X", 4, 5, 2))
    assert got == 10, f"score of impact=4, urgency=5, effort=2 should be 10, got {got!r}"


def test_score_rounding():
    """score() rounds to 2 decimal places"""
    got = score(_r("X", 5, 5, 8))
    assert got == 3.12, f"25 / 8 = 3.125 should round to 3.12, got {got!r}"
    got = score(_r("X", 2, 1, 3))
    assert got == 0.67, f"2 / 3 should round to 0.67, got {got!r}"


def test_score_blocked():
    """Blocked requests score 0"""
    got = score(_r("X", 5, 5, 1, blocked=True))
    assert got == 0, f"a blocked request should score 0, got {got!r}"


def test_plan_example():
    """plan_sprint() matches the example in the instructions"""
    backlog = [_r("A", 4, 5, 4), _r("B", 3, 3, 1), _r("C", 5, 5, 8)]
    got = plan_sprint(backlog, 6)
    assert got == ["B", "A"], f"expected ['B', 'A'], got {got!r}"


def test_plan_skips_items_that_dont_fit():
    """plan_sprint() skips a request that doesn't fit and keeps looking"""
    backlog = [_r("BIG", 5, 5, 5), _r("MED", 4, 4, 4), _r("SMALL", 1, 2, 1)]
    # scores: BIG 5.0, MED 4.0, SMALL 2.0; capacity 6 -> BIG (1 left), skip MED, SMALL fits
    got = plan_sprint(backlog, 6)
    assert got == ["BIG", "SMALL"], f"expected ['BIG', 'SMALL'], got {got!r}"


def test_plan_tie_breaks():
    """Ties are broken by lower effort, then by id"""
    backlog = [_r("Z", 4, 2, 2), _r("Y", 4, 1, 1), _r("X", 4, 1, 1), _r("W", 8, 2, 4)]
    # all score 4.0 -> effort 1 first (X, Y by id), then Z (2), then W (4)
    got = plan_sprint(backlog, 100)
    assert got == ["X", "Y", "Z", "W"], f"expected ['X', 'Y', 'Z', 'W'], got {got!r}"


def test_plan_never_includes_blocked():
    """Blocked requests are never planned, even with spare capacity"""
    backlog = [_r("OK", 2, 2, 1), _r("STUCK", 5, 5, 1, blocked=True)]
    got = plan_sprint(backlog, 50)
    assert got == ["OK"], f"expected ['OK'], got {got!r}"


def test_plan_does_not_mutate_input():
    """plan_sprint() doesn't modify the input list"""
    backlog = [_r("A", 1, 1, 1), _r("B", 5, 5, 1)]
    before = copy.deepcopy(backlog)
    result = plan_sprint(backlog, 10)
    assert isinstance(result, list), "implement plan_sprint first: it should return a list"
    assert backlog == before, "the input list was changed; use sorted() instead of .sort()"


def test_plan_brightline():
    """plan_sprint() produces the right plan for the Brightline backlog"""
    backlog = [
        _r("BH-1", 4, 3, 5), _r("BH-2", 3, 5, 2), _r("BH-3", 5, 4, 3),
        _r("BH-4", 5, 5, 8, blocked=True), _r("BH-5", 1, 2, 1),
    ]
    got = plan_sprint(backlog, 10)
    assert got == ["BH-2", "BH-3", "BH-1"], f"expected ['BH-2', 'BH-3', 'BH-1'], got {got!r}"


def test_plan_empty():
    """plan_sprint() returns an empty list for an empty backlog"""
    got = plan_sprint([], 10)
    assert got == [], f"expected [], got {got!r}"
