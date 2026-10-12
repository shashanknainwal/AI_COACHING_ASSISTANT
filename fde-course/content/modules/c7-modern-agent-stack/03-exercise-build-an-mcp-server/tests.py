import json


def _client():
    c = McpTestClient(ShipmentsServer())
    c.connect()
    return c


def _tool(name):
    return next((t for t in TOOLS if isinstance(t, dict) and t.get("name") == name), None)


def test_initialize():
    """initialize returns protocolVersion, capabilities and serverInfo"""
    c = McpTestClient(ShipmentsServer())
    r = c.request("initialize", {"protocolVersion": SUPPORTED_VERSIONS[-1], "capabilities": {},
                                 "clientInfo": {"name": "t", "version": "1"}})
    assert r is not None, "initialize got no response. handle() must return a JSON string for requests."
    assert r.get("jsonrpc") == "2.0" and r.get("id") == 1, f"Echo jsonrpc '2.0' and the request id. Got {r}"
    res = r.get("result") or {}
    assert res.get("protocolVersion") == SUPPORTED_VERSIONS[-1], "If you support the client's requested version, answer with that same version."
    assert "tools" in (res.get("capabilities") or {}) and "resources" in res["capabilities"], "Declare the tools and resources capabilities."
    assert res.get("serverInfo") == SERVER_INFO, "Return SERVER_INFO as serverInfo."
    r2 = c.request("initialize", {"protocolVersion": "1999-01-01", "capabilities": {}, "clientInfo": {"name": "t", "version": "1"}})
    assert (r2.get("result") or {}).get("protocolVersion") == SUPPORTED_VERSIONS[0], \
        "For a version you don't support, answer with the newest version you do support (SUPPORTED_VERSIONS[0])."


def test_notifications_get_no_response():
    """Notifications (no id) get no response"""
    s = ShipmentsServer()
    out = s.handle(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}))
    assert out is None, "A message without an id is a notification. Return None: JSON-RPC forbids replying to it."


def test_tool_definitions():
    """tools/list returns two well-described tools with JSON Schemas"""
    r = _client().request("tools/list")
    tools = (r or {}).get("result", {}).get("tools")
    assert isinstance(tools, list) and {t.get("name") for t in tools} == {"shipments_get", "shipments_search"}, \
        f"tools/list should return the two tools in TOOLS. Got {tools}"
    for t in tools:
        schema = t.get("inputSchema") or {}
        assert schema.get("type") == "object" and schema.get("required"), f"{t['name']}: inputSchema needs type 'object' and a required list."
        d = t.get("description") or ""
        assert len(d) >= 60 and "when" in d.lower(), f"{t['name']}: say what it does AND when to call it (at least 60 characters, include 'when')."
    assert _tool("shipments_get")["inputSchema"]["required"] == ["shipment_id"], "shipments_get requires shipment_id."
    assert "status" in _tool("shipments_search")["inputSchema"]["required"], "shipments_search requires status."


def test_tools_call_success():
    """tools/call returns text content with isError false"""
    r = _client().request("tools/call", {"name": "shipments_get", "arguments": {"shipment_id": "CV-1004"}})
    res = (r or {}).get("result") or {}
    assert res.get("isError") is False, f"A successful call returns isError: false. Got {r}"
    content = res.get("content") or [{}]
    assert content[0].get("type") == "text", "Return content as a list of {type: 'text', text: ...} blocks."
    assert json.loads(content[0]["text"]) == SHIPMENTS["CV-1004"], "The text should be the shipment record as JSON."
    r2 = _client().request("tools/call", {"name": "shipments_search", "arguments": {"status": "customs_hold"}})
    data = json.loads(r2["result"]["content"][0]["text"])
    expected = sorted(s["id"] for s in SHIPMENTS.values() if s["status"] == "customs_hold")
    assert sorted(s["id"] for s in data.get("shipments", [])) == expected, "shipments_search should filter by status."


def test_tool_errors_vs_protocol_errors():
    """Unknown tool is a protocol error; a missing shipment is a tool error"""
    c = _client()
    r = c.request("tools/call", {"name": "shipments_delete", "arguments": {}})
    assert (r or {}).get("error", {}).get("code") == INVALID_PARAMS, f"An unknown tool is a JSON-RPC error with code {INVALID_PARAMS}. Got {r}"
    r = c.request("tools/call", {"name": "shipments_get", "arguments": {}})
    assert (r or {}).get("error", {}).get("code") == INVALID_PARAMS, "A missing required argument is a JSON-RPC error with code -32602."
    r = c.request("tools/call", {"name": "shipments_get", "arguments": {"shipment_id": "CV-9999"}})
    res = (r or {}).get("result") or {}
    assert "error" not in r and res.get("isError") is True, \
        "A shipment that doesn't exist is a tool execution error: a normal result with isError: true, so the model can read it and recover."
    assert res.get("content") and res["content"][0].get("text"), "Put a helpful message in the error result's content."


def test_protocol_error_codes():
    """Parse errors, invalid requests and unknown methods use the standard codes"""
    s = ShipmentsServer()
    r = json.loads(s.handle("{not json") or "{}")
    assert r.get("error", {}).get("code") == PARSE_ERROR and r.get("id") is None, "Unparseable JSON: code -32700 with id null."
    r = json.loads(s.handle(json.dumps({"jsonrpc": "1.0", "id": 7, "method": "ping"})) or "{}")
    assert r.get("error", {}).get("code") == INVALID_REQUEST, "jsonrpc must be '2.0'; otherwise code -32600."
    r = json.loads(s.handle(json.dumps({"jsonrpc": "2.0", "id": "abc", "method": "shipments/delete_all"})) or "{}")
    assert r.get("error", {}).get("code") == METHOD_NOT_FOUND and r.get("id") == "abc", "Unknown method: code -32601, echoing the id (ids can be strings)."
    r = json.loads(s.handle(json.dumps({"jsonrpc": "2.0", "id": 9, "method": "ping"})) or "{}")
    assert r.get("result") == {}, "ping returns an empty result object."


def test_resources_pagination():
    """resources/list pages through every shipment with an opaque cursor"""
    c = _client()
    seen, cursor, pages = [], None, 0
    while True:
        r = c.request("resources/list", {"cursor": cursor} if cursor else {})
        res = (r or {}).get("result")
        assert isinstance(res, dict) and isinstance(res.get("resources"), list), f"resources/list should return {{'resources': [...]}}. Got {r}"
        assert len(res["resources"]) <= PAGE_SIZE, f"Return at most PAGE_SIZE ({PAGE_SIZE}) resources per page."
        seen += [x["uri"] for x in res["resources"]]
        pages += 1
        cursor = res.get("nextCursor")
        if not cursor:
            break
        assert pages < 10, "nextCursor never ran out."
    assert pages == 3, f"23 shipments at 10 per page is 3 pages. Got {pages}."
    assert sorted(seen) == sorted(f"shipment://{k}" for k in SHIPMENTS) and len(seen) == len(set(seen)), \
        "Every shipment should appear exactly once, as shipment://<id>."
    first = c.request("resources/list")["result"]["resources"][0]
    assert first.get("name") and first.get("mimeType") == "application/json", "Each resource needs a name and mimeType application/json."
    bad = c.request("resources/list", {"cursor": "not-a-real-cursor"})
    assert (bad or {}).get("error", {}).get("code") == INVALID_PARAMS, "A cursor you didn't issue is an invalid-params error (-32602)."


def test_resources_read():
    """resources/read returns contents, and a missing resource is -32002"""
    c = _client()
    r = c.request("resources/read", {"uri": "shipment://CV-1010"})
    contents = ((r or {}).get("result") or {}).get("contents")
    assert isinstance(contents, list) and contents[0].get("uri") == "shipment://CV-1010", f"Return {{'contents': [{{uri, mimeType, text}}]}}. Got {r}"
    assert json.loads(contents[0]["text"]) == SHIPMENTS["CV-1010"], "text should be the shipment as JSON."
    r = c.request("resources/read", {"uri": "shipment://CV-0000"})
    assert (r or {}).get("error", {}).get("code") == RESOURCE_NOT_FOUND, "Unknown resource: code -32002."
