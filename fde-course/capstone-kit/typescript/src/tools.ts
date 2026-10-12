// Tool definitions and a tiny fake customer system shared by the tool loop and the MCP server.
// Quillfeather Stationery is a fictional shop. Replace this with your own domain.
import type Anthropic from "@anthropic-ai/sdk";

const ORDERS: Record<string, { status: string; eta?: string; items: string[] }> = {
  "QF-1001": { status: "delivered", items: ["Fountain pen, navy (engraved)"] },
  "QF-1002": { status: "shipped", eta: "2026-10-08", items: ["A5 dotted notebook x2"] },
  "QF-1003": { status: "processing", items: ["Black ink, 50 ml x4"] },
};

export const TOOLS: Anthropic.Tool[] = [
  {
    name: "get_order",
    description: "Look up one order by its order number (format QF-1234). Read-only.",
    strict: true,
    input_schema: {
      type: "object",
      properties: { order_id: { type: "string", description: "Order number, e.g. QF-1001" } },
      required: ["order_id"],
      additionalProperties: false,
    },
  },
  {
    name: "create_escalation",
    description: "Ask a human agent to take over. Needs operator approval; may be declined.",
    strict: true,
    input_schema: {
      type: "object",
      properties: {
        order_id: { type: "string" },
        reason: { type: "string" },
      },
      required: ["order_id", "reason"],
      additionalProperties: false,
    },
  },
];

export type ToolOutcome = { content: string; isError: boolean };
export type Approver = (name: string, input: Record<string, unknown>) => boolean;

/** Run one tool. Never throws: errors come back as results the model can read. */
export function executeTool(
  name: string,
  input: unknown,
  approve: Approver = () => false,
): ToolOutcome {
  // Tool input is model output: validate it before acting.
  if (typeof input !== "object" || input === null) {
    return { content: JSON.stringify({ error: "input must be an object" }), isError: true };
  }
  const args = input as Record<string, unknown>;
  if (name === "get_order") {
    if (typeof args.order_id !== "string") {
      return { content: JSON.stringify({ error: "order_id must be a string" }), isError: true };
    }
    const id = args.order_id.trim().toUpperCase();
    const order = ORDERS[id];
    return order
      ? { content: JSON.stringify({ order_id: id, ...order }), isError: false }
      : { content: JSON.stringify({ error: `No order ${id}` }), isError: true };
  }
  if (name === "create_escalation") {
    if (!approve(name, args)) {
      return { content: JSON.stringify({ error: "Escalation not approved by the operator." }), isError: true };
    }
    return { content: JSON.stringify({ ticket_id: "ESC-001", ...args }), isError: false };
  }
  return { content: JSON.stringify({ error: `unknown tool ${name}` }), isError: true };
}
