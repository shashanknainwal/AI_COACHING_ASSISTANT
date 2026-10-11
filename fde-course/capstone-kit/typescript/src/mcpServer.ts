// A minimal MCP server over stdio, HAND-WRITTEN FOR TEACHING (not the official SDK).
// JSON-RPC 2.0, one message per line on stdin/stdout. Implements initialize,
// ping, tools/list and tools/call. For real use, take an official MCP SDK and
// check its current docs. Run: npx tsx src/mcpServer.ts
import { createInterface } from "node:readline";
import { pathToFileURL } from "node:url";
import { TOOLS, executeTool } from "./tools.js";

// Protocol revisions this stub answers to, newest first. Check the MCP spec for the current list.
export const SUPPORTED_VERSIONS = ["2025-06-18", "2025-03-26", "2024-11-05"];

type JsonRpcRequest = { jsonrpc: "2.0"; id?: number | string; method: string; params?: Record<string, unknown> };
type JsonRpcResponse =
  | { jsonrpc: "2.0"; id: number | string | null; result: unknown }
  | { jsonrpc: "2.0"; id: number | string | null; error: { code: number; message: string } };

const err = (id: number | string | null, code: number, message: string): JsonRpcResponse => ({
  jsonrpc: "2.0",
  id,
  error: { code, message },
});

/** Handle one message. Returns null for notifications (no id), which get no reply. */
export function handleMessage(msg: unknown, allowWrites = process.env.CAPSTONE_MCP_ALLOW_WRITES === "1"): JsonRpcResponse | null {
  const m = msg as JsonRpcRequest;
  if (!m || m.jsonrpc !== "2.0" || typeof m.method !== "string") return err(null, -32600, "invalid request");
  if (m.id === undefined) return null;
  const id = m.id;
  const params = m.params ?? {};
  switch (m.method) {
    case "initialize": {
      const requested = params.protocolVersion as string | undefined;
      return {
        jsonrpc: "2.0",
        id,
        result: {
          protocolVersion: requested && SUPPORTED_VERSIONS.includes(requested) ? requested : SUPPORTED_VERSIONS[0],
          capabilities: { tools: { listChanged: false } },
          serverInfo: { name: "quillfeather-customer-system", version: "0.1.0" },
        },
      };
    }
    case "ping":
      return { jsonrpc: "2.0", id, result: {} };
    case "tools/list":
      return {
        jsonrpc: "2.0",
        id,
        result: { tools: TOOLS.map((t) => ({ name: t.name, description: t.description, inputSchema: t.input_schema })) },
      };
    case "tools/call": {
      const name = params.name as string;
      if (!TOOLS.some((t) => t.name === name)) return err(id, -32602, `unknown tool: ${name}`);
      // An MCP server can't see a human, so writes are off unless the operator enables them.
      const out = executeTool(name, params.arguments ?? {}, () => allowWrites);
      return { jsonrpc: "2.0", id, result: { content: [{ type: "text", text: out.content }], isError: out.isError } };
    }
    default:
      return err(id, -32601, `method not found: ${m.method}`);
  }
}

export function handleLine(line: string): string | null {
  let msg: unknown;
  try {
    msg = JSON.parse(line);
  } catch {
    return JSON.stringify(err(null, -32700, "parse error"));
  }
  const res = handleMessage(msg);
  return res ? JSON.stringify(res) : null;
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? "").href) {
  const rl = createInterface({ input: process.stdin });
  rl.on("line", (line) => {
    if (!line.trim()) return;
    const out = handleLine(line);
    if (out) process.stdout.write(out + "\n"); // stdout is for protocol messages only; log to stderr
  });
}
