from fde_datasets import pinecrest

con = pinecrest.connect()


Q_FIRST_VISIT = """
"""

Q_REVENUE_GROWTH = """
"""

Q_SIGNUPS = """
"""


def month_offset(a, b):
    """Months from 'YYYY-MM' a to 'YYYY-MM' b."""
    # TODO
    pass


def retention_table(con, last_month="2026-03"):
    """{cohort: {"size": n, "pct": [month0, month1, ...]}} ordered by cohort."""
    # TODO
    pass


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
