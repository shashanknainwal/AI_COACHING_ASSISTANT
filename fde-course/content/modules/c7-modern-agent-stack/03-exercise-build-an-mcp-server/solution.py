import base64
import json

TOOLS = [
    {
        "name": "shipments_get",
        "description": (
            "Get one Cindervale shipment by its ID (for example CV-1004). Call this when the user "
            "names a specific shipment and wants its status, route, carrier or ETA."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {"shipment_id": {"type": "string", "description": "Shipment ID such as CV-1004"}},
            "required": ["shipment_id"],
        },
    },
    {
        "name": "shipments_search",
        "description": (
            "Find shipments by status and, optionally, destination city. Call this when the user asks "
            "which shipments are delayed, held in customs, or headed somewhere."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["in_transit", "delivered", "customs_hold", "delayed", "booked"]},
                "destination": {"type": "string", "description": "Destination city, exact match"},
            },
            "required": ["status"],
        },
    },
]


def _ok(id_, result):
    return {"jsonrpc": "2.0", "id": id_, "result": result}


def _err(id_, code, message):
    return {"jsonrpc": "2.0", "id": id_, "error": {"code": code, "message": message}}


def _encode_cursor(offset):
    return base64.urlsafe_b64encode(f"offset:{offset}".encode()).decode()


def _decode_cursor(cursor):
    """Returns the offset, or None if the cursor isn't one we issued."""
    try:
        text = base64.urlsafe_b64decode(cursor.encode()).decode()
        prefix, value = text.split(":")
        offset = int(value)
    except Exception:
        return None
    if prefix != "offset" or offset < 0 or offset >= len(SHIPMENTS):
        return None
    return offset


def _text_result(data, is_error=False):
    return {"content": [{"type": "text", "text": json.dumps(data)}], "isError": is_error}


class ShipmentsServer:
    def __init__(self):
        self.initialized = False

    def handle(self, raw):
        try:
            msg = json.loads(raw)
        except (ValueError, TypeError):
            return json.dumps(_err(None, PARSE_ERROR, "Parse error"))
        out = self.dispatch(msg)
        return None if out is None else json.dumps(out)

    def dispatch(self, msg):
        if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or not isinstance(msg.get("method"), str):
            return _err(msg.get("id") if isinstance(msg, dict) else None, INVALID_REQUEST, "Invalid Request")
        if "id" not in msg:
            if msg["method"] == "notifications/initialized":
                self.initialized = True
            return None  # notifications never get a response
        id_, method, params = msg["id"], msg["method"], msg.get("params") or {}
        if not isinstance(params, dict):
            return _err(id_, INVALID_PARAMS, "params must be an object")
        handlers = {
            "initialize": self.initialize,
            "ping": lambda p: {},
            "tools/list": lambda p: {"tools": TOOLS},
            "tools/call": self.call_tool,
            "resources/list": self.list_resources,
            "resources/read": self.read_resource,
        }
        if method not in handlers:
            return _err(id_, METHOD_NOT_FOUND, f"Method not found: {method}")
        try:
            result = handlers[method](params)
        except _RpcError as e:
            return _err(id_, e.code, e.message)
        except Exception:
            return _err(id_, INTERNAL_ERROR, "Internal error")
        return _ok(id_, result)

    def initialize(self, params):
        requested = params.get("protocolVersion")
        version = requested if requested in SUPPORTED_VERSIONS else SUPPORTED_VERSIONS[0]
        return {
            "protocolVersion": version,
            "capabilities": {"tools": {}, "resources": {}},
            "serverInfo": SERVER_INFO,
        }

    def call_tool(self, params):
        name, args = params.get("name"), params.get("arguments") or {}
        if name not in {t["name"] for t in TOOLS}:
            raise _RpcError(INVALID_PARAMS, f"Unknown tool: {name}")
        if not isinstance(args, dict):
            raise _RpcError(INVALID_PARAMS, "arguments must be an object")
        if name == "shipments_get":
            sid = args.get("shipment_id")
            if not isinstance(sid, str):
                raise _RpcError(INVALID_PARAMS, "shipment_id is required")
            if sid not in SHIPMENTS:
                return _text_result({"error": f"No shipment {sid}. Check the ID or search by status."}, is_error=True)
            return _text_result(SHIPMENTS[sid])
        status = args.get("status")
        if status not in ("in_transit", "delivered", "customs_hold", "delayed", "booked"):
            raise _RpcError(INVALID_PARAMS, "status is required and must be one of the listed values")
        rows = [s for s in SHIPMENTS.values() if s["status"] == status]
        if args.get("destination"):
            rows = [s for s in rows if s["destination"] == args["destination"]]
        return _text_result({"count": len(rows), "shipments": rows})

    def list_resources(self, params):
        offset = 0
        if "cursor" in params:
            offset = _decode_cursor(params["cursor"]) if isinstance(params["cursor"], str) else None
            if offset is None:
                raise _RpcError(INVALID_PARAMS, "Invalid cursor")
        ids = sorted(SHIPMENTS)
        page = ids[offset:offset + PAGE_SIZE]
        result = {"resources": [
            {"uri": f"shipment://{sid}", "name": f"Shipment {sid}", "mimeType": "application/json"} for sid in page
        ]}
        if offset + PAGE_SIZE < len(ids):
            result["nextCursor"] = _encode_cursor(offset + PAGE_SIZE)
        return result

    def read_resource(self, params):
        uri = params.get("uri")
        if not isinstance(uri, str):
            raise _RpcError(INVALID_PARAMS, "uri is required")
        sid = uri[len("shipment://"):] if uri.startswith("shipment://") else None
        if sid not in SHIPMENTS:
            raise _RpcError(RESOURCE_NOT_FOUND, f"Resource not found: {uri}")
        return {"contents": [{"uri": uri, "mimeType": "application/json", "text": json.dumps(SHIPMENTS[sid])}]}


class _RpcError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code, self.message = code, message


# --- Try it out (not graded) ---
client = McpTestClient(ShipmentsServer())
print("initialize ->", client.connect())
print("tools/list ->", [t["name"] for t in (client.request("tools/list") or {}).get("result", {}).get("tools", [])])
print("tools/call ->", client.request("tools/call", {"name": "shipments_get", "arguments": {"shipment_id": "CV-1004"}}))
page = client.request("resources/list")
print("resources/list page 1 ->", page)
print("unknown method ->", client.request("shipments/delete_all"))
