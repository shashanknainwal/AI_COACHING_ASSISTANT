"""NorthStar Logistics: the capstone customer (Module 10).

Raw exports exactly as NorthStar's team sent them (messy), plus clean versions
for the later exercises.

    SHIPMENTS_CSV      raw shipment export (text, messy)
    CARRIER_EVENTS     raw carrier tracking events (list of dicts, messy IDs)
    CUSTOMERS          customer accounts with SLA tiers
    EXCEPTION_HISTORY  30 days of manually handled exceptions (for the baseline)
    ASKS               what each stakeholder asked for during discovery
    clean_data()       cleaned (shipments, latest_events, customers) dicts
"""

import copy

CUSTOMERS = {
    "C-01": {"name": "Halvorsen Medical Supply", "tier": "platinum", "sla_hours": 2, "contact": "ops@halvorsen.example"},
    "C-02": {"name": "Prairie Home Goods", "tier": "standard", "sla_hours": 24, "contact": "orders@prairiehome.example"},
    "C-03": {"name": "Lakeshore Electronics", "tier": "gold", "sla_hours": 4, "contact": "logistics@lakeshore.example"},
    "C-04": {"name": "Bramble & Oak Furniture", "tier": "standard", "sla_hours": 24, "contact": "hello@brambleoak.example"},
    "C-05": {"name": "Cedar Valley Foods", "tier": "gold", "sla_hours": 4, "contact": "supply@cedarvalley.example"},
    "C-06": {"name": "Ironline Auto Parts", "tier": "platinum", "sla_hours": 2, "contact": "dispatch@ironline.example"},
}
CARRIERS = ["FastFreight", "BlueLine Express", "NorthPeak Carriers"]

# (id, customer, carrier, origin, destination, ship_date, promised_date, weight_kg, value_usd)
_SHIPMENTS = [
    ("NS-2001", "C-01", "FastFreight", "Chicago, IL", "Denver, CO", "2026-04-01", "2026-04-04", 120.0, 18400.0),
    ("NS-2002", "C-02", "BlueLine Express", "Chicago, IL", "Omaha, NE", "2026-04-01", "2026-04-03", 340.5, 2100.0),
    ("NS-2003", "C-03", "NorthPeak Carriers", "Milwaukee, WI", "Minneapolis, MN", "2026-04-02", "2026-04-04", 56.0, 9650.0),
    ("NS-2004", "C-04", "FastFreight", "Chicago, IL", "Kansas City, MO", "2026-04-02", "2026-04-06", 410.0, 5200.0),
    ("NS-2005", "C-05", "BlueLine Express", "Indianapolis, IN", "St. Louis, MO", "2026-04-02", "2026-04-03", 980.0, 3300.0),
    ("NS-2006", "C-06", "NorthPeak Carriers", "Detroit, MI", "Chicago, IL", "2026-04-03", "2026-04-04", 75.0, 12800.0),
    ("NS-2007", "C-02", "FastFreight", "Chicago, IL", "Des Moines, IA", "2026-04-03", "2026-04-05", 220.0, 1450.0),
    ("NS-2008", "C-03", "BlueLine Express", "Milwaukee, WI", "Columbus, OH", "2026-04-03", "2026-04-06", 30.0, 7400.0),
    ("NS-2009", "C-01", "NorthPeak Carriers", "Chicago, IL", "Madison, WI", "2026-04-04", "2026-04-05", 64.0, 22100.0),
    ("NS-2010", "C-04", "BlueLine Express", "Chicago, IL", "Louisville, KY", "2026-04-04", "2026-04-07", None, 3900.0),
    ("NS-2011", "C-05", "FastFreight", "Indianapolis, IN", "Cleveland, OH", "2026-04-04", "2026-04-06", 1210.0, 4100.0),
    ("NS-2012", "C-06", "FastFreight", "Detroit, MI", "Toledo, OH", "2026-04-05", "2026-04-06", 140.0, 15600.0),
    ("NS-2013", "C-02", "NorthPeak Carriers", "Chicago, IL", "Peoria, IL", "2026-04-05", "2026-04-06", 88.0, 760.0),
    ("NS-2014", "C-03", "FastFreight", "Milwaukee, WI", "Toronto, ON", "2026-04-05", "2026-04-09", 45.0, 11300.0),
    ("NS-2015", "C-04", "NorthPeak Carriers", "Chicago, IL", "Fargo, ND", "2026-04-06", "2026-04-09", 515.0, 6800.0),
    ("NS-2016", "C-05", "BlueLine Express", "Indianapolis, IN", "Nashville, TN", "2026-04-06", "2026-04-08", None, 2950.0),
    ("NS-2017", "C-01", "BlueLine Express", "Chicago, IL", "Winnipeg, MB", "2026-04-06", "2026-04-10", 98.0, 26700.0),
    ("NS-2018", "C-06", "BlueLine Express", "Detroit, MI", "Grand Rapids, MI", "2026-04-07", "2026-04-08", 160.0, 9100.0),
    ("NS-2019", "C-02", "FastFreight", "Chicago, IL", "Rockford, IL", "2026-04-07", "2026-04-08", 72.0, 540.0),
    ("NS-2020", "C-03", "NorthPeak Carriers", "Milwaukee, WI", "Green Bay, WI", "2026-04-07", "2026-04-08", 38.0, 6200.0),
]

# Latest carrier event per shipment: (code, timestamp, detail)
_LATEST = {
    "NS-2001": ("DELAY", "2026-04-04T09:15:00Z", "Weather closure on I-80; new ETA 2026-04-06"),
    "NS-2002": ("DELIVERED", "2026-04-03T14:02:00Z", "Delivered, signed by M. Ruiz"),
    "NS-2003": ("DAMAGE", "2026-04-04T11:40:00Z", "Pallet crushed in transit; 3 of 12 cartons damaged"),
    "NS-2004": ("DELIVERED", "2026-04-05T16:20:00Z", "Delivered to dock 4"),
    "NS-2005": ("DELAY", "2026-04-03T18:05:00Z", "Missed linehaul connection; new ETA 2026-04-04"),
    "NS-2006": ("PICKUP_MISSED", "2026-04-03T17:30:00Z", "Driver unavailable; pickup not completed"),
    "NS-2007": ("IN_TRANSIT", "2026-04-04T08:00:00Z", "Departed Chicago terminal"),
    "NS-2008": ("ADDRESS_ISSUE", "2026-04-05T10:10:00Z", "Consignee address incomplete: suite number missing"),
    "NS-2009": ("DELIVERED", "2026-04-05T12:45:00Z", "Delivered, signed by T. Okafor"),
    "NS-2010": ("IN_TRANSIT", "2026-04-05T07:30:00Z", "Arrived Indianapolis hub"),
    "NS-2011": ("DELAY", "2026-04-06T13:00:00Z", "Equipment failure; new ETA 2026-04-09"),
    "NS-2012": ("DELIVERED", "2026-04-06T11:15:00Z", "Delivered to receiving"),
    "NS-2013": ("DELIVERED", "2026-04-06T15:50:00Z", "Delivered"),
    "NS-2014": ("CUSTOMS_HOLD", "2026-04-07T09:00:00Z", "Held at border: commercial invoice missing HS codes"),
    "NS-2015": ("IN_TRANSIT", "2026-04-07T06:20:00Z", "Departed Minneapolis terminal"),
    "NS-2016": ("DAMAGE", "2026-04-08T09:30:00Z", "Water damage reported on 2 pallets"),
    "NS-2017": ("CUSTOMS_HOLD", "2026-04-09T15:10:00Z", "Held at border: inspection requested"),
    "NS-2018": ("DELAY", "2026-04-08T07:45:00Z", "Driver hours limit reached; new ETA 2026-04-09"),
    "NS-2019": ("ADDRESS_ISSUE", "2026-04-08T09:05:00Z", "Business closed at delivery address"),
    "NS-2020": ("DELIVERED", "2026-04-08T13:30:00Z", "Delivered"),
}
EXCEPTION_CODES = ["DELAY", "DAMAGE", "CUSTOMS_HOLD", "ADDRESS_ISSUE", "PICKUP_MISSED"]

# How each row's fields are mangled in the raw export.
_CARRIER_VARIANTS = {
    "FastFreight": ["FastFreight", "fastfreight ", "Fast Freight Inc.", "FAST FREIGHT"],
    "BlueLine Express": ["BlueLine Express", "Blueline Express LLC", "blue line express"],
    "NorthPeak Carriers": ["NorthPeak Carriers", "Northpeak", "North Peak Carriers Inc"],
}
_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _mangle_date(iso, i):
    y, m, d = iso.split("-")
    style = i % 3
    if style == 0:
        return iso
    if style == 1:
        return f"{m}/{d}/{y}"
    return f"{_MONTHS[int(m) - 1]} {int(d)} {y}"


def _render_csv():
    lines = ["shipment_id,customer_id,carrier,origin,destination,ship_date,promised_date,weight_kg,value_usd"]
    for i, (sid, cid, carrier, origin, dest, ship, promised, weight, value) in enumerate(_SHIPMENTS):
        variants = _CARRIER_VARIANTS[carrier]
        carrier_raw = variants[i % len(variants)]
        weight_raw = "" if weight is None else (f"{weight:g}" if i % 4 else f"{weight:.1f}")
        value_raw = f'"${value:,.2f}"' if i % 2 else f"{value:.2f}"
        row = [sid if i % 5 else f" {sid.lower()} ", cid, carrier_raw, f'"{origin}"', f'"{dest}"',
               _mangle_date(ship, i), _mangle_date(promised, i + 1), weight_raw, value_raw]
        lines.append(",".join(row))
        if sid in ("NS-2004", "NS-2011", "NS-2017"):        # exported twice
            lines.append(",".join(row))
    lines.append("NS-2021,C-02,FastFreight,\"Chicago, IL\",\"Gary, IN\",2026-13-45,2026-04-09,50,300.00")  # bad dates
    return "\n".join(lines) + "\n"


def _events():
    events, n = [], 0
    for sid, (code, ts, detail) in _LATEST.items():
        day = ts[:10]
        raw_id = sid if n % 4 else sid.lower().replace("-", " - ")
        events.append({"shipment_id": raw_id, "ts": f"{day}T05:00:00Z", "code": "IN_TRANSIT", "detail": "Scanned at origin"})
        events.append({"shipment_id": sid, "ts": ts, "code": code, "detail": detail})
        n += 1
    events.append({"shipment_id": "NS-9999", "ts": "2026-04-05T10:00:00Z", "code": "DELAY", "detail": "Unknown shipment"})
    events.append({"shipment_id": "NS-9998", "ts": "2026-04-06T10:00:00Z", "code": "DAMAGE", "detail": "Unknown shipment"})
    events.reverse()                                       # the export isn't in time order
    return events


def _history():
    seed, out = 11, []

    def rand():
        nonlocal seed
        seed = (seed * 1103515245 + 12345) % 2**31
        return seed / 2**31

    types = [("DELAY", 0.46, 18), ("ADDRESS_ISSUE", 0.18, 14), ("DAMAGE", 0.14, 41), ("CUSTOMS_HOLD", 0.12, 52), ("PICKUP_MISSED", 0.10, 26)]
    tiers = [("platinum", 0.2, 2), ("gold", 0.3, 4), ("standard", 0.5, 24)]
    for day in range(1, 31):
        for k in range(36 + day % 9):
            r, acc = rand(), 0
            for t, share, base in types:
                acc += share
                if r <= acc:
                    break
            r2, acc2 = rand(), 0
            for tier, share, sla in tiers:
                acc2 += share
                if r2 <= acc2:
                    break
            minutes = int(base * (0.5 + rand() * 1.5))
            wait_hours = round(rand() * {"platinum": 3.5, "gold": 4.6, "standard": 30}[tier], 1)
            out.append({"id": f"EX-{day:02d}{k:03d}", "date": f"2026-03-{day:02d}", "type": t, "tier": tier,
                        "handle_minutes": minutes, "first_response_hours": wait_hours, "sla_hours": sla,
                        "breached": wait_hours > sla})
    return out


SHIPMENTS_CSV = _render_csv()
CARRIER_EVENTS = _events()
EXCEPTION_HISTORY = _history()

ASKS = [
    {"id": "A1", "from": "VP Operations (sponsor)", "ask": "Triage every new exception and draft the customer update",
     "value": 5, "effort_days": 8, "must_have": True},
    {"id": "A2", "from": "VP Operations (sponsor)", "ask": "Weekly report on exception volume, handling time and SLA breaches",
     "value": 4, "effort_days": 3, "must_have": True},
    {"id": "A3", "from": "Ops team lead", "ask": "Open claims automatically for damaged freight",
     "value": 4, "effort_days": 4, "must_have": False},
    {"id": "A4", "from": "Customer success", "ask": "Proactive ETA emails for every shipment, not just exceptions",
     "value": 3, "effort_days": 9, "must_have": False},
    {"id": "A5", "from": "IT security", "ask": "SSO login and audit log for every automated action",
     "value": 3, "effort_days": 2, "must_have": True},
    {"id": "A6", "from": "Ops team lead", "ask": "Suggest a backup carrier when a pickup is missed",
     "value": 4, "effort_days": 3, "must_have": False},
    {"id": "A7", "from": "Finance", "ask": "Rebuild carrier invoice reconciliation",
     "value": 2, "effort_days": 10, "must_have": False},
    {"id": "A8", "from": "Customs broker team", "ask": "Pre-check commercial invoices for missing HS codes",
     "value": 3, "effort_days": 3, "must_have": False},
]


def clean_data():
    """Cleaned (shipments, latest_events, customers) dicts keyed by ID."""
    shipments = {s[0]: {"shipment_id": s[0], "customer_id": s[1], "carrier": s[2], "origin": s[3], "destination": s[4],
                        "ship_date": s[5], "promised_date": s[6], "weight_kg": s[7], "value_usd": s[8]} for s in _SHIPMENTS}
    latest = {sid: {"code": c, "ts": ts, "detail": d} for sid, (c, ts, d) in _LATEST.items()}
    return shipments, latest, copy.deepcopy(CUSTOMERS)
