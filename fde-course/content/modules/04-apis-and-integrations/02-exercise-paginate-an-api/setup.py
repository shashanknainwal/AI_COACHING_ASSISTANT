from requests import _sim

_STATUSES = ["in_transit", "delivered", "delivered", "exception", "in_transit", "delivered", "pending"]
_CITIES = ["Chicago, IL", "Dallas, TX", "Newark, NJ", "Denver, CO", "Atlanta, GA", "Seattle, WA"]
SHIPMENTS = [
    {
        "id": f"SHP-{1001 + i}",
        "status": _STATUSES[i % len(_STATUSES)],
        "origin": _CITIES[i % len(_CITIES)],
        "destination": _CITIES[(i * 5 + 2) % len(_CITIES)],
        "updated_at": f"2026-03-{1 + i % 28:02d}T{(i * 7) % 24:02d}:00:00Z",
    }
    for i in range(127)
]
_TOKEN = "nw_test_token"


def _list(req):
    if req.header("Authorization") != f"Bearer {_TOKEN}":
        return _sim.respond(401, json={"error": "invalid or missing token"})
    try:
        limit = int(req.params.get("limit", 20))
    except ValueError:
        return _sim.respond(400, json={"error": "limit must be an integer"})
    if not 1 <= limit <= 50:
        return _sim.respond(400, json={"error": "limit must be between 1 and 50"})
    rows = SHIPMENTS
    if "status" in req.params:
        rows = [s for s in rows if s["status"] == req.params["status"]]
    cursor = req.params.get("cursor")
    start = 0
    if cursor is not None:
        if not cursor.startswith("c_") or not cursor[2:].isdigit():
            return _sim.respond(400, json={"error": "invalid cursor"})
        start = int(cursor[2:])
    page = rows[start:start + limit]
    nxt = f"c_{start + limit}" if start + limit < len(rows) else None
    return _sim.respond(200, json={"data": page, "next_cursor": nxt})


_sim.route("GET", r"/v1/shipments", _list)
