def _r(received, entered):
    return {"id": "x", "received": received, "entered": entered}


def test_hours_between():
    """hours_between() returns hours rounded to 1 decimal, across days"""
    got = hours_between("2026-02-03 08:10", "2026-02-04 14:40")
    assert got == 30.5, f"expected 30.5, got {got!r}"
    got = hours_between("2026-02-03 08:00", "2026-02-03 08:20")
    assert got == 0.3, f"20 minutes is 0.3 hours (rounded); got {got!r}"


def test_baseline_brightline():
    """baseline() matches the Brightline export"""
    got = baseline(RECORDS)
    want = {"n": 18, "open": 2, "median_hours": 48.5, "p90_hours": 104.0}
    assert got == want, f"expected {want}, got {got}"


def test_baseline_odd_count_and_outlier():
    """Median ignores the outlier; p90 uses nearest rank"""
    hours = [2, 3, 3, 4, 4, 5, 6, 8, 120]
    recs = [_r("2026-01-01 00:00", f"2026-01-{1 + h // 24:02d} {h % 24:02d}:00") for h in hours]
    got = baseline(recs)
    assert got["median_hours"] == 4.0, f"median of the lesson example should be 4.0, got {got['median_hours']!r}"
    assert got["p90_hours"] == 120.0, f"p90 (position ceil(0.9*9)=9) should be 120.0, got {got['p90_hours']!r}"


def test_baseline_even_count_full_precision():
    """With an even count the median averages the middle two, before rounding"""
    recs = [_r("2026-01-01 00:00", "2026-01-01 01:10"), _r("2026-01-01 00:00", "2026-01-01 02:05")]
    got = baseline(recs)
    # 1.1667h and 2.0833h -> median 1.625 -> 1.6. Rounding first would give (1.2 + 2.1) / 2 = 1.65.
    assert got["median_hours"] == 1.6, f"compute at full precision, round at the end; expected 1.6, got {got['median_hours']!r}"


def test_baseline_all_open():
    """baseline() handles no completed records"""
    got = baseline([_r("2026-01-01 00:00", None)])
    assert got == {"n": 0, "open": 1, "median_hours": None, "p90_hours": None}, f"got {got}"


def test_pct_within():
    """pct_within() is the share of completed records within the limit (inclusive)"""
    assert pct_within(RECORDS, 24) == 0.11, f"expected 0.11 within 24h, got {pct_within(RECORDS, 24)!r}"
    assert pct_within(RECORDS, 48) == 0.5, f"expected 0.5 within 48h, got {pct_within(RECORDS, 48)!r}"
    recs = [_r("2026-01-01 00:00", "2026-01-01 08:00"), _r("2026-01-01 00:00", "2026-01-01 09:00")]
    assert pct_within(recs, 8) == 0.5, "a record that took exactly the limit counts as within it"
    assert pct_within([_r("2026-01-01 00:00", None)], 8) == 0.0, "no completed records should give 0.0"


def _m(**overrides):
    m = {"name": "Intake time", "baseline": 48.5, "target": 8, "direction": "decrease", "deadline": "2026-06-30", "owner": "Priya"}
    m.update(overrides)
    return m


def test_validate_good_metric():
    """validate_metric() returns [] for a complete, improving metric"""
    assert validate_metric(_m()) == [], f"got {validate_metric(_m())!r}"
    assert validate_metric(_m(direction="increase", baseline=0.6, target=0.9)) == [], "an increasing metric that goes up is fine"


def test_validate_missing_fields_in_order():
    """Missing, None or empty fields are reported in REQUIRED_FIELDS order"""
    m = _m(owner="", baseline=None)
    del m["deadline"]
    got = validate_metric(m)
    assert got == ["missing baseline", "missing deadline", "missing owner"], f"got {got!r}"


def test_validate_direction_and_improvement():
    """Bad direction and non-improving targets are caught"""
    assert validate_metric(_m(direction="down")) == ["invalid direction"], f"got {validate_metric(_m(direction='down'))!r}"
    got = validate_metric(_m(target=48.5))
    assert got == ["target does not improve on baseline"], f"a target equal to the baseline isn't an improvement; got {got!r}"
    got = validate_metric(_m(direction="increase", baseline=0.6, target=0.5))
    assert got == ["target does not improve on baseline"], f"got {got!r}"


def test_validate_zero_is_a_value():
    """A baseline or target of 0 counts as present"""
    got = validate_metric(_m(direction="increase", baseline=0, target=5))
    assert got == [], f"0 is a real baseline, not a missing one; got {got!r}"
