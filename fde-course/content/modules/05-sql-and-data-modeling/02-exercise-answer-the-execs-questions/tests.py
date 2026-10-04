import sqlite3
from fde_datasets import pinecrest


def _check(sql, columns, rows):
    assert sql.strip(), "write the query first"
    db = pinecrest.connect()
    try:
        cur = db.execute(sql)
    except sqlite3.Error as e:
        raise AssertionError(f"SQL error: {e}")
    got_cols = [d[0] for d in cur.description]
    got = cur.fetchall()
    assert got_cols == columns, f"columns should be {columns}, got {got_cols} (use AS to name them)"
    assert len(got) == len(rows), f"expected {len(rows)} rows, got {len(got)}: {got}"
    for i, (g, w) in enumerate(zip(got, rows)):
        assert tuple(g) == tuple(w), f"row {i + 1}: expected {w}, got {tuple(g)}"


def test_q1_active_by_location():
    """Q1: active members per home location, most first"""
    _check(Q1_ACTIVE_BY_LOCATION, ["location", "active_members"],
           [("Downtown", 31), ("Riverside", 30), ("Northgate", 23), ("Lakeshore", 16)])


def test_q2_monthly_revenue():
    """Q2: revenue per month for January to March 2026"""
    _check(Q2_MONTHLY_REVENUE, ["month", "revenue"], [("2026-01", 3657.0), ("2026-02", 4220.0), ("2026-03", 4624.0)])


def test_q3_quiet_locations():
    """Q3: locations with fewer than 200 visits in March (HAVING)"""
    _check(Q3_QUIET_LOCATIONS, ["location", "visits"], [("Lakeshore", 108), ("Riverside", 128)])


def test_q4_never_visited():
    """Q4: members with no visits, per home location (anti-join)"""
    _check(Q4_NEVER_VISITED, ["location", "never_visited"],
           [("Riverside", 19), ("Lakeshore", 4), ("Northgate", 4), ("Downtown", 1)])


def test_q5_churn_by_location():
    """Q5: churn percentage per home location"""
    _check(Q5_CHURN_BY_LOCATION, ["location", "members", "cancelled", "churn_pct"],
           [("Riverside", 41, 11, 26.8), ("Downtown", 37, 6, 16.2), ("Northgate", 25, 2, 8.0), ("Lakeshore", 17, 1, 5.9)])


def test_biggest_churn_location():
    """biggest_churn_location() returns the top row of Q5"""
    got = biggest_churn_location(pinecrest.connect())
    assert got == "Riverside", f"expected 'Riverside', got {got!r}"
