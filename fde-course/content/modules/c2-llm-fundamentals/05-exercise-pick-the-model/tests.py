import copy


def _m(name, quality, p95, cost):
    return {"name": name, "quality": quality, "p95_latency_ms": p95, "cost_per_1k_requests": cost}


TABLE = [
    _m("Model A", 0.96, 4200, 22.00),
    _m("Model B", 0.93, 2100, 11.00),
    _m("Model C", 0.81, 900, 0.55),
    _m("Model D", 0.91, 2600, 6.00),
]


def test_picks_cheapest_that_qualifies():
    """choose_model() returns the cheapest model that meets every constraint"""
    got = choose_model(TABLE, 0.90, 3000, 15.00)
    assert got == "Model D", f"A is too slow and too expensive, C misses quality; D ($6) beats B ($11). Got {got!r}"


def test_each_constraint_filters():
    """choose_model() applies quality, latency and budget"""
    got = choose_model(TABLE, 0.92, 3000, 15.00)
    assert got == "Model B", f"at min_quality 0.92 only B qualifies, got {got!r}"
    got = choose_model(TABLE, 0.90, 5000, 100.00)
    assert got == "Model D", f"with loose latency and budget, D is still the cheapest at quality >= 0.90, got {got!r}"
    got = choose_model(TABLE, 0.95, 5000, 20.00)
    assert got is None, f"A is the only model at quality >= 0.95 but costs $22 > $20 budget; expected None, got {got!r}"


def test_limits_are_inclusive():
    """A model exactly at a limit qualifies"""
    got = choose_model(TABLE, 0.91, 2600, 6.00)
    assert got == "Model D", f"D has quality 0.91, p95 2600 ms and $6.00, exactly at every limit; got {got!r}"


def test_tie_breaks():
    """Equal cost: higher quality wins, then name alphabetically"""
    table = [_m("Zeta", 0.90, 1000, 5.00), _m("Alpha", 0.94, 1000, 5.00), _m("Beta", 0.94, 1000, 5.00)]
    got = choose_model(table, 0.85, 2000, 10.00)
    assert got == "Alpha", f"Alpha and Beta tie on cost and quality and beat Zeta on quality; Alpha wins by name. Got {got!r}"


def test_none_and_empty():
    """choose_model() returns None when nothing qualifies or the table is empty"""
    assert choose_model(TABLE, 0.99, 10000, 100.00) is None, "no model reaches 0.99 quality, expected None"
    assert choose_model([], 0.5, 10000, 100.00) is None, "an empty table should return None"


def test_does_not_modify_input():
    """choose_model() leaves the candidate list unchanged"""
    table = copy.deepcopy(TABLE)
    choose_model(table, 0.90, 3000, 15.00)
    assert table == TABLE, "choose_model() should not reorder or change the input list"


def test_explain_choice_format():
    """explain_choice() returns the exact one-line formats"""
    got = explain_choice(TABLE, 0.90, 3000, 15.00)
    want = "Model D: quality 0.91, p95 2600 ms, $6.00/1k requests (2 of 4 qualified)"
    assert got == want, f"expected {want!r}, got {got!r}"
    got = explain_choice(TABLE, 0.98, 3000, 15.00)
    want = "No model qualifies: 0 of 4 meet quality >= 0.98, p95 <= 3000 ms, cost <= $15.00/1k"
    assert got == want, f"expected {want!r}, got {got!r}"
