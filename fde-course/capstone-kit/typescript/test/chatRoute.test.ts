import { describe, expect, it } from "vitest";
import type Anthropic from "@anthropic-ai/sdk";
import { createChatHandler, type StreamingClient } from "../src/chatRoute.js";

function fakeStreamingClient(chunks: string[], stopReason: string) {
  let aborted = false;
  const client: StreamingClient = {
    messages: {
      stream() {
        const events = chunks.map(
          (text) => ({ type: "content_block_delta", index: 0, delta: { type: "text_delta", text } }) as Anthropic.MessageStreamEvent,
        );
        return {
          async *[Symbol.asyncIterator]() {
            for (const e of events) yield e;
          },
          async finalMessage() {
            return { stop_reason: stopReason } as Anthropic.Message;
          },
          abort() {
            aborted = true;
          },
        };
      },
    },
  };
  return { client, wasAborted: () => aborted };
}

const post = (body: unknown) =>
  new Request("http://localhost/api/chat", { method: "POST", body: JSON.stringify(body), headers: { "content-type": "application/json" } });

describe("chat route", () => {
  it("streams text deltas", async () => {
    const { client } = fakeStreamingClient(["Hel", "lo"], "end_turn");
    const res = await createChatHandler(() => client)(post({ messages: [{ role: "user", content: "hi" }] }));
    expect(res.status).toBe(200);
    expect(await res.text()).toBe("Hello");
  });

  it("tells the client about a mid-stream refusal", async () => {
    const { client } = fakeStreamingClient(["Partial"], "refusal");
    const res = await createChatHandler(() => client)(post({ messages: [{ role: "user", content: "x" }] }));
    expect(await res.text()).toContain("can't help");
  });

  it("rejects a bad body", async () => {
    const { client } = fakeStreamingClient([], "end_turn");
    const handler = createChatHandler(() => client);
    expect((await handler(post({ messages: [] }))).status).toBe(400);
    expect((await handler(new Request("http://x", { method: "POST", body: "nope" }))).status).toBe(400);
  });
});
