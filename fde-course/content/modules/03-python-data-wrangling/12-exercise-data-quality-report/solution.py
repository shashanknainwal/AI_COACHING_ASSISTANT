import csv
import io
import re
from collections import Counter

MISSING_TOKENS = {"", "n/a", "na", "null", "none", "-", "unknown"}

CRM_CSV = """account_id,name,email,industry,annual_revenue,owner
A-1001,Acme Corp,buyer@acme.com,Manufacturing,1200000,jlee
A-1002,Birch & Co,,Retail,N/A,mpatel
A-1003,Cobalt Rigging,ops@cobaltrigging.com,Construction,850000,jlee
A-1004,acme corporation,jim@acme,Manufacturing,"1,200,000",
A-1005,Delta Fasteners,sales at delta.com,Unknown,-,skim
A-1006,Evergreen Tools,ap@evergreentools.com,Retail,2450000.50,mpatel
A-1007,Falcon Hydraulics,jim.falcon@gmail.com,Manufacturing,990000,jlee
A-1008,Granite Works,orders@graniteworks.com,Construction,410000,skim
A-1009,Harbor Marine Supply,,Marine,,mpatel
A-1003,Cobalt Rigging LLC,ops@cobaltrigging.com,Construction,850000,jlee
A-1011,Ironclad Safety,sales@ironclad-safety.com,Manufacturing,3100000,skim
A-1012,Juniper Electric,billing@juniper-electric.com,Utilities,275000.75,jlee
A-1013,Keystone Pumps,,Manufacturing,1750000,mpatel
A-1014,Lakeside Lumber,info@lakesidelumber,Retail,190000,skim
A-1015,Meridian Valves,purchasing@meridianvalves.com,Manufacturing,6200000,jlee
A-1016,Northwind Bearings,ap@northwind-bearings.com,Utilities,880000,mpatel
"""

ROWS = list(csv.DictReader(io.StringIO(CRM_CSV)))

RULES = [
    {"name": "email present", "column": "email", "check": "required"},
    {"name": "email format", "column": "email", "check": "regex", "pattern": r"[^@\s]+@[^@\s]+\.[a-z]{2,}"},
    {"name": "account id unique", "column": "account_id", "check": "unique"},
    {"name": "revenue numeric", "column": "annual_revenue", "check": "numeric"},
    {"name": "industry allowed", "column": "industry", "check": "allowed",
     "values": ["Manufacturing", "Retail", "Construction", "Utilities", "Marine"]},
    {"name": "owner present", "column": "owner", "check": "required"},
]


def is_missing(value):
    return value is None or value.strip().lower() in MISSING_TOKENS


def evaluate_rule(rows, rule):
    values = [r.get(rule["column"]) for r in rows]
    check = rule["check"]
    if check == "required":
        checked = len(values)
        failed = sum(1 for v in values if is_missing(v))
    elif check == "unique":
        present = [v.strip() for v in values if not is_missing(v)]
        counts = Counter(present)
        checked = len(values)
        failed = sum(1 for v in present if counts[v] > 1)
    else:
        present = [v.strip() for v in values if not is_missing(v)]
        checked = len(present)
        if check == "regex":
            failed = sum(1 for v in present if not re.fullmatch(rule["pattern"], v))
        elif check == "numeric":
            failed = sum(1 for v in present if not re.fullmatch(r"-?\d+(\.\d+)?", v))
        elif check == "allowed":
            failed = sum(1 for v in present if v not in rule["values"])
        else:
            raise ValueError(f"unknown check: {check}")
    pass_rate = round((checked - failed) / checked * 100, 1) if checked else 100.0
    return {"name": rule["name"], "checked": checked, "failed": failed, "pass_rate": pass_rate}


def severity(pass_rate):
    if pass_rate < 90:
        return "critical"
    if pass_rate < 98:
        return "warning"
    return "ok"


def dq_report(rows, rules, title):
    results = sorted((evaluate_rule(rows, r) for r in rules), key=lambda r: (r["pass_rate"], r["name"]))
    lines = [
        f"# {title}",
        f"{len(rows)} rows checked against {len(rules)} rules.",
        "",
        "| Rule | Checked | Failed | Pass rate | Severity |",
        "|---|---|---|---|---|",
    ]
    tally = Counter()
    for r in results:
        level = severity(r["pass_rate"])
        tally[level] += 1
        lines.append(f"| {r['name']} | {r['checked']} | {r['failed']} | {r['pass_rate']:.1f}% | {level} |")
    lines.append("")
    lines.append(f"Critical: {tally['critical']}, warnings: {tally['warning']}, ok: {tally['ok']}")
    return "\n".join(lines)


# --- Try it out (not graded) ---
print(dq_report(ROWS, RULES, "Cobalt CRM data quality"))
