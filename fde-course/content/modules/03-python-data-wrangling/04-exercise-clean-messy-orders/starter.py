import csv
import io
import re
from datetime import date, datetime

MISSING_TOKENS = {"", "n/a", "na", "null", "none", "-", "unknown"}
DATE_FORMATS = ["%Y-%m-%d", "%m/%d/%Y", "%b %d %Y", "%d-%b-%Y"]
MIN_DATE = date(2000, 1, 1)
MAX_DATE = date(2030, 12, 31)

ORDERS_CSV = """order_id,account_id,order_date,amount,phone
O-501,a-1001,2026-03-04,"$1,204.50",(555) 123-4567
O-502,A-1003 ,03/05/2026,USD 880,555.987.6543 x12
O-503,A-1006,Mar 6 2026,(45.00),
O-504,A-1007,06-Mar-2026,2200,1-555-222-3333
O-505,A-1011,2026-13-01,310.00,555-444-1212
O-506,A-1012,1900-01-01,N/A,123-4567
O-507,A-1015,2026-03-07,"6,200",555 777 8888
O-501,A-1001,2026-03-04,"$1,204.50",(555) 123-4567
O-508,A-1016,2026-03-08,12.3.4,
O-509,A-1004,03/09/2026,$-3,+1 (555) 010-0199
"""

ROWS = list(csv.DictReader(io.StringIO(ORDERS_CSV)))


def is_missing(value):
    return value is None or value.strip().lower() in MISSING_TOKENS


def parse_date(text):
    """Return "YYYY-MM-DD" or None."""
    # TODO
    pass


def parse_money(text):
    """Return a float rounded to 2 decimals, or None."""
    # TODO
    pass


def normalize_phone(text):
    """Return "+1XXXXXXXXXX" or None."""
    # TODO
    pass


def clean_orders(rows):
    """Return (clean_rows, rejects)."""
    # TODO
    pass


# --- Try it out (not graded) ---
result = clean_orders(ROWS)
if result:
    clean, rejects = result
    print(f"{len(clean)} clean orders:")
    for row in clean:
        print("  ", row)
    print(f"\n{len(rejects)} rejected:")
    for r in rejects:
        print("  ", r)
