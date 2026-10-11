---
title: "Exercise: Build an MCP Server for Shipments"
type: exercise
minutes: 50
hints:
  - "Write `handle` first: `json.loads` inside a try (a failure is a parse error with id null), then a dispatcher that maps method names to small functions. Every response is `{\"jsonrpc\": \"2.0\", \"id\": <same id>, \"result\" or \"error\": ...}`."
  - "A message with no `id` is a notification. JSON-RPC forbids replying to one, so return None even for `notifications/initialized`."
  - "Keep two kinds of failure apart. Something wrong with the *request* (unknown method, unknown tool, missing required argument, bad cursor) is a JSON-RPC `error`. Something that went wrong *while running the tool* (no such shipment) is a normal `result` with `isError: true` and a message the model can act on."
  - "The cursor only has to round-trip through your own server. Base64 of `offset:10` works. Decode it inside a try and treat anything you can't decode, or an offset out of range, as invalid params. Omit `nextCursor` entirely on the last page."
  - "For version negotiation: if the client's `protocolVersion` is in `SUPPORTED_VERSIONS`, echo it; otherwise answer with `SUPPORTED_VERSIONS[0]` and let the client decide whether it can continue."
---

Rhea Petrakis runs platform engineering at Cindervale Freight, a fictional European freight forwarder. "Every team here wants Claude to look up shipments. Right now that's four copy-pasted tool definitions in four codebases, each with its own bugs. I want one MCP server that owns shipment access, and every agent, Claude Code session and internal app talks to it. Before we wire it to real systems, show me a server that speaks the protocol correctly: tools, resources, proper errors and pagination. My team will port it to the official SDK once we trust the shapes."

This is the core of an MCP server with the transport stripped away. Over stdio, a client writes one JSON-RPC message per line to your process. Over streamable HTTP, it POSTs the same messages. Either way, your code receives a JSON string and returns one. The shipment records (`SHIPMENTS`), `SUPPORTED_VERSIONS`, `SERVER_INFO`, `PAGE_SIZE`, the error-code constants and a small `McpTestClient` are given.

## Your task

Fill in `TOOLS` and the `ShipmentsServer` class. `handle(raw)` takes one raw message and returns the raw response string, or `None`.

**Messages to support**

| Method | Result |
|---|---|
| `initialize` | `{"protocolVersion": ..., "capabilities": {"tools": {}, "resources": {}}, "serverInfo": SERVER_INFO}` |
| `ping` | `{}` |
| `tools/list` | `{"tools": TOOLS}` |
| `tools/call` | `{"content": [{"type": "text", "text": "<json>"}], "isError": false}` |
| `resources/list` | `{"resources": [{"uri": "shipment://CV-1001", "name": "Shipment CV-1001", "mimeType": "application/json"}, ...], "nextCursor": "..."}` |
| `resources/read` | `{"contents": [{"uri": ..., "mimeType": "application/json", "text": "<json>"}]}` |
| `notifications/initialized` (no `id`) | no response |

**Tools.** `shipments_get` takes a required `shipment_id` and returns that record. `shipments_search` takes a required `status` (one of the five statuses in the data) and an optional exact `destination`, and returns `{"count": n, "shipments": [...]}`. Each tool needs an `inputSchema` (JSON Schema, `type: object`, with `required`) and a description that says what it does and when to call it.

**Errors.** Use the standard codes:

| Situation | Response |
|---|---|
| Not valid JSON | error `-32700`, `id: null` |
| `jsonrpc` isn't `"2.0"`, or no `method` | error `-32600` |
| Unknown method | error `-32601` |
| Unknown tool, missing required argument, bad cursor | error `-32602` |
| Unknown resource URI | error `-32002` |
| Shipment ID not found in `shipments_get` | **result** with `isError: true` and a helpful text message |

**Pagination.** `resources/list` returns at most `PAGE_SIZE` resources, sorted by ID. Include an opaque `nextCursor` while more remain and leave it out on the last page. Reject cursors you didn't issue.

## Example

```python
client = McpTestClient(ShipmentsServer())
client.connect()
client.request("tools/call", {"name": "shipments_get", "arguments": {"shipment_id": "CV-9999"}})
# {"jsonrpc": "2.0", "id": 2, "result": {"content": [{"type": "text",
#   "text": "{\"error\": \"No shipment CV-9999. Check the ID or search by status.\"}"}], "isError": true}}
```

## Why it's built this way

- **Tool errors go back to the model; protocol errors go to the client.** The model can read an `isError` result and try another ID. It never sees a JSON-RPC error: the client handles that. This split comes from the MCP spec, and it's the first thing to check when an agent "silently gives up".
- **Resources are for the application, tools are for the model.** A resource is data the host app can list, read and attach as context. A tool is an action the model chooses. Exposing shipments as both is common.
- **Opaque cursors.** The client must not build cursors itself. That leaves you free to switch from offsets to database keys later without breaking anyone.
- **In production, use the official SDK.** The Python and TypeScript MCP SDKs handle framing, sessions and capability negotiation for you. Knowing the wire shapes is what lets you debug them. The TypeScript version of this server (`@modelcontextprotocol/sdk`) is in the local capstone kit under `capstone-kit/typescript/`.

In a debrief, expect: "What's the difference between a tool and a resource?" and "Your agent keeps retrying a deleted shipment. Where do you look?"
