from datetime import datetime, timedelta
import requests

BASE = "https://api.northwind.example"
TIMEOUT = 10
PAGE_SIZE = 50
ISO = "%Y-%m-%dT%H:%M:%SZ"
OVERLAP_MINUTES = 5
INITIAL_WATERMARK = "1970-01-01T00:00:00Z"
LBS_TO_KG = 0.45359237

REQUIRED = ["id", "status_code", "weight_lbs", "charge_cents", "updated_at"]
STATUS_MAP = {"PU": "picked_up", "IT": "in_transit", "DL": "delivered", "EX": "exception"}


def map_record(src):
    """Translate a Northwind shipment into the ERP schema."""
    # TODO
    pass


def overlap_since(watermark):
    """watermark minus OVERLAP_MINUTES, in ISO format."""
    # TODO
    pass


def fetch_changes(session, watermark):
    """All shipments updated since overlap_since(watermark), across pages."""
    # TODO
    pass


def sync(session, target, watermark):
    """One sync run. Upserts into target and returns the summary dict."""
    # TODO
    pass


# --- Try it out (not graded) ---
session = requests.Session()
session.headers["Authorization"] = "Bearer nw_test_token"
erp = {}

first = sync(session, erp, INITIAL_WATERMARK)
print("Run 1 (full):       ", first)
if first:
    again = sync(session, erp, first["watermark"])
    print("Run 2 (no changes): ", again)
    simulate_new_changes()
    third = sync(session, erp, again["watermark"])
    print("Run 3 (incremental):", third)
    print("\nSHP-1003 in the ERP:", erp.get("SHP-1003"))
