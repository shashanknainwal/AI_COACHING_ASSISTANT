import json

NOTE_OK = {"shipment_id": "CV-1004", "note": "Driver called: dock 4 at 14:00"}
REROUTE_OK = {"shipment_id": "CV-1004", "depot": "Lyon", "reason": "Rotterdam depot closed by strike"}
CANCEL_OK = {"shipment_id": "CV-1005", "reason": "Customer withdrew the order today"}


def _server():
    reset_data()
    log = []
    return SecureShipmentsServer(log), log


def test_write_tools_refuse_without_scope():
    """Write tools refuse a read-only token and change nothing"""
    server, log = _server()
    reader = make_claims(scope="shipments:read")
    for name, args in [("shipments_add_note", NOTE_OK), ("shipments_reroute", REROUTE_OK), ("shipments_cancel", CANCEL_OK)]:
        r = server.call(reader, name, dict(args))
        assert (r or {}).get("status") == "denied", f"{name} with only shipments:read must be denied. Got {r}"
        assert str(r.get("reason", "")).startswith("missing_scope"), f"Say which scope is missing, e.g. missing_scope:shipments:write. Got {r}"
    assert SHIPMENTS["CV-1004"]["notes"] == [] and SHIPMENTS["CV-1004"]["destination"] != "Lyon" and SHIPMENTS["CV-1005"]["status"] != "cancelled", \
        "A denied call must never reach execute_tool."
    r = server.call(reader, "shipments_get", {"shipment_id": "CV-1004"})
    assert (r or {}).get("status") == "ok", "Reads still work with shipments:read."


def test_cancel_needs_admin():
    """Cancelling needs shipments:admin, not just write"""
    server, _ = _server()
    writer = make_claims(scope="shipments:read shipments:write")
    assert server.call(writer, "shipments_cancel", dict(CANCEL_OK)).get("status") == "denied", "Cancel is the most destructive tool: require shipments:admin."
    admin = make_claims(scope="shipments:read shipments:write shipments:admin")
    assert server.call(admin, "shipments_cancel", dict(CANCEL_OK)).get("status") == "ok", "An admin token can cancel."
    assert SHIPMENTS["CV-1005"]["status"] == "cancelled"


def test_token_checks():
    """Missing, expired and wrong-audience tokens are denied"""
    assert authorize(None, "shipments_get") == (False, "unauthenticated"), "No claims: (False, 'unauthenticated')."
    assert authorize(make_claims(exp_in=-5), "shipments_get") == (False, "expired"), "exp in the past: (False, 'expired')."
    assert authorize(make_claims(aud="https://other.example"), "shipments_get") == (False, "wrong_audience"), \
        "A token minted for another service must not work here: (False, 'wrong_audience')."
    assert authorize(make_claims(), "shipments_get") == (True, "ok")
    assert authorize(make_claims(scope="shipments:readonly"), "shipments_get")[0] is False, \
        "Scopes are space-separated tokens. 'shipments:readonly' is not 'shipments:read' (no substring matching)."


def test_validation():
    """Arguments are validated before anything runs"""
    bad = [
        ("shipments_get", {"shipment_id": "CV-1004; DROP TABLE"}),
        ("shipments_get", {"shipment_id": "CV-1004", "include_pii": True}),
        ("shipments_add_note", {"shipment_id": "CV-1004", "note": "x" * 501}),
        ("shipments_add_note", {"shipment_id": "CV-1004", "note": ""}),
        ("shipments_add_note", {"shipment_id": "CV-1004", "note": "ok\x1b[2J"}),
        ("shipments_reroute", {"shipment_id": "CV-1004", "depot": "Atlantis", "reason": "Rotterdam depot closed by strike"}),
        ("shipments_reroute", {"shipment_id": "CV-1004", "depot": "Lyon", "reason": "because"}),
        ("shipments_search", {"status": "lost"}),
    ]
    for name, args in bad:
        assert validate(name, args), f"validate({name!r}, {args!r}) should report a problem."
    for name, args in [("shipments_add_note", NOTE_OK), ("shipments_reroute", REROUTE_OK), ("shipments_search", {"status": "delayed", "destination": "Le Havre"})]:
        assert validate(name, args) == [], f"validate({name!r}, {args!r}) should pass. Got {validate(name, args)}"
    server, _ = _server()
    writer = make_claims(scope="shipments:read shipments:write")
    r = server.call(writer, "shipments_add_note", {"shipment_id": "CV-1004", "note": "x" * 900})
    assert r.get("status") == "invalid" and r.get("problems"), f"An authorised but invalid call returns status 'invalid' with problems. Got {r}"
    assert SHIPMENTS["CV-1004"]["notes"] == [], "Invalid calls must not execute."


def test_audit_log():
    """Every decision is audited, without raw arguments"""
    server, log = _server()
    secret = "Customer phone +44 7700 900123"
    writer = make_claims(sub="ops-lead", scope="shipments:read shipments:write")
    server.call(make_claims(sub="bot", scope="shipments:read"), "shipments_cancel", dict(CANCEL_OK))
    server.call(writer, "shipments_add_note", {"shipment_id": "CV-1004", "note": "x" * 900})
    server.call(writer, "shipments_add_note", {"shipment_id": "CV-1004", "note": secret})
    assert len(log) == 3, f"Audit every call, including denied and invalid ones. Got {len(log)} entries."
    assert [e.get("decision") for e in log] == ["denied", "invalid", "allowed"], f"decision should be denied, invalid, allowed. Got {[e.get('decision') for e in log]}"
    for e in log:
        for key in ("ts", "sub", "tool", "decision", "reason", "args_digest"):
            assert key in e, f"Audit entries need {key}. Got {e}"
    assert log[0]["sub"] == "bot" and log[2]["sub"] == "ops-lead", "Record who made the call (sub)."
    assert secret not in json.dumps(log), "Don't write raw arguments to the audit log: notes can contain personal data. Store a digest."
    assert log[1]["args_digest"] != log[2]["args_digest"], "Different arguments should give different digests."


def test_visible_tools_and_annotations():
    """tools/list shows only callable tools, with correct annotations"""
    server, _ = _server()
    names = [t["name"] for t in server.visible_tools(make_claims(scope="shipments:read"))]
    assert names == ["shipments_get", "shipments_search"], f"A read-only token should only see the read tools. Got {names}"
    full = server.visible_tools(make_claims(scope="shipments:read shipments:write shipments:admin"))
    by = {t["name"]: t.get("annotations") or {} for t in full}
    assert len(by) == 5, "An admin token sees all five tools."
    assert by["shipments_get"].get("readOnlyHint") is True and by["shipments_get"].get("destructiveHint") is False, "Reads: readOnlyHint true, destructiveHint false."
    assert by["shipments_add_note"].get("readOnlyHint") is False and by["shipments_add_note"].get("destructiveHint") is False \
        and by["shipments_add_note"].get("idempotentHint") is False, "add_note writes, doesn't destroy, and isn't idempotent (two calls add two notes)."
    for n in ("shipments_reroute", "shipments_cancel"):
        assert by[n].get("destructiveHint") is True and by[n].get("idempotentHint") is True, f"{n}: destructive, and repeating it has no extra effect."
    assert all(a.get("openWorldHint") is False for a in by.values()), "These tools touch only Cindervale's own system: openWorldHint false."


def test_connector_request():
    """The MCP connector request exposes only the read tools"""
    req = connector_request("https://mcp.cindervale.example/shipments", "tok_123")
    assert isinstance(req, dict), "Return the keyword arguments as a dict."
    assert "mcp-client-2025-11-20" in (req.get("betas") or []), "The MCP connector needs the mcp-client-2025-11-20 beta."
    servers = req.get("mcp_servers") or [{}]
    assert servers[0].get("type") == "url" and servers[0].get("url") and servers[0].get("name") and servers[0].get("authorization_token") == "tok_123", \
        "mcp_servers entries need type 'url', url, name and the authorization_token."
    toolset = next((t for t in req.get("tools", []) if t.get("type") == "mcp_toolset"), None)
    assert toolset and toolset.get("mcp_server_name") == servers[0]["name"], "Add an mcp_toolset whose mcp_server_name matches the server's name. Without it the request is rejected."
    assert (toolset.get("default_config") or {}).get("enabled") is False, "Allowlist mode: default_config {'enabled': False}."
    enabled = sorted(k for k, v in (toolset.get("configs") or {}).items() if v.get("enabled"))
    assert enabled == ["shipments_get", "shipments_search"], f"Enable only the read tools in configs. Got {enabled}"
