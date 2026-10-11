"""Hidden setup: Cindervale Freight's shipment records and a tiny MCP test client.

Cindervale Freight is a fictional company. Every record below is made up.
"""
import json

# Protocol revisions this server speaks, newest first. These are example values:
# check modelcontextprotocol.io for the revision your SDK and clients use today.
SUPPORTED_VERSIONS = ["2025-06-18", "2025-03-26"]

SERVER_INFO = {"name": "cindervale-shipments", "version": "0.1.0"}

# Standard JSON-RPC 2.0 error codes, plus the code the MCP spec uses for a missing resource.
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603
RESOURCE_NOT_FOUND = -32002

PAGE_SIZE = 10

_STATUSES = ["in_transit", "delivered", "customs_hold", "delayed", "booked"]
_LANES = [("Rotterdam", "Lyon"), ("Gdansk", "Milan"), ("Antwerp", "Munich"), ("Le Havre", "Zurich"),
          ("Hamburg", "Vienna"), ("Valencia", "Toulouse")]

SHIPMENTS = {}
for _i in range(23):
    _sid = f"CV-{1001 + _i}"
    _o, _d = _LANES[_i % len(_LANES)]
    SHIPMENTS[_sid] = {
        "id": _sid,
        "status": _STATUSES[(_i * 3) % len(_STATUSES)],
        "origin": _o,
        "destination": _d,
        "carrier": ["Brask Haulage", "Ostrander Lines", "Pellworth Cargo"][_i % 3],
        "eta": f"2026-11-{(_i % 27) + 1:02d}",
        "weight_kg": 800 + 137 * _i,
    }


class McpTestClient:
    """A minimal client that talks to your server through handle(raw) -> raw.

    Real clients send these strings over stdio (one JSON message per line) or
    as HTTP POST bodies (streamable HTTP). The handler is the same either way.
    """

    def __init__(self, server):
        self.server = server
        self._next_id = 1

    def send_raw(self, raw):
        out = self.server.handle(raw)
        return None if out is None else json.loads(out)

    def request(self, method, params=None):
        msg = {"jsonrpc": "2.0", "id": self._next_id, "method": method}
        if params is not None:
            msg["params"] = params
        self._next_id += 1
        return self.send_raw(json.dumps(msg))

    def notify(self, method, params=None):
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        return self.send_raw(json.dumps(msg))

    def connect(self):
        r = self.request("initialize", {
            "protocolVersion": SUPPORTED_VERSIONS[0],
            "capabilities": {},
            "clientInfo": {"name": "course-test-client", "version": "1.0"},
        })
        self.notify("notifications/initialized")
        return r
