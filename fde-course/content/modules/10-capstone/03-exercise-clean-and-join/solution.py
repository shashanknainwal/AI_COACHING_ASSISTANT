import csv
import io
import re
from datetime import datetime
from fde_datasets import northstar

DATE_FORMATS = ["%Y-%m-%d", "%m/%d/%Y", "%b %d %Y"]
CARRIER_KEYS = {  # normalized key -> canonical carrier name (given)
    "fastfreight": "FastFreight",
    "bluelineexpress": "BlueLine Express",
    "northpeakcarriers": "NorthPeak Carriers",
    "northpeak": "NorthPeak Carriers",
}
COMPANY_SUFFIXES = {"inc", "llc", "co", "corp"}


def parse_date(raw):
    raw = raw.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def normalize_id(raw):
    return re.sub(r"\s+", "", raw).upper()


def normalize_carrier(raw):
    words = re.sub(r"[^a-z0-9 ]", "", raw.lower()).split()
    while words and words[-1] in COMPANY_SUFFIXES:
        words.pop()
    return CARRIER_KEYS.get("".join(words))


def parse_money(raw):
    return float(raw.replace("$", "").replace(",", "").strip())


def clean_shipments(csv_text):
    shipments = {}
    issues = {"rows": 0, "duplicates": 0, "bad_dates": [], "missing_weight": [], "unknown_carrier": []}
    for row in csv.DictReader(io.StringIO(csv_text)):
        issues["rows"] += 1
        sid = normalize_id(row["shipment_id"])
        if sid in shipments:
            issues["duplicates"] += 1
            continue
        ship, promised = parse_date(row["ship_date"]), parse_date(row["promised_date"])
        if ship is None or promised is None:
            issues["bad_dates"].append(sid)
            continue
        carrier = normalize_carrier(row["carrier"])
        if carrier is None:
            issues["unknown_carrier"].append(sid)
        weight = float(row["weight_kg"]) if row["weight_kg"].strip() else None
        if weight is None:
            issues["missing_weight"].append(sid)
        shipments[sid] = {"shipment_id": sid, "customer_id": row["customer_id"].strip(), "carrier": carrier,
                          "origin": row["origin"].strip(), "destination": row["destination"].strip(),
                          "ship_date": ship, "promised_date": promised, "weight_kg": weight,
                          "value_usd": parse_money(row["value_usd"])}
    return shipments, issues


def latest_events(events):
    latest = {}
    for e in events:
        sid = normalize_id(e["shipment_id"])
        if sid not in latest or e["ts"] > latest[sid]["ts"]:
            latest[sid] = {"code": e["code"], "ts": e["ts"], "detail": e["detail"]}
    return latest


def build_queue(shipments, latest, customers):
    queue, orphans = [], []
    for sid, event in latest.items():
        if event["code"] not in northstar.EXCEPTION_CODES:
            continue
        if sid not in shipments:
            orphans.append(sid)
            continue
        s = shipments[sid]
        c = customers[s["customer_id"]]
        queue.append({"shipment_id": sid, "customer": c["name"], "tier": c["tier"], "sla_hours": c["sla_hours"],
                      "code": event["code"], "detail": event["detail"], "carrier": s["carrier"],
                      "value_usd": s["value_usd"], "event_ts": event["ts"]})
    queue.sort(key=lambda q: (q["sla_hours"], -q["value_usd"]))
    return queue, sorted(orphans)


# --- Try it out (not graded) ---
cleaned = clean_shipments(northstar.SHIPMENTS_CSV)
if cleaned:
    shipments, issues = cleaned
    print(f"{len(shipments)} clean shipments; data-quality issues: {issues}")
    latest = latest_events(northstar.CARRIER_EVENTS)
    built = build_queue(shipments, latest, northstar.CUSTOMERS) if latest else None
    if built:
        queue, orphans = built
        print(f"\nException queue ({len(queue)}), most urgent first:")
        for q in queue:
            print(f"   {q['shipment_id']} {q['tier']:<9} {q['code']:<14} ${q['value_usd']:>9,.2f}  {q['customer']}")
        print("Events for unknown shipments:", orphans)
