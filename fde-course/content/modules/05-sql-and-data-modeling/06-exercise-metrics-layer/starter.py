from fde_datasets import pinecrest

con = pinecrest.connect()


VIEWS_SQL = """
"""


def kpi(con, location, month):
    """One row of v_location_kpis as a dict, or None."""
    # TODO
    pass


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
