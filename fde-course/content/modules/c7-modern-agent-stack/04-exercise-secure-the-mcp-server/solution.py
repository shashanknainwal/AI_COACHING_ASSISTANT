import hashlib
import json
import re

TOOL_POLICY = {
    "shipments_get": {"tier": "read", "scope": "shipments:read"},
    "shipments_search": {"tier": "read", "scope": "shipments:read"},
    "shipments_add_note": {"tier": "write", "scope": "shipments:write"},
    "shipments_reroute": {"tier": "write", "scope": "shipments:write"},
    "shipments_cancel": {"tier": "write", "scope": "shipments:admin"},
}

_ID_RE = re.compile(r"^CV-\d{4}$")
_CONTROL = re.compile(r"[\x00-\x09\x0b-\x1f\x7f]")  # control characters except newline
_ALLOWED_KEYS = {
    "shipments_get": {"shipment_id"},
    "shipments_search": {"status", "destination"},
    "shipments_add_note": {"shipment_id", "note"},
    "shipments_reroute": {"shipment_id", "depot", "reason"},
    "shipments_cancel": {"shipment_id", "reason"},
}


def annotations(tool_name):
    """MCP tool annotations: hints for clients, never a security control."""
    read = TOOL_POLICY[tool_name]["tier"] == "read"
    return {
        "readOnlyHint": read,
        "destructiveHint": tool_name in ("shipments_reroute", "shipments_cancel"),
        "idempotentHint": tool_name != "shipments_add_note",
        "openWorldHint": False,
    }


def validate(tool_name, args):
    """Returns a list of problems. An empty list means the arguments are safe to execute."""
    if not isinstance(args, dict):
        return ["arguments must be an object"]
    problems = [f"unexpected argument: {k}" for k in sorted(set(args) - _ALLOWED_KEYS[tool_name])]
    if "shipment_id" in _ALLOWED_KEYS[tool_name]:
        sid = args.get("shipment_id")
        if not isinstance(sid, str) or not _ID_RE.match(sid):
            problems.append("shipment_id must look like CV-1234")
    if tool_name == "shipments_search":
        if args.get("status") not in STATUSES:
            problems.append("status must be one of " + ", ".join(STATUSES))
        dest = args.get("destination")
        if dest is not None and (not isinstance(dest, str) or not re.fullmatch(r"[A-Za-z][A-Za-z \-]{0,63}", dest)):
            problems.append("destination must be a city name of up to 64 letters")
    if tool_name == "shipments_add_note":
        note = args.get("note")
        if not isinstance(note, str) or not 1 <= len(note) <= 500:
            problems.append("note must be 1 to 500 characters")
        elif _CONTROL.search(note):
            problems.append("note contains control characters")
    if tool_name == "shipments_reroute" and args.get("depot") not in DEPOTS:
        problems.append("depot must be one of " + ", ".join(DEPOTS))
    if tool_name in ("shipments_reroute", "shipments_cancel"):
        reason = args.get("reason")
        if not isinstance(reason, str) or not 10 <= len(reason.strip()) <= 300:
            problems.append("reason must be 10 to 300 characters")
    return problems


def authorize(claims, tool_name):
    """Returns (allowed, reason)."""
    if tool_name not in TOOL_POLICY:
        return False, "unknown_tool"
    if not claims:
        return False, "unauthenticated"
    if claims.get("exp", 0) <= NOW:
        return False, "expired"
    if claims.get("aud") != AUDIENCE:
        return False, "wrong_audience"
    needed = TOOL_POLICY[tool_name]["scope"]
    if needed not in (claims.get("scope") or "").split():
        return False, f"missing_scope:{needed}"
    return True, "ok"


def _digest(args):
    return hashlib.sha256(json.dumps(args, sort_keys=True, default=str).encode()).hexdigest()[:16]


class SecureShipmentsServer:
    def __init__(self, audit_log):
        self.audit_log = audit_log

    def _audit(self, claims, name, args, decision, reason):
        self.audit_log.append({
            "ts": NOW,
            "sub": (claims or {}).get("sub"),
            "tool": name,
            "decision": decision,
            "reason": reason,
            "args_digest": _digest(args),
        })

    def visible_tools(self, claims):
        out = []
        for tool in BASE_TOOLS:
            allowed, _ = authorize(claims, tool["name"])
            if allowed:
                out.append(dict(tool, annotations=annotations(tool["name"])))
        return out

    def call(self, claims, name, args):
        allowed, reason = authorize(claims, name)
        if not allowed:
            self._audit(claims, name, args, "denied", reason)
            return {"status": "denied", "reason": reason}
        problems = validate(name, args)
        if problems:
            self._audit(claims, name, args, "invalid", "; ".join(problems))
            return {"status": "invalid", "problems": problems}
        result = execute_tool(name, args)
        self._audit(claims, name, args, "allowed", "ok")
        return {"status": "ok", "result": result}


def connector_request(server_url, token):
    """Keyword arguments for client.beta.messages.create: the read-only tools only."""
    return {
        "model": "claude-opus-5-5",
        "max_tokens": 16000,
        "betas": ["mcp-client-2025-11-20"],
        "mcp_servers": [{"type": "url", "url": server_url, "name": "cindervale-shipments", "authorization_token": token}],
        "tools": [{
            "type": "mcp_toolset",
            "mcp_server_name": "cindervale-shipments",
            "default_config": {"enabled": False},
            "configs": {name: {"enabled": True} for name, p in TOOL_POLICY.items() if p["tier"] == "read"},
        }],
    }


# --- Try it out (not graded) ---
log = []
server = SecureShipmentsServer(log)
reader = make_claims(scope="shipments:read")
print("reader sees:", [t["name"] for t in server.visible_tools(reader)])
print("reader cancels:", server.call(reader, "shipments_cancel", {"shipment_id": "CV-1004", "reason": "customer asked to cancel"}))
writer = make_claims(sub="ops-lead", scope="shipments:read shipments:write")
print("writer bad note:", server.call(writer, "shipments_add_note", {"shipment_id": "CV-1004", "note": "x" * 900}))
print("writer reroute:", server.call(writer, "shipments_reroute", {"shipment_id": "CV-1004", "depot": "Lyon", "reason": "Rotterdam depot closed by strike"}))
for entry in log:
    print("audit:", entry)
