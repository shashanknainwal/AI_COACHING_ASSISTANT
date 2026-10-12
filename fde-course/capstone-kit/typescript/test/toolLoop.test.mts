import { describe, expect, it } from "vitest";
import type Anthropic from "@anthropic-ai/sdk";
import { runToolLoop, type MessagesClient } from "../src/toolLoop.js";

const usage = { input_tokens: 100, output_tokens: 20, cache_read_input_tokens: 0 } as Anthropic.Usage;

function msg(content: unknown[], stop_reason: string): Anthropic.Message {
  return { id: "msg", type: "message", role: "assistant", model: "claude-haiku-5-5", content, stop_reason, usage } as unknown as Anthropic.Message;
}

function fakeClient(responses: Anthropic.Message[]) {
  const requests: Anthropic.MessageCreateParamsNonStreaming[] = [];
  const client: MessagesClient = {
    messages: {
      async create(params) {
        requests.push({ ...params, messages: [...params.messages] });
        const next = responses.shift();
        if (!next) throw new Error("no more responses");
        return next;
      },
    },
  };
  return { client, requests };
}

describe("runToolLoop", () => {
  it("runs a tool and sends the assistant content back unmodified", async () => {
    const first = [
      { type: "thinking", thinking: "", signature: "sig" },
      { type: "tool_use", id: "tu_1", name: "get_order", input: { order_id: "QF-1002" } },
    ];
    const { client, requests } = fakeClient([msg(first, "tool_use"), msg([{ type: "text", text: "Shipped." }], "end_turn")]);
    const r = await runToolLoop(client, "Where is QF-1002?");
    expect(r.status).toBe("ok");
    expect(r.text).toBe("Shipped.");
    expect(r.toolCalls).toEqual(["get_order"]);
    expect(requests[1].messages[1].content).toBe(first);
    const results = requests[1].messages[2].content as Anthropic.ToolResultBlockParam[];
    expect(results[0].tool_use_id).toBe("tu_1");
    expect(JSON.parse(results[0].content as string).status).toBe("shipped");
    expect(requests[0].output_config).toEqual({ effort: "low" });
  });

  it("runs no tools on a refusal", async () => {
    const { client } = fakeClient([msg([{ type: "tool_use", id: "t", name: "create_escalation", input: {} }], "refusal")]);
    const r = await runToolLoop(client, "x");
    expect(r.status).toBe("refused");
    expect(r.toolCalls).toEqual([]);
  });

  it("stops on max_tokens and denies writes by default", async () => {
    const { client } = fakeClient([msg([], "max_tokens")]);
    expect((await runToolLoop(client, "x")).status).toBe("truncated");
    const esc = fakeClient([
      msg([{ type: "tool_use", id: "t1", name: "create_escalation", input: { order_id: "QF-1001", reason: "dispute" } }], "tool_use"),
      msg([{ type: "text", text: "A person will review it." }], "end_turn"),
    ]);
    await runToolLoop(esc.client, "person please");
    const res = esc.requests[1].messages[2].content as Anthropic.ToolResultBlockParam[];
    expect(res[0].is_error).toBe(true);
  });

  it("re-sends a paused turn without adding a user message", async () => {
    const paused = [{ type: "text", text: "working" }];
    const { client, requests } = fakeClient([msg(paused, "pause_turn"), msg([{ type: "text", text: "done" }], "end_turn")]);
    await runToolLoop(client, "x");
    expect(requests[1].messages.at(-1)).toEqual({ role: "assistant", content: paused });
  });
});
