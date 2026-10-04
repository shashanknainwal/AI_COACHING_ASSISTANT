from fde_datasets import pinecrest

con = pinecrest.connect()


VIEWS_SQL = """
CREATE VIEW v_location_monthly_visits AS
SELECT l.name AS location,
       strftime('%Y-%m', v.visited_at) AS month,
       COUNT(*) AS visits,
       COUNT(DISTINCT v.member_id) AS unique_visitors
FROM visits v
JOIN locations l ON l.id = v.location_id
GROUP BY location, month;

CREATE VIEW v_location_monthly_revenue AS
SELECT l.name AS location,
       strftime('%Y-%m', p.paid_on) AS month,
       ROUND(SUM(p.amount), 2) AS revenue
FROM payments p
JOIN members m   ON m.id = p.member_id
JOIN locations l ON l.id = m.home_location_id
GROUP BY location, month;

CREATE VIEW v_location_kpis AS
SELECT r.location,
       r.month,
       r.revenue,
       v.visits,
       v.unique_visitors,
       ROUND(r.revenue / NULLIF(v.unique_visitors, 0), 2) AS revenue_per_visitor
FROM v_location_monthly_revenue r
LEFT JOIN v_location_monthly_visits v
       ON v.location = r.location AND v.month = r.month;
"""


def kpi(con, location, month):
    cur = con.execute("SELECT * FROM v_location_kpis WHERE location = ? AND month = ?", (location, month))
    row = cur.fetchone()
    if row is None:
        return None
    return dict(zip([d[0] for d in cur.description], row))


# --- Try it out (not graded) ---
if VIEWS_SQL.strip():
    con.executescript(VIEWS_SQL)
    cur = con.execute("SELECT * FROM v_location_kpis WHERE month >= '2026-01' ORDER BY month, location")
    print([d[0] for d in cur.description])
    for row in cur.fetchall():
        print(row)
    print("\nRiverside, March:", kpi(con, "Riverside", "2026-03"))
else:
    print("Write VIEWS_SQL first.")
