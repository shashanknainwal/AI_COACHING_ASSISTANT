---
title: "An MCP Server in TypeScript"
type: reading
minutes: 15
---

> **By the end of this lesson** you'll be able to build a small MCP server with the official TypeScript SDK: a validated read-only tool, a resource, and a stdio transport. You'll also know how input-validation failures reach the model, and what to check before you ship it to a customer.

## Start from C7

C7 taught the protocol. MCP is JSON-RPC 2.0 underneath. Servers expose tools (the model decides to call them), resources (the app attaches them) and prompts. stdio is for local servers and streamable HTTP for shared ones. Remote servers authenticate with OAuth, and annotations are hints, not security. In C7 you wrote the JSON-RPC handler by hand in Python. Here you let the official SDK handle the protocol, and you write only the tools.

## Which package

The examples use `@modelcontextprotocol/sdk` version 1.32, the package most existing servers use. Its README says v1.x is now the maintenance line. Version 2 ships as separate packages (`@modelcontextprotocol/server` and `@modelcontextprotocol/client`) and implements a newer protocol revision. Both are moving targets. Before you start a customer project, check the SDK's current docs for which line to use and what changed. The concepts below carry over; some names may not.

```bash
npm install @modelcontextprotocol/sdk zod
```

Zod is a required peer dependency. The SDK uses it to describe and validate tool inputs.

## A booking server

Fernhollow wants its support agents (and Claude Code on engineers' laptops) to look up bookings and read the cancellation policy through one server.

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const BOOKINGS: Record<string, { status: string; nights: number }> = {
  "FH-2041": { status: "confirmed", nights: 3 },
};

const server = new McpServer({ name: "fernhollow-bookings", version: "0.1.0" });

server.registerTool(
  "get_booking",
  {
    title: "Get booking",
    description: "Look up one booking by reference, for example FH-2041. Read-only.",
    inputSchema: { ref: z.string().regex(/^FH-\d{4}$/) },
    annotations: { readOnlyHint: true },
  },
  async ({ ref }) => {
    const booking = BOOKINGS[ref];
    if (!booking) {
      return { content: [{ type: "text", text: `No booking ${ref}` }], isError: true };
    }
    return { content: [{ type: "text", text: JSON.stringify({ ref, ...booking }) }] };
  },
);

server.registerResource(
  "cancellation-policy",
  "policy://cancellation",
  { title: "Cancellation policy", mimeType: "text/markdown" },
  async (uri) => ({ contents: [{ uri: uri.href, text: "Free cancellation up to 48 hours before check-in." }] }),
);

const transport = new StdioServerTransport();
await server.connect(transport);
console.error("fernhollow-bookings MCP server running on stdio"); // stdout carries the protocol
```

What the SDK does for you, and what you still own:

| The SDK handles | You own |
|---|---|
| `initialize` and version negotiation, `tools/list`, `tools/call`, `resources/list`, `resources/read` | Tool names, descriptions and schemas the model can understand |
| Turning the Zod shape into the JSON Schema clients see | What the tool is allowed to do, and for whom |
| Validating arguments against that schema before your handler runs | Validation the schema can't express (does this caller own this booking?) |
| JSON-RPC framing over stdio | Logging to stderr, never stdout |

## How errors reach the model

Two kinds of failure, as in C7:

- **A tool-level failure** (no such booking) is a normal result with `isError: true` and a message the model can act on. The model reads it and can try something else.
- **Arguments that fail the Zod schema** never reach your handler. In the SDK version tested for this lesson (1.32), the server answered a bad `ref` with a normal tool result marked `isError: true`, whose text said "Input validation error" and named the failing pattern. It did not send a JSON-RPC protocol error. That's what you want the model to see, but behaviour can differ across SDK versions, so test it in yours.
- **Protocol problems** (unknown method, malformed JSON-RPC) are JSON-RPC errors, handled by the SDK.

## Trying it

Pipe JSON-RPC lines into the server to see the wire format. Send `initialize`, then the `notifications/initialized` notification, then `tools/list` and a `tools/call`:

```bash
printf '%s\n' \
 '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"t","version":"1"}}}' \
 '{"jsonrpc":"2.0","method":"notifications/initialized"}' \
 '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"get_booking","arguments":{"ref":"FH-2041"}}}' \
 | npx tsx server.ts
```

To use it from a real client, register it as a stdio server in that client's configuration (C7 shows Claude Code and the Messages API MCP connector). The MCP connector reaches remote servers only, so a stdio server needs an HTTP transport and auth before the API can call it. The connector is in beta and not available on Bedrock or Vertex.

## Before you ship it to a customer

- **Least privilege.** Read tools and write tools behind different scopes. The destructive tool gets the tightest scope and a human confirmation in the client. Annotations like `readOnlyHint` help a client's UI, but a server can claim anything, so enforce permissions in your handler.
- **Remote means OAuth.** For streamable HTTP, validate the access token and its audience on every request, as in C7. A token minted for another service must fail.
- **Treat tool output as untrusted data** for the agent that reads it. A booking note can contain injected instructions. That risk lives in the client and agent design (C7's red-team lesson), but your server shouldn't make it worse by returning raw HTML or secrets.
- **Audit every call**: caller, tool, decision, and a hash of the arguments, not the raw arguments.
- **Test it.** The `capstone-kit/typescript/` lab has vitest tests for a hand-written MCP handler. Write the same tests against your SDK-based server: list, call, a missing booking, a bad argument.

> **Key takeaways**
> - The official SDK handles the protocol. You own tool design, permissions, extra validation and logging.
> - `registerTool` takes a Zod shape, so arguments are validated before your handler runs. Tool failures return `isError: true`.
> - stdio servers log to stderr. Remote servers need streamable HTTP plus OAuth with an audience check.
> - v1 of `@modelcontextprotocol/sdk` is the maintenance line, and v2 splits into separate packages. Check the current docs before choosing.
> - Annotations are hints. Enforce least privilege in code, and test the server like any other service.
