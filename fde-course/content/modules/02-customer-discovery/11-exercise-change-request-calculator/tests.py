def _w(id, days, priority):
    return {"id": id, "title": id, "days": days, "priority": priority}


def test_plan_load():
    """plan_load() sums the days"""
    assert plan_load(PLAN) == 25, f"expected 25, got {plan_load(PLAN)!r}"
    assert plan_load([]) == 0, "an empty plan has 0 days"


def test_accept_when_it_fits():
    """A change that fits is accepted, at exactly full capacity too"""
    got = evaluate_change([_w("A", 5, "must")], 10, _w("CR", 5, "could"))
    assert got == {"decision": "accept", "drop": [], "slip_days": 0}, f"5 + 5 <= 10 should be accepted; got {got}"


def test_defer_could_changes():
    """A 'could' change that doesn't fit is deferred, never swapped"""
    got = evaluate_change(PLAN, CAPACITY, REQUESTS[1])
    assert got == {"decision": "defer", "drop": [], "slip_days": 0}, f"got {got}"


def test_swap_lumen():
    """CR-3 swaps out W5, W6, W3 in that order"""
    got = evaluate_change(PLAN, CAPACITY, REQUESTS[0])
    assert got == {"decision": "swap", "drop": ["W5", "W6", "W3"], "slip_days": 0}, f"got {got}"


def test_swap_only_strictly_lower_priority():
    """A 'should' change can only displace 'could' items"""
    plan = [_w("M", 8, "must"), _w("S", 1, "should"), _w("C", 1, "could")]
    got = evaluate_change(plan, 10, _w("CR", 1, "should"))
    assert got == {"decision": "swap", "drop": ["C"], "slip_days": 0}, f"only the 'could' item may be dropped; got {got}"


def test_swap_largest_first_and_stops_early():
    """Within a priority the largest goes first, and dropping stops once it fits"""
    plan = [_w("M", 6, "must"), _w("C1", 1, "could"), _w("C2", 3, "could"), _w("C3", 3, "could")]
    got = evaluate_change(plan, 13, _w("CR", 3, "must"))
    # load 13 + 3 = 16 > 13; drop C2 (3, id before C3) -> 13 fits
    assert got == {"decision": "swap", "drop": ["C2"], "slip_days": 0}, f"got {got}"


def test_slip_when_swap_cannot_fit():
    """If dropping every lower-priority item isn't enough, it's a slip with no drops"""
    got = evaluate_change(PLAN, CAPACITY, REQUESTS[2])
    assert got == {"decision": "slip", "drop": [], "slip_days": 20}, f"got {got}"
    got = evaluate_change([_w("M", 10, "must")], 10, _w("CR", 4, "must"))
    assert got == {"decision": "slip", "drop": [], "slip_days": 4}, f"a must change can't displace must work; got {got}"


def test_does_not_mutate_plan():
    """evaluate_change() doesn't modify the plan"""
    plan = [dict(w) for w in PLAN]
    evaluate_change(plan, CAPACITY, REQUESTS[0])
    assert plan == PLAN, "the plan was modified"


def test_change_notes():
    """change_note() writes the right message for each decision"""
    cr = _w("CR-9", 6, "must")
    cases = [
        ({"decision": "accept", "drop": [], "slip_days": 0}, "CR-9 accepted: fits in current capacity."),
        ({"decision": "defer", "drop": [], "slip_days": 0}, "CR-9 deferred to the next phase."),
        ({"decision": "swap", "drop": ["W5", "W6"], "slip_days": 0}, "CR-9 fits if we defer: W5, W6."),
        ({"decision": "slip", "drop": [], "slip_days": 7}, "CR-9 adds 7 days; the deadline moves unless we cut scope."),
    ]
    for result, want in cases:
        got = change_note(cr, result)
        assert got == want, f"for {result['decision']}: expected {want!r}, got {got!r}"
