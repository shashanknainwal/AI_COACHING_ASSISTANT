---
title: "MCP Fundamentals: Tools, Resources, Prompts and the Wire"
type: reading
minutes: 18
---

> **By the end of this lesson you will be able to:**
> - Explain what an MCP server exposes (tools, resources, prompts) and when to use each.
> - Choose between stdio and streamable HTTP transport, and say how a remote server authenticates.
> - Scope and annotate tools, and wire a server to the Messages API MCP connector and to Claude Code.
> - Name the platforms where the MCP connector is not available.

The Model Context Protocol (MCP) is how you expose a customer's systems to Claude once and reuse that everywhere: the API, Claude Code, Claude Desktop, other agents. Instead of four copy-pasted tool definitions in four codebases, there is one server that owns access to a system, and every client speaks the same protocol to it. The FDE posting names MCP servers because building them is a core part of the job.

## What a server exposes

An MCP server offers three kinds of thing, and the distinction matters.

- **Tools** are actions the model chooses to call: `shipments_get`, `shipments_reroute`. The model decides when to use them from their names and descriptions.
- **Resources** are data the host application lists, reads and attaches as context: a shipment record, a file, a log. The application is in control, not the model.
- **Prompts** are reusable, named message templates the user can invoke, often surfaced as slash commands in a client.

A single system is often both a tool and a resource. Shipments can be a `shipments_get` tool the model calls and a `shipment://CV-1004` resource the app attaches. Lead with tools for anything the model should decide to do; use resources for data a human or the app picks.

## The wire: JSON-RPC 2.0

Underneath, MCP is JSON-RPC 2.0. A client sends a request `{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}` and the server answers with a `result` or an `error` carrying the same `id`. A message with no `id` is a notification and gets no response at all. The methods you will implement most often are `initialize` (version negotiation and capability exchange), `tools/list`, `tools/call`, `resources/list` and `resources/read`.

Two error habits matter. Use the standard JSON-RPC codes for protocol problems: parse error, invalid request, method not found, invalid params. But report a problem that happens *while a tool runs* inside the result, with `isError: true` and a message the model can act on, not as a JSON-RPC error. A deleted shipment is a tool error the model can recover from; an unknown method is a protocol error the client handles. Keeping these apart is the first thing to check when an agent silently gives up.

## Transport: stdio versus streamable HTTP

| | stdio | Streamable HTTP |
|---|---|---|
| Deployment | Local subprocess of the client | Remote web service |
| Clients | One, single session | Many, concurrent |
| Setup | Low: no network | Medium |
| Use for | Local dev tools, a developer's own machine | A shared server many agents and apps reach |

A local tool a developer runs on their laptop is usually stdio; the client launches it as a subprocess and talks over standard input and output (so a stdio server must log to stderr, never stdout, or it corrupts the protocol). A server the whole customer org reaches is streamable HTTP. The older HTTP+SSE transport is deprecated in favour of streamable HTTP.

## Auth for remote servers

A remote server needs authentication, and MCP uses OAuth 2.1 for it. The client obtains an access token and sends it; the server validates the token before doing anything, and accepts only tokens minted for itself (the audience check). Watch one trap: a hosted MCP server's OAuth bearer token is not the same thing as the underlying service's own API key. A Notion integration token authenticates against Notion's REST API but will not work as the bearer token for Notion's MCP server; they are different auth systems.

## Scoping and annotating tools

Two mechanisms keep a server safe and legible:

- **Tool scoping and least privilege.** Map each tool to the OAuth scope it needs, and give a caller only the tools its scope allows. Read tools behind a read scope, writes behind a write scope, the one truly destructive tool behind an admin scope.
- **Annotations.** Each tool can carry hints: `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`. These help a client render a confirmation before a destructive call or parallelise read-only ones. They are hints, not security guarantees: a server can claim anything, so enforce permissions in code and use annotations only for UX.

Also respect pagination on anything that lists: take a `limit`, return an opaque cursor the client passes back, and never load an entire dataset into memory.

## Wiring it to Claude

**The Messages API MCP connector** lets Claude call a remote server's tools directly, with Anthropic making the connection server-side. It needs both halves of its configuration or it is rejected:

```python
client.beta.messages.create(
    model="claude-opus-5-5", max_tokens=16000,
    betas=["mcp-client-2025-11-20"],
    mcp_servers=[{"type": "url", "url": "https://mcp.example/mcp", "name": "shipments",
                  "authorization_token": "<token>"}],
    tools=[{"type": "mcp_toolset", "mcp_server_name": "shipments"}],
    messages=[...],
)
```

The `mcp_toolset` entry references the server by name; omit it and the request fails validation. For an allowlist, set `default_config: {"enabled": False}` on the toolset and enable named tools in `configs`.

**Claude Code and Claude Desktop** take a server in their MCP configuration instead: you register the server (stdio command or HTTP URL) and it appears as tools in the session. In Claude Code that config lives alongside the project, and an org can govern which servers are allowed through managed settings.

## Platform gaps you must know

The MCP connector is in beta on the Claude API and Claude Platform on AWS, in beta on Microsoft Foundry, and **not available on Amazon Bedrock or Google Vertex AI**. A customer on Bedrock or Vertex who wants Claude to use an MCP server connects through their own MCP client instead, for example the Python SDK's MCP helpers feeding the tool runner. Always confirm the customer's platform before promising the connector.

> **Key takeaways**
> - A server exposes tools (model-chosen actions), resources (app-controlled data) and prompts (named templates).
> - The wire is JSON-RPC 2.0; keep protocol errors (standard codes) apart from tool errors (`isError: true` in the result).
> - stdio for local single-client tools, streamable HTTP for shared remote servers; remote servers authenticate with OAuth 2.1 and the audience check.
> - Scope tools to least privilege and annotate them, but enforce permissions in code because annotations are only hints.
> - The MCP connector needs `mcp_servers` and a matching `mcp_toolset`, and is not available on Bedrock or Vertex.
