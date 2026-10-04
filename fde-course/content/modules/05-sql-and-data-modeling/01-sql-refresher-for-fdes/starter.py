from fde_datasets import pinecrest

con = pinecrest.connect()

# 1. What tables are there?
for name, sql in con.execute("SELECT name, sql FROM sqlite_master WHERE type = 'table'"):
    count = con.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
    print(f"{name:<14} {count:>5} rows")

# 2. Look at real rows
print()
cur = con.execute("SELECT * FROM subscriptions LIMIT 5")
print([d[0] for d in cur.description])
for row in cur.fetchall():
    print(row)

# 3. A first business question: active members per location
print()
query = """
SELECT l.name, COUNT(*) AS active_members
FROM subscriptions s
JOIN members m   ON m.id = s.member_id
JOIN locations l ON l.id = m.home_location_id
WHERE s.status = 'active'
GROUP BY l.name
ORDER BY active_members DESC
"""
for row in con.execute(query):
    print(row)

# Try it: how many members are on each plan? (Join subscriptions to plans.)
