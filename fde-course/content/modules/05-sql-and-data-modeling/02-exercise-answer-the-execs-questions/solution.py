from fde_datasets import pinecrest

con = pinecrest.connect()


def run(con, sql, params=()):
    """Execute a query and return all rows as a list of tuples."""
    return con.execute(sql, params).fetchall()


Q1_ACTIVE_BY_LOCATION = """
SELECT l.name AS location, COUNT(*) AS active_members
FROM subscriptions s
JOIN members m   ON m.id = s.member_id
JOIN locations l ON l.id = m.home_location_id
WHERE s.status = 'active'
GROUP BY l.name
ORDER BY active_members DESC, location
"""

Q2_MONTHLY_REVENUE = """
SELECT strftime('%Y-%m', paid_on) AS month, ROUND(SUM(amount), 2) AS revenue
FROM payments
WHERE paid_on >= '2026-01-01' AND paid_on < '2026-04-01'
GROUP BY month
ORDER BY month
"""

Q3_QUIET_LOCATIONS = """
SELECT l.name AS location, COUNT(*) AS visits
FROM visits v
JOIN locations l ON l.id = v.location_id
WHERE v.visited_at >= '2026-03-01' AND v.visited_at < '2026-04-01'
GROUP BY l.name
HAVING COUNT(*) < 200
ORDER BY visits
"""

Q4_NEVER_VISITED = """
SELECT l.name AS location, COUNT(*) AS never_visited
FROM members m
JOIN locations l ON l.id = m.home_location_id
LEFT JOIN visits v ON v.member_id = m.id
WHERE v.id IS NULL
GROUP BY l.name
ORDER BY never_visited DESC, location
"""

Q5_CHURN_BY_LOCATION = """
SELECT l.name AS location,
       COUNT(*) AS members,
       SUM(s.status = 'cancelled') AS cancelled,
       ROUND(100.0 * SUM(s.status = 'cancelled') / COUNT(*), 1) AS churn_pct
FROM subscriptions s
JOIN members m   ON m.id = s.member_id
JOIN locations l ON l.id = m.home_location_id
GROUP BY l.name
ORDER BY churn_pct DESC
"""


def biggest_churn_location(con):
    return run(con, Q5_CHURN_BY_LOCATION)[0][0]


# --- Try it out (not graded) ---
for name in ["Q1_ACTIVE_BY_LOCATION", "Q2_MONTHLY_REVENUE", "Q3_QUIET_LOCATIONS", "Q4_NEVER_VISITED", "Q5_CHURN_BY_LOCATION"]:
    sql = globals()[name]
    print(name)
    if sql.strip():
        cur = con.execute(sql)
        print("  ", [d[0] for d in cur.description])
        for row in cur.fetchall():
            print("  ", row)
    else:
        print("   (not written yet)")
print("\nBiggest churn:", biggest_churn_location(con))
