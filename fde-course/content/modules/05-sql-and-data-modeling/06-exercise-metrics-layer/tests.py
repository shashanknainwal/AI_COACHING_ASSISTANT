import sqlite3
from fde_datasets import pinecrest


def _db():
    assert VIEWS_SQL.strip(), "write VIEWS_SQL first"
    db = pinecrest.connect()
    try:
        db.executescript(VIEWS_SQL)
    except sqlite3.Error as e:
        raise AssertionError(f"SQL error while creating views: {e}")
    return db


def _cols(db, view):
    return [d[0] for d in db.execute(f"SELECT * FROM {view} LIMIT 0").description]


def test_views_exist_with_columns():
    """All three views exist with the specified columns"""
    db = _db()
    views = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type = 'view'")}
    for v in ["v_location_monthly_visits", "v_location_monthly_revenue", "v_location_kpis"]:
        assert v in views, f"view {v} is missing (create it with CREATE VIEW)"
    assert _cols(db, "v_location_monthly_visits") == ["location", "month", "visits", "unique_visitors"]
    assert _cols(db, "v_location_monthly_revenue") == ["location", "month", "revenue"]
    assert _cols(db, "v_location_kpis") == ["location", "month", "revenue", "visits", "unique_visitors", "revenue_per_visitor"]


def test_visits_view():
    """v_location_monthly_visits counts visits and unique visitors where the visit happened"""
    db = _db()
    got = db.execute("SELECT visits, unique_visitors FROM v_location_monthly_visits WHERE location = 'Riverside' AND month = '2026-03'").fetchone()
    assert got == (128, 32), f"Riverside March: expected (128, 32), got {got}"
    assert db.execute("SELECT SUM(visits) FROM v_location_monthly_visits").fetchone()[0] == 2538, "visits should total 2538"


def test_revenue_view():
    """v_location_monthly_revenue uses the payer's home location"""
    db = _db()
    got = db.execute("SELECT revenue FROM v_location_monthly_revenue WHERE location = 'Lakeshore' AND month = '2025-12'").fetchone()
    assert got == (293.0,), f"Lakeshore December: expected 293.0, got {got}"


def test_no_fan_out():
    """Total revenue in v_location_kpis equals total payments (no fan-out)"""
    db = _db()
    total = db.execute("SELECT ROUND(SUM(revenue), 2), COUNT(*) FROM v_location_kpis").fetchone()
    assert total == (18192.0, 24), f"expected 24 location-months totaling 18192.0, got {total}; join the views, not payments x visits"


def test_kpis_values():
    """v_location_kpis computes revenue_per_visitor"""
    db = _db()
    got = db.execute("SELECT revenue, visits, unique_visitors, revenue_per_visitor FROM v_location_kpis WHERE location = 'Riverside' AND month = '2026-03'").fetchone()
    assert got == (1436.0, 128, 32, 44.88), f"Riverside March: got {got}"


def test_kpis_without_visits_is_null_not_error():
    """A month with revenue but no visits gives NULL visits and NULL revenue_per_visitor"""
    db = _db()
    db.execute("INSERT INTO payments (member_id, amount, paid_on) VALUES (1, 29.0, '2026-04-01')")
    got = db.execute("SELECT revenue, visits, revenue_per_visitor FROM v_location_kpis WHERE month = '2026-04'").fetchall()
    assert got == [(29.0, None, None)], f"expected [(29.0, None, None)], got {got} (LEFT JOIN + NULLIF)"


def test_kpi_function():
    """kpi() returns a dict for a location-month, or None"""
    db = _db()
    got = kpi(db, "Riverside", "2026-03")
    assert got == {"location": "Riverside", "month": "2026-03", "revenue": 1436.0, "visits": 128,
                   "unique_visitors": 32, "revenue_per_visitor": 44.88}, f"got {got}"
    assert kpi(db, "Atlantis", "2026-03") is None, "an unknown location should return None"
    assert kpi(db, "Riverside'; DROP TABLE visits; --", "2026-03") is None, "use query parameters, not string formatting"
