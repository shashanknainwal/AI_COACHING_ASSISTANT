import sqlite3
from fde_datasets import pinecrest


def _rows(sql):
    assert sql.strip(), "write the query first"
    db = pinecrest.connect()
    try:
        cur = db.execute(sql)
    except sqlite3.Error as e:
        raise AssertionError(f"SQL error: {e}")
    return [d[0] for d in cur.description], [tuple(r) for r in cur.fetchall()], db


def test_first_visit():
    """Q_FIRST_VISIT: one row per visiting member, with the first visit's location"""
    cols, rows, db = _rows(Q_FIRST_VISIT)
    assert cols == ["member_id", "first_visit", "location_id"], f"columns: {cols}"
    assert len(rows) == 92, f"92 members have visited; got {len(rows)} rows"
    assert rows[:3] == [(1, "2025-10-13 20:31", 1), (2, "2025-12-26 19:56", 1), (4, "2025-11-24 16:19", 3)], f"first rows: {rows[:3]}"
    earliest = dict(db.execute("SELECT member_id, MIN(visited_at) FROM visits GROUP BY member_id").fetchall())
    for member_id, first, _loc in rows:
        assert earliest[member_id] == first, f"member {member_id}: first visit should be {earliest[member_id]}, got {first}"
    assert [r[0] for r in rows] == sorted(r[0] for r in rows), "order by member_id"


def test_revenue_growth():
    """Q_REVENUE_GROWTH: LAG gives the previous month; first month is NULL"""
    cols, rows, _ = _rows(Q_REVENUE_GROWTH)
    assert cols == ["month", "revenue", "prev_revenue", "pct_change"], f"columns: {cols}"
    want = [("2025-10", 1174.0, None, None), ("2025-11", 1779.0, 1174.0, 51.5), ("2025-12", 2738.0, 1779.0, 53.9),
            ("2026-01", 3657.0, 2738.0, 33.6), ("2026-02", 4220.0, 3657.0, 15.4), ("2026-03", 4624.0, 4220.0, 9.6)]
    assert rows == want, f"expected {want}, got {rows}"


def test_signups():
    """Q_SIGNUPS: new members per month and a running total"""
    cols, rows, _ = _rows(Q_SIGNUPS)
    assert cols == ["month", "new_members", "total_members"], f"columns: {cols}"
    want = [("2025-10", 26, 26), ("2025-11", 15, 41), ("2025-12", 23, 64), ("2026-01", 23, 87), ("2026-02", 22, 109), ("2026-03", 11, 120)]
    assert rows == want, f"expected {want}, got {rows}"


def test_month_offset():
    """month_offset() counts months across year boundaries"""
    cases = [("2025-11", "2026-02", 3), ("2026-03", "2026-03", 0), ("2025-01", "2025-12", 11), ("2024-12", "2026-01", 13)]
    for a, b, want in cases:
        assert month_offset(a, b) == want, f"month_offset({a!r}, {b!r}) should be {want}, got {month_offset(a, b)!r}"


def test_retention_table():
    """retention_table() matches Pinecrest's real cohorts"""
    got = retention_table(pinecrest.connect())
    want = {
        "2025-10": {"size": 26, "pct": [73, 77, 69, 69, 65, 65]},
        "2025-11": {"size": 15, "pct": [80, 80, 73, 60, 53]},
        "2025-12": {"size": 23, "pct": [78, 83, 70, 70]},
        "2026-01": {"size": 23, "pct": [65, 74, 74]},
        "2026-02": {"size": 22, "pct": [64, 64]},
        "2026-03": {"size": 11, "pct": [91]},
    }
    assert isinstance(got, dict), "return a dict"
    assert list(got) == list(want), f"cohorts (in order): expected {list(want)}, got {list(got)}"
    for cohort, w in want.items():
        assert got[cohort]["size"] == w["size"], f"{cohort} size: expected {w['size']} (include members who never visited), got {got[cohort]['size']}"
        assert got[cohort]["pct"] == w["pct"], f"{cohort} pct: expected {w['pct']}, got {got[cohort]['pct']}"


def test_retention_last_month_parameter():
    """last_month controls how many months each cohort shows"""
    got = retention_table(pinecrest.connect(), last_month="2026-01")
    assert got["2025-10"]["pct"] == [73, 77, 69, 69], f"through 2026-01 the Oct cohort has 4 months; got {got['2025-10']['pct']}"
    assert got["2026-01"]["pct"] == [65], f"got {got['2026-01']['pct']}"
