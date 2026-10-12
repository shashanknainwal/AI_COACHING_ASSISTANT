import hashlib
import json
import re

# Which scope each tool needs, and whether it reads or writes.
TOOL_POLICY = {
    # "shipments_get": {"tier": "read", "scope": "shipments:read"},
    # TODO: all five tools
}


def annotations(tool_name):
    """MCP tool annotations: readOnlyHint, destructiveHint, idempotentHint, openWorldHint."""
    # TODO
    pass


def validate(tool_name, args):
    """Returns a list of problems. An empty list means the arguments are safe to execute."""
    # TODO
    return []


def authorize(claims, tool_name):
    """Returns (allowed, reason)."""
    # TODO
    return True, "ok"


class SecureShipmentsServer:
    def __init__(self, audit_log):
        self.audit_log = audit_log

    def visible_tools(self, claims):
        # TODO: only the tools this caller may call, each with its annotations
        return BASE_TOOLS

    def call(self, claims, name, args):
        # TODO: authorize, validate, execute, audit every decision
        return {"status": "ok", "result": execute_tool(name, args)}


def connector_request(server_url, token):
    """Keyword arguments for client.beta.messages.create: the read-only tools only."""
    # TODO
    pass


# --- Try it out (not graded) ---
log = []
server = SecureShipmentsServer(log)
reader = make_claims(scope="shipments:read")
print("reader sees:", [t["name"] for t in server.visible_tools(reader)])
print("reader cancels:", server.call(reader, "shipments_cancel", {"shipment_id": "CV-1004", "reason": "customer asked to cancel"}))
writer = make_claims(sub="ops-lead", scope="shipments:read shipments:write")
print("writer bad note:", server.call(writer, "shipments_add_note", {"shipment_id": "CV-1004", "note": "x" * 900}))
for entry in log:
    print("audit:", entry)
