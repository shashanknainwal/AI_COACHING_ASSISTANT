from requests import _sim


def _shipment(req):
    return {"id": "SHP-2001", "status": "in_transit", "eta": "2026-03-12", "carrier": "Northwind"}


# Monday morning: a 503, a 429 with Retry-After, a timeout, then success.
_sim.route("GET", r"/v1/shipments/SHP-2001", _sim.flaky(_shipment, [503, (429, {"Retry-After": "3"}), "timeout"]))
_sim.route("GET", r"/v1/shipments/SHP-404", lambda req: _sim.respond(404, json={"error": "shipment not found"}))
