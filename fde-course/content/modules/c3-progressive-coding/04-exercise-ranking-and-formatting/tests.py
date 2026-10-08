import copy


def _e(user, points, t):
    return {"user": user, "points": points, "t": t}


def test_totals_and_format():
    """leaderboard sums each user's points and formats each entry as name(total)"""
    events = [_e("maya", 30, 1), _e("leo", 50, 2), _e("maya", 40, 3)]
    got = leaderboard(events, 2)
    assert got == ["maya(70)", "leo(50)"], f"expected ['maya(70)', 'leo(50)'], got {got!r}"


def test_tie_broken_by_earliest_reach_time():
    """Equal totals: the user who reached the total first ranks higher"""
    events = [_e("zed", 20, 1), _e("amy", 50, 2), _e("zed", 30, 3)]
    got = leaderboard(events, 2)
    assert got == ["amy(50)", "zed(50)"], (
        f"amy reached 50 at t=2, zed at t=3, so amy ranks first; got {got!r}"
    )


def test_reach_time_is_latest_event_even_if_unordered():
    """Events can arrive out of order; a user reaches their total at their latest event"""
    events = [_e("bo", 10, 8), _e("cy", 30, 4), _e("bo", 20, 1)]
    got = leaderboard(events, 2)
    assert got == ["cy(30)", "bo(30)"], (
        f"bo's events are at t=1 and t=8, so bo reached 30 at t=8, after cy at t=4; got {got!r}"
    )


def test_tie_on_total_and_time_broken_by_name():
    """Equal totals reached at the same time: sort by name"""
    events = [_e("rui", 40, 5), _e("eva", 40, 5), _e("max", 10, 1)]
    got = leaderboard(events, 3)
    assert got == ["eva(40)", "rui(40)", "max(10)"], f"expected name order on a full tie, got {got!r}"


def test_n_larger_than_users_and_n_zero():
    """n larger than the number of users returns everyone; n of 0 returns []"""
    events = [_e("a", 5, 1), _e("b", 7, 2)]
    got = leaderboard(events, 10)
    assert got == ["b(7)", "a(5)"], f"with n=10 and 2 users, return both; got {got!r}"
    got = leaderboard(events, 0)
    assert got == [], f"n=0 should return [], got {got!r}"


def test_empty_input():
    """No events: leaderboard returns [] and window_totals returns {}"""
    got = leaderboard([], 3)
    assert got == [], f"leaderboard([], 3) should be [], got {got!r}"
    got = window_totals([], 0, 100)
    assert got == {}, f"window_totals([], 0, 100) should be {{}}, got {got!r}"


def test_window_start_inclusive_end_exclusive():
    """window_totals includes t == start and excludes t == end"""
    events = [_e("a", 1, 9), _e("a", 2, 10), _e("b", 4, 15), _e("a", 8, 20), _e("c", 16, 21)]
    got = window_totals(events, 10, 20)
    assert got == {"a": 2, "b": 4}, (
        f"start=10 is included and end=20 is excluded, so expected {{'a': 2, 'b': 4}}; got {got!r}"
    )


def test_inputs_not_modified():
    """Neither function changes the events list"""
    events = [_e("a", 3, 2), _e("b", 5, 1)]
    before = copy.deepcopy(events)
    leaderboard(events, 2)
    window_totals(events, 0, 5)
    assert events == before, "don't modify the input list or its dicts"
