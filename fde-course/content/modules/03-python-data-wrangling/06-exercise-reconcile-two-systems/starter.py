import csv
import io
import re

FIELD_MAP = [("plan", "plan"), ("mrr", "monthly_amount")]

CRM_CSV = """account_id,name,plan,mrr
A-1001,Acme Corp,Enterprise,4800.00
A-1003,Cobalt Rigging,Pro,850.00
A-1004,acme corporation,Pro,1200.00
A-1006,Evergreen Tools,Enterprise,2450.50
A-1007,Falcon Hydraulics,Pro,990.00
A-1009,Harbor Marine Supply,Basic,150.00
A-1011,Ironclad Safety,Enterprise,3100.00
A-1012,Juniper Electric,Starter,275.75
A-1013,Keystone Pumps,Pro,1750.00
A-1014,Lakeside Lumber,Basic,190.00
A-1015,Meridian Valves,Enterprise,6200.00
A-1016,Northwind Bearings,Pro,880.00
"""

BILLING_CSV = """customer_ref,customer_name,plan,monthly_amount
a1001,ACME CORP,enterprise,4800
A-01003,Cobalt Rigging LLC,Pro,850.00
a1004,ACME CORP,basic,1200
 A-1006 ,Evergreen Tools Inc,Enterprise,2405.50
A-1007,Falcon Hydraulics,PRO,990
A-1011,Ironclad Safety,Enterprise,3100.00
A1012,Juniper Electric Co,starter ,275.749
A-1014,Lakeside Lumber,Basic,190
A-1015,Meridian Valves,Enterprise,6000
A-1016,Northwind Bearings,Pro,880.00
A-1020,Orion Cranes,Pro,640.00
"""

CRM = list(csv.DictReader(io.StringIO(CRM_CSV)))
BILLING = list(csv.DictReader(io.StringIO(BILLING_CSV)))


def normalize_key(key):
    """Uppercase, no whitespace/hyphens, no leading zeros in the number part."""
    # TODO
    pass


def index_by_key(rows, key_field):
    """Dict of normalized key -> row. Raise ValueError on duplicate keys."""
    # TODO
    pass


def reconcile(crm_rows, billing_rows, tolerance=0.01):
    """Return matched, only_crm, only_billing and mismatches."""
    # TODO
    pass


def summary(result):
    """One-line summary of a reconciliation result."""
    # TODO
    pass


# --- Try it out (not graded) ---
result = reconcile(CRM, BILLING)
if result:
    print(summary(result))
    print("Only in CRM:    ", result["only_crm"])
    print("Only in billing:", result["only_billing"])
    for m in result["mismatches"]:
        print(f"  {m['key']:<7} {m['field']:<5} CRM={m['crm']!r:<14} Billing={m['billing']!r}")
