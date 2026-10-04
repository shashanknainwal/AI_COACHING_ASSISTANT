from fde_datasets import pinecrest

con = pinecrest.connect()


Q_FIRST_VISIT = """
WITH ranked AS (
    SELECT member_id, visited_at, location_id,
           ROW_NUMBER() OVER (PARTITION BY member_id ORDER BY visited_at, id) AS n
    FROM visits
)
SELECT member_id, visited_at AS first_visit, location_id
FROM ranked
WHERE n = 1
ORDER BY member_id
"""

Q_REVENUE_GROWTH = """
WITH monthly AS (
    SELECT strftime('%Y-%m', paid_on) AS month, ROUND(SUM(amount), 2) AS revenue
    FROM payments
    GROUP BY month
),
with_prev AS (
    SELECT month, revenue, LAG(revenue) OVER (ORDER BY month) AS prev_revenue
    FROM monthly
)
SELECT month, revenue, prev_revenue,
       ROUND(100.0 * (revenue - prev_revenue) / prev_revenue, 1) AS pct_change
FROM with_prev
ORDER BY month
"""

Q_SIGNUPS = """
WITH monthly AS (
    SELECT strftime('%Y-%m', joined_on) AS month, COUNT(*) AS new_members
    FROM members
    GROUP BY month
)
SELECT month, new_members, SUM(new_members) OVER (ORDER BY month) AS total_members
FROM monthly
ORDER BY month
"""


def month_offset(a, b):
    return (int(b[:4]) - int(a[:4])) * 12 + (int(b[5:7]) - int(a[5:7]))


def retention_table(con, last_month="2026-03"):
    sizes = dict(con.execute(
        "SELECT strftime('%Y-%m', joined_on) AS cohort, COUNT(*) FROM members GROUP BY cohort ORDER BY cohort"
    ).fetchall())
    active = {}
    rows = con.execute("""
        SELECT DISTINCT v.member_id, strftime('%Y-%m', m.joined_on), strftime('%Y-%m', v.visited_at)
        FROM visits v JOIN members m ON m.id = v.member_id
    """).fetchall()
    for _member, cohort, month in rows:
        key = (cohort, month_offset(cohort, month))
        active[key] = active.get(key, 0) + 1
    table = {}
    for cohort, size in sizes.items():
        months = month_offset(cohort, last_month) + 1
        pct = [round(100 * active.get((cohort, k), 0) / size) for k in range(months)]
        table[cohort] = {"size": size, "pct": pct}
    return table


# --- Try it out (not graded) ---
for name in ["Q_FIRST_VISIT", "Q_REVENUE_GROWTH", "Q_SIGNUPS"]:
    sql = globals()[name]
    print(name)
    if sql.strip():
        cur = con.execute(sql)
        print("  ", [d[0] for d in cur.description])
        for row in cur.fetchall()[:6]:
            print("  ", row)
    else:
        print("   (not written yet)")

table = retention_table(con)
if table:
    print("\ncohort   size  " + "  ".join(f"m{k:<3}" for k in range(6)))
    for cohort, r in table.items():
        print(f"{cohort}  {r['size']:>4}  " + "  ".join(f"{p:>3}%" for p in r["pct"]))
