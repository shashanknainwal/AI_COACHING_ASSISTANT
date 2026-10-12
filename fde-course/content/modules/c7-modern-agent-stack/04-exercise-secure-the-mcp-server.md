---
title: "Exercise: Secure the MCP Server"
type: exercise
minutes: 45
hints:
  - "Order matters in `call`: authorize, then validate, then execute. Audit after each decision, including the denials. A call that fails authorization should never reach `validate`'s error messages or `execute_tool`."
  - "OAuth scopes arrive as one space-separated string. Split it and check membership. `'shipments:read' in 'shipments:readonly'` is True as a substring, which is exactly the bug the tests look for."
  - "Treat the JSON Schema as a contract you enforce yourself. Reject unknown keys, check the ID with a regular expression, bound every string, and refuse control characters in free text (they can corrupt terminals and logs)."
  - "Annotations are per tool: reads are read-only and not destructive. A note is a write that isn't destructive, and two identical calls add two notes, so it isn't idempotent. Reroute and cancel overwrite state, and repeating them changes nothing more."
  - "The connector half: `mcp_servers` declares the server, and an `mcp_toolset` with the same `mcp_server_name` exposes its tools. `default_config: {\"enabled\": False}` plus `configs` keyed by tool name turns it into an allowlist."
---

Rhea is back. "The server works. Now security wants it before it touches production. Dispatch bots get read access. Ops leads can add notes and reroute. Only two people can cancel. Every call, allowed or not, goes in an audit log that security can read without seeing customer data. And the first agent we connect through the Messages API should only ever see the read tools, even though the server has five."

The server now has three write tools. `BASE_TOOLS`, `execute_tool` (the unprotected business logic, which trusts its input completely), `AUDIENCE`, `NOW`, `DEPOTS`, `STATUSES`, `SHIPMENTS`, `reset_data()` and `make_claims(...)` are given. `make_claims` returns decoded access-token claims, as your OAuth middleware would hand them over after checking the signature.

## Your task

**1. `TOOL_POLICY`.** For each tool, its tier (`"read"` or `"write"`) and the scope it needs: `shipments:read` for get and search, `shipments:write` for add_note and reroute, `shipments:admin` for cancel.

**2. `annotations(tool_name)`** returns the four MCP annotations: `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`. All five tools touch only Cindervale's own system.

**3. `validate(tool_name, args)`** returns a list of problems (empty means valid):

- no keys outside the tool's schema;
- `shipment_id` matches `CV-` plus four digits;
- `status` is one of `STATUSES`; `destination`, if given, is a city name of up to 64 letters, spaces or hyphens;
- `note` is 1 to 500 characters with no control characters (newlines are fine);
- `depot` is one of `DEPOTS`; `reason` is 10 to 300 characters.

**4. `authorize(claims, tool_name)`** returns `(allowed, reason)`, checking in this order:

| Check | Reason when it fails |
|---|---|
| Tool exists in `TOOL_POLICY` | `"unknown_tool"` |
| Claims present | `"unauthenticated"` |
| `exp` later than `NOW` | `"expired"` |
| `aud` equals `AUDIENCE` | `"wrong_audience"` |
| Required scope in the space-separated `scope` | `"missing_scope:<scope>"` |

Success is `(True, "ok")`.

**5. `SecureShipmentsServer`**

- `visible_tools(claims)` returns only the tools this caller may call, each with an `annotations` key.
- `call(claims, name, args)` returns `{"status": "denied", "reason": ...}`, `{"status": "invalid", "problems": [...]}` or `{"status": "ok", "result": ...}`.
- Append one audit entry per call: `ts`, `sub`, `tool`, `decision` (`denied`, `invalid` or `allowed`), `reason`, and `args_digest` (a short SHA-256 of the canonical JSON). Never log the raw arguments.

**6. `connector_request(server_url, token)`** returns the keyword arguments for `client.beta.messages.create`: `model`, `max_tokens`, the `mcp-client-2025-11-20` beta, one `mcp_servers` entry with the token, and an `mcp_toolset` in allowlist mode that enables only the read tools.

## Example

```python
server.call(make_claims(scope="shipments:read"), "shipments_cancel",
            {"shipment_id": "CV-1004", "reason": "customer asked to cancel"})
# {"status": "denied", "reason": "missing_scope:shipments:admin"}
```

## Why it's built this way

- **Least privilege at two layers.** The server enforces scopes, and the client exposes only the tools it needs. Either layer alone fails open when someone misconfigures it.
- **Annotations are hints, not controls.** The MCP spec says clients shouldn't make security decisions from annotations alone, because a server can claim anything. Use them for UX (confirm before a destructive call) and enforce permissions in code.
- **Audience checks stop token reuse.** A token minted for another internal service must not work here, even if it carries the right-looking scope.
- **In a real deployment**, the HTTP layer rejects a missing or expired token with 401 and an insufficient scope with 403 before the message reaches the handler. The decision logic is the same function. Vendor features differ by platform: the MCP connector is in beta on the Claude API and is not available on Amazon Bedrock or Google Vertex AI, so a customer there connects through their own MCP client, for example the Python SDK's MCP helpers with the tool runner.

In a debrief, expect: "A prompt injection tells the agent to cancel every delayed shipment. Walk me through what stops it."
