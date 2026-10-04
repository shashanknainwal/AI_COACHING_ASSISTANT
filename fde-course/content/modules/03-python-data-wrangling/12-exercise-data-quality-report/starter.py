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
    """Return {"name", "checked", "failed", "pass_rate"} for one rule."""
    # TODO
    pass


def severity(pass_rate):
    """'critical' below 90, 'warning' below 98, otherwise 'ok'."""
    # TODO
    pass


def dq_report(rows, rules, title):
    """Markdown data-quality report, worst rule first."""
    # TODO
    pass


# --- Try it out (not graded) ---
print(dq_report(ROWS, RULES, "Cobalt CRM data quality"))
