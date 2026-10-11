import { describe, expect, it } from "vitest";
import { handleLine, handleMessage } from "../src/mcpServer.js";

describe("hand-written MCP server", () => {
  it("initializes and lists tools", () => {
    const init = handleMessage({ jsonrpc: "2.0", id: 1, method: "initialize", params: { protocolVersion: "2025-06-18" } }) as any;
    expect(init.result.protocolVersion).toBe("2025-06-18");
    const list = handleMessage({ jsonrpc: "2.0", id: 2, method: "tools/list" }) as any;
    expect(list.result.tools.map((t: any) => t.name)).toEqual(["get_order", "create_escalation"]);
    expect(list.result.tools[0].inputSchema.type).toBe("object");
  });

  it("calls tools, refuses writes by default, and reports protocol errors", () => {
    const ok = handleMessage({ jsonrpc: "2.0", id: 3, method: "tools/call", params: { name: "get_order", arguments: { order_id: "QF-1003" } } }, false) as any;
    expect(ok.result.isError).toBe(false);
    const write = handleMessage({ jsonrpc: "2.0", id: 4, method: "tools/call", params: { name: "create_escalation", arguments: { order_id: "x", reason: "y" } } }, false) as any;
    expect(write.result.isError).toBe(true);
    expect((handleMessage({ jsonrpc: "2.0", id: 5, method: "nope" }) as any).error.code).toBe(-32601);
    expect(handleMessage({ jsonrpc: "2.0", method: "notifications/initialized" })).toBeNull();
    expect(JSON.parse(handleLine("{bad")!).error.code).toBe(-32700);
  });
});
