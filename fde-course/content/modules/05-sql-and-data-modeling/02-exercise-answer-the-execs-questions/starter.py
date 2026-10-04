from fde_datasets import pinecrest

con = pinecrest.connect()


def run(con, sql, params=()):
    """Execute a query and return all rows as a list of tuples."""
    return con.execute(sql, params).fetchall()


Q1_ACTIVE_BY_LOCATION = """
"""

Q2_MONTHLY_REVENUE = """
"""

Q3_QUIET_LOCATIONS = """
"""

Q4_NEVER_VISITED = """
"""

Q5_CHURN_BY_LOCATION = """
"""


def biggest_churn_location(con):
    """Name of the location with the highest churn_pct, using Q5."""
    # TODO
    pass


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
