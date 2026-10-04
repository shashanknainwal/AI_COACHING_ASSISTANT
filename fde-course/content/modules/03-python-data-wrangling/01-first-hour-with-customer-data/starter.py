import csv
import io
import random
from collections import Counter

ACCOUNTS_CSV = """account_id,name,industry,annual_revenue,created
A-001,Acme Corp,Manufacturing,"1,200,000",2019-04-02
A-002,Birch & Co,,N/A,03/15/2021
A-003,Cobalt Rigging,Construction,850000,2020-11-30
A-004,acme corporation,Manufacturing,"1,200,000",2022-01-09
A-005,Delta Fasteners,Unknown,-,1900-01-01
A-006,Evergreen Tools,Retail,"2,450,000.50",Mar 4 2023
"""

rows = list(csv.DictReader(io.StringIO(ACCOUNTS_CSV)))
print(f"{len(rows)} rows, columns: {list(rows[0])}\n")

# Step 2: look at a few random rows
for row in random.sample(rows, 3):
    print(row)

# Step 3 (preview): most common values per column
print()
for column in rows[0]:
    counts = Counter(r[column] for r in rows)
    print(f"{column:<15} distinct={len(counts):<3} top={counts.most_common(2)}")

# Try it: what problems can you spot? Write them down before the next exercise.
