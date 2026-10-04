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
    for field in REQUIRED:
        if src.get(field) in (None, ""):
            raise ValueError(f"missing {field}")
    code = src["status_code"]
    if code not in STATUS_MAP:
        raise ValueError(f"unknown status {code}")
    consignee = src.get("consignee") or {}
    return {
        "external_id": src["id"],
        "status": STATUS_MAP[code],
        "weight_kg": round(src["weight_lbs"] * LBS_TO_KG, 1),
        "charge": round(src["charge_cents"] / 100, 2),
        "customer_name": consignee.get("name"),
        "city": consignee.get("city"),
        "source_updated_at": src["updated_at"],
    }


def overlap_since(watermark):
    return (datetime.strptime(watermark, ISO) - timedelta(minutes=OVERLAP_MINUTES)).strftime(ISO)


def fetch_changes(session, watermark):
    params = {"updated_since": overlap_since(watermark), "limit": PAGE_SIZE}
    records = []
    while True:
        response = session.get(f"{BASE}/v1/shipments", params=params, timeout=TIMEOUT)
        response.raise_for_status()
        body = response.json()
        records.extend(body["data"])
        if body["next_cursor"] is None:
            return records
        params = dict(params, cursor=body["next_cursor"])


def sync(session, target, watermark):
    changes = fetch_changes(session, watermark)
    summary = {"created": 0, "updated": 0, "unchanged": 0, "skipped": 0, "errors": []}
    for record in changes:
        try:
            mapped = map_record(record)
        except ValueError as e:
            summary["skipped"] += 1
            summary["errors"].append((record.get("id"), str(e)))
            continue
        key = mapped["external_id"]
        if key not in target:
            summary["created"] += 1
        elif target[key] != mapped:
            summary["updated"] += 1
        else:
            summary["unchanged"] += 1
            continue
        target[key] = mapped
    summary["watermark"] = max([watermark] + [r["updated_at"] for r in changes])
    return summary


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
