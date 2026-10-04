from requests import _sim

SOURCE = [
    {"id": "SHP-1001", "status_code": "IT", "weight_lbs": 1200, "charge_cents": 88000, "consignee": {"name": "Brightway Retail", "city": "Chicago"}, "updated_at": "2026-03-10T07:02:13Z"},
    {"id": "SHP-1002", "status_code": "DL", "weight_lbs": 310, "charge_cents": 19950, "consignee": {"name": "Brightway Retail", "city": "Boston"}, "updated_at": "2026-03-10T07:10:00Z"},
    {"id": "SHP-1003", "status_code": "IT", "weight_lbs": 750, "charge_cents": 41250, "consignee": {"name": "Brightway Retail", "city": "Dallas"}, "updated_at": "2026-03-10T07:15:30Z"},
    {"id": "SHP-1004", "status_code": "PU", "weight_lbs": 95.5, "charge_cents": 7400, "consignee": {"name": "Brightway Outlet", "city": "Denver"}, "updated_at": "2026-03-10T07:21:00Z"},
    {"id": "SHP-1005", "status_code": "EX", "weight_lbs": 2050, "charge_cents": 131000, "consignee": {"name": "Brightway Retail", "city": "Phoenix"}, "updated_at": "2026-03-10T07:33:45Z"},
    {"id": "SHP-1006", "status_code": "DL", "weight_lbs": 40, "charge_cents": 3999, "consignee": {"name": "Brightway Retail", "city": "Atlanta"}, "updated_at": "2026-03-10T07:38:00Z"},
    {"id": "SHP-1011", "status_code": "ZZ", "weight_lbs": 500, "charge_cents": 25000, "consignee": {"name": "Brightway Retail", "city": "Miami"}, "updated_at": "2026-03-10T07:40:00Z"},
    {"id": "SHP-1007", "status_code": "IT", "weight_lbs": 620, "charge_cents": 35500, "consignee": {"name": "Brightway Retail", "city": "Seattle"}, "updated_at": "2026-03-10T07:52:10Z"},
    {"id": "SHP-1008", "status_code": "PU", "weight_lbs": 150, "charge_cents": 11000, "consignee": None, "updated_at": "2026-03-10T08:05:00Z"},
    {"id": "SHP-1009", "status_code": "IT", "weight_lbs": 880, "charge_cents": 52000, "consignee": {"name": "Brightway Retail", "city": "Newark"}, "updated_at": "2026-03-10T08:12:12Z"},
    {"id": "SHP-1010", "status_code": "DL", "weight_lbs": 275, "charge_cents": 16500, "consignee": {"name": "Brightway Outlet", "city": "Austin"}, "updated_at": "2026-03-10T08:25:00Z"},
    {"id": "SHP-1012", "status_code": "IT", "weight_lbs": None, "charge_cents": 9900, "consignee": {"name": "Brightway Retail", "city": "Tampa"}, "updated_at": "2026-03-10T08:28:41Z"},
]


def simulate_new_changes():
    """Northwind updates two shipments and creates one (for the demo)."""
    for s in SOURCE:
        if s["id"] == "SHP-1003":
            s.update(status_code="DL", updated_at="2026-03-10T08:40:00Z")
        if s["id"] == "SHP-1005":
            s.update(charge_cents=129500, updated_at="2026-03-10T08:41:10Z")
    SOURCE.append({"id": "SHP-1013", "status_code": "PU", "weight_lbs": 60, "charge_cents": 5200,
                   "consignee": {"name": "Brightway Retail", "city": "Portland"}, "updated_at": "2026-03-10T08:42:05Z"})


def _list(req):
    since = req.params.get("updated_since", "")
    limit = int(req.params.get("limit", 20))
    if not 1 <= limit <= 50:
        return _sim.respond(400, json={"error": "limit must be between 1 and 50"})
    rows = sorted((s for s in SOURCE if s["updated_at"] >= since), key=lambda s: (s["updated_at"], s["id"]))
    start = int(req.params.get("cursor", "c_0")[2:])
    page = [dict(r) for r in rows[start:start + limit]]
    nxt = f"c_{start + limit}" if start + limit < len(rows) else None
    return {"data": page, "next_cursor": nxt}


_sim.route("GET", r"/v1/shipments", _list)
