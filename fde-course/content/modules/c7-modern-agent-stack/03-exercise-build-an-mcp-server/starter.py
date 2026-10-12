import base64
import json

# The two tools this server exposes. Each needs "name", "description" and "inputSchema".
# Names: "shipments_get" (input: shipment_id) and "shipments_search" (input: status, optional destination).
TOOLS = [
    # TODO
]


def _ok(id_, result):
    return {"jsonrpc": "2.0", "id": id_, "result": result}


def _err(id_, code, message):
    return {"jsonrpc": "2.0", "id": id_, "error": {"code": code, "message": message}}


class ShipmentsServer:
    def __init__(self):
        self.initialized = False

    def handle(self, raw):
        """Take one raw JSON-RPC message (a string) and return the raw response string, or None."""
        # TODO: parse, dispatch, serialise. A notification gets no response.
        return None

    def initialize(self, params):
        # TODO: negotiate protocolVersion, declare capabilities, return serverInfo
        pass

    def call_tool(self, params):
        # TODO: shipments_get and shipments_search
        pass

    def list_resources(self, params):
        # TODO: one page of PAGE_SIZE resources, opaque nextCursor until the last page
        pass

    def read_resource(self, params):
        # TODO
        pass


# --- Try it out (not graded) ---
client = McpTestClient(ShipmentsServer())
print("initialize ->", client.connect())
print("tools/list ->", client.request("tools/list"))
print("tools/call ->", client.request("tools/call", {"name": "shipments_get", "arguments": {"shipment_id": "CV-1004"}}))
print("resources/list page 1 ->", client.request("resources/list"))
print("unknown method ->", client.request("shipments/delete_all"))
