import csv
import io
import re
from collections import Counter
from datetime import datetime

MISSING_TOKENS = {"", "n/a", "na", "null", "none", "-", "unknown"}

CRM_CSV = """account_id,name,industry,employees,annual_revenue,created,owner
A-1001,Acme Corp,Manufacturing,250,1200000,2019-04-02,jlee
A-1002,Birch & Co,,12,N/A,2021-03-15,mpatel
A-1003,Cobalt Rigging,Construction,80,850000,2020-11-30,jlee
A-1004,acme corporation,Manufacturing,250,"1,200,000",2022-01-09,
A-1005,Delta Fasteners,Unknown,40,-,1900-01-01,skim
A-1006,Evergreen Tools,Retail,1400,2450000.50,2023-03-04,mpatel
A-1007,Falcon Hydraulics,Manufacturing,95,990000,2018-07-21,jlee
A-1008,Granite Works,Construction,n/a,410000,2024-02-29,skim
A-1009,Harbor Marine Supply,Marine,60,,2017-05-05,mpatel
A-1003,Cobalt Rigging LLC,Construction,80,850000,2020-11-30,jlee
A-1011,Ironclad Safety,Manufacturing,310,3100000,2021-09-12,skim
A-1012,Juniper Electric,Utilities,22,275000.75,2022-12-01,jlee
A-1013,Keystone Pumps,,150,1750000,2016-01-18,mpatel
A-1014,Lakeside Lumber,Retail,18,190000,03/15/2021,skim
A-1015,Meridian Valves,Manufacturing,500,6200000,2015-10-10,jlee
A-1016,Northwind Bearings,Utilities,75,880000,2020-06-30,mpatel
"""

ROWS = list(csv.DictReader(io.StringIO(CRM_CSV)))


def is_missing(value):
    return value is None or value.strip().lower() in MISSING_TOKENS


def _is_iso_date(v):
    try:
        datetime.strptime(v, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def infer_type(values):
    present = [v.strip() for v in values if not is_missing(v)]
    if not present:
        return "empty"
    if all(re.fullmatch(r"-?\d+", v) for v in present):
        return "int"
    if all(re.fullmatch(r"-?\d+(\.\d+)?", v) for v in present):
        return "float"
    if all(_is_iso_date(v) for v in present):
        return "date"
    return "text"


def profile_column(rows, column):
    values = [r.get(column) for r in rows]
    present = [v.strip() for v in values if not is_missing(v)]
    missing = len(values) - len(present)
    counts = Counter(present)
    top = min(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0] if counts else None
    return {
        "column": column,
        "missing": missing,
        "missing_pct": round(missing / len(values) * 100, 1) if values else 0.0,
        "distinct": len(counts),
        "top": top,
        "type": infer_type(values),
    }


def profile(rows):
    if not rows:
        return []
    return [profile_column(rows, c) for c in rows[0]]


def duplicate_values(rows, column):
    counts = Counter(r[column].strip() for r in rows if not is_missing(r.get(column)))
    return sorted(v for v, n in counts.items() if n > 1)


# --- Try it out (not graded) ---
print(f"{len(ROWS)} rows\n")
print(f"{'column':<15}{'missing':>8}{'pct':>7}{'distinct':>10}  {'type':<7} top")
for p in profile(ROWS) or []:
    print(f"{p['column']:<15}{p['missing']:>8}{p['missing_pct']:>7}{p['distinct']:>10}  {p['type']:<7} {p['top']}")
print("\nDuplicate account IDs:", duplicate_values(ROWS, "account_id"))
