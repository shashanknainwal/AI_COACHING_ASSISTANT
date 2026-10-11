"""Hidden setup: Cindervale's shipment server, now with write tools. All data is fictional."""
import copy
import json

AUDIENCE = "https://mcp.cindervale.example/shipments"
NOW = 1_793_000_000  # fixed "current time" (Unix seconds) so tests are repeatable
DEPOTS = ["Rotterdam", "Gdansk", "Antwerp", "Le Havre", "Hamburg", "Valencia", "Lyon", "Milan"]
STATUSES = ["in_transit", "delivered", "customs_hold", "delayed", "booked"]

_BASE = {
    f"CV-{1001 + i}": {
        "id": f"CV-{1001 + i}",
        "status": STATUSES[(i * 3) % 5],
        "destination": DEPOTS[(i + 6) % len(DEPOTS)],
        "notes": [],
    }
    for i in range(23)
}
SHIPMENTS = copy.deepcopy(_BASE)


def reset_data():
    SHIPMENTS.clear()
    SHIPMENTS.update(copy.deepcopy(_BASE))


def _schema(props, required):
    return {"type": "object", "properties": props, "required": required, "additionalProperties": False}


_ID = {"type": "string", "pattern": "^CV-[0-9]{4}$"}

BASE_TOOLS = [
    {"name": "shipments_get", "description": "Get one shipment by ID. Call this when the user names a shipment.",
     "inputSchema": _schema({"shipment_id": _ID}, ["shipment_id"])},
    {"name": "shipments_search", "description": "Find shipments by status. Call this when the user asks which shipments are delayed or held.",
     "inputSchema": _schema({"status": {"type": "string", "enum": STATUSES}, "destination": {"type": "string"}}, ["status"])},
    {"name": "shipments_add_note", "description": "Add an internal note to a shipment. Call this when the user asks to record something on a shipment.",
     "inputSchema": _schema({"shipment_id": _ID, "note": {"type": "string", "maxLength": 500}}, ["shipment_id", "note"])},
    {"name": "shipments_reroute", "description": "Send a shipment to a different depot. Call this only when the user explicitly asks to reroute.",
     "inputSchema": _schema({"shipment_id": _ID, "depot": {"type": "string", "enum": DEPOTS}, "reason": {"type": "string"}},
                            ["shipment_id", "depot", "reason"])},
    {"name": "shipments_cancel", "description": "Cancel a shipment. Call this only when the user explicitly asks to cancel.",
     "inputSchema": _schema({"shipment_id": _ID, "reason": {"type": "string"}}, ["shipment_id", "reason"])},
]


def execute_tool(name, args):
    """The unprotected business logic. Returns an MCP tool result. It trusts its input completely."""
    def ok(data):
        return {"content": [{"type": "text", "text": json.dumps(data)}], "isError": False}

    def fail(msg):
        return {"content": [{"type": "text", "text": json.dumps({"error": msg})}], "isError": True}

    sid = args.get("shipment_id")
    if name == "shipments_search":
        rows = [s for s in SHIPMENTS.values() if s["status"] == args["status"]]
        if args.get("destination"):
            rows = [s for s in rows if s["destination"] == args["destination"]]
        return ok({"count": len(rows), "shipments": rows})
    if sid not in SHIPMENTS:
        return fail(f"No shipment {sid}")
    s = SHIPMENTS[sid]
    if name == "shipments_get":
        return ok(s)
    if name == "shipments_add_note":
        s["notes"].append(args["note"])
        return ok({"id": sid, "notes": len(s["notes"])})
    if name == "shipments_reroute":
        s["destination"] = args["depot"]
        return ok({"id": sid, "destination": s["destination"]})
    if name == "shipments_cancel":
        s["status"] = "cancelled"
        return ok({"id": sid, "status": "cancelled"})
    return fail(f"Unknown tool {name}")


def make_claims(sub="svc-dispatch-bot", scope="shipments:read", exp_in=3600, aud=AUDIENCE):
    """Decoded, signature-checked access-token claims, as your auth middleware would hand them over."""
    return {"sub": sub, "scope": scope, "exp": NOW + exp_in, "aud": aud, "iss": "https://login.cindervale.example"}
