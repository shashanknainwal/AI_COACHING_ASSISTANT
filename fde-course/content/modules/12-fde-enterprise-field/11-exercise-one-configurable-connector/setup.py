# Two carrier APIs, simulated as page-fetching functions.
# Northwind pages with a cursor; Polar Express pages with page numbers.
_NORTHWIND = [
    {"id": "SHP-1001", "status_code": "IT", "weight_lbs": 1200, "charge_cents": 88000,
     "consignee": {"name": "Brightway Retail", "city": "Chicago"}, "updated_at": "2026-03-10T07:02:13Z"},
    {"id": "SHP-1002", "status_code": "DL", "weight_lbs": 310, "charge_cents": 19950,
     "consignee": {"name": "Brightway Retail", "city": "Boston"}, "updated_at": "2026-03-10T07:10:00Z"},
    {"id": "SHP-1008", "status_code": "PU", "weight_lbs": 150, "charge_cents": 11000,
     "consignee": None, "updated_at": "2026-03-10T08:05:00Z"},
    {"id": "SHP-1011", "status_code": "ZZ", "weight_lbs": 500, "charge_cents": 25000,
     "consignee": {"name": "Brightway Retail", "city": "Miami"}, "updated_at": "2026-03-10T07:40:00Z"},
    {"id": "SHP-1012", "status_code": "IT", "weight_lbs": None, "charge_cents": 9900,
     "consignee": {"name": "Brightway Retail", "city": "Tampa"}, "updated_at": "2026-03-10T08:28:41Z"},
]
_POLAR = [
    {"trk_no": "PX-88213", "state": "OUT_FOR_DELIVERY", "wt_kg": 12.5, "amt_usd": "48.20",
     "recipient": "Brightway Retail", "dest_city": "Austin", "last_event_ts": "10/03/2026 08:15", "svc_level": "GROUND"},
    {"trk_no": "PX-88214", "state": "DELIVERED", "wt_kg": 3.1, "amt_usd": "12.75",
     "recipient": "Brightway Outlet", "dest_city": "Reno", "last_event_ts": "10/03/2026 09:02", "svc_level": "EXPRESS"},
    {"trk_no": "PX-88215", "state": "PICKED_UP", "wt_kg": 40.0, "amt_usd": "101.00",
     "recipient": "Brightway Retail", "dest_city": None, "last_event_ts": "11/03/2026 14:30", "svc_level": "GROUND"},
    {"trk_no": "PX-88216", "state": "HELD_AT_CUSTOMS", "wt_kg": 7.2, "amt_usd": "33.10",
     "recipient": "Brightway Retail", "dest_city": "El Paso", "last_event_ts": "11/03/2026 16:05", "svc_level": "EXPRESS"},
    {"trk_no": "PX-88217", "state": "EXCEPTION", "wt_kg": 2.0, "amt_usd": "9.99",
     "recipient": "Brightway Outlet", "dest_city": "Tucson", "last_event_ts": "12/03/2026 07:45", "svc_level": "GROUND"},
]

page_calls = []


def northwind_fetch(params):
    """GET /v1/shipments?cursor=...  ->  {"data": [...], "next_cursor": str | None}"""
    page_calls.append(("northwind", dict(params)))
    start = int(params.get("cursor") or 0)
    items = _NORTHWIND[start:start + 2]
    nxt = start + 2 if start + 2 < len(_NORTHWIND) else None
    return {"data": [dict(i) for i in items], "next_cursor": str(nxt) if nxt is not None else None}


def polar_fetch(params):
    """GET /api/shipments?page=N  ->  {"shipments": [...], "has_more": bool}"""
    page_calls.append(("polar", dict(params)))
    page = int(params.get("page", 1))
    items = _POLAR[(page - 1) * 2:page * 2]
    return {"shipments": [dict(i) for i in items], "has_more": page * 2 < len(_POLAR)}
