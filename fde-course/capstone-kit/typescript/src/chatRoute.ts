// A streaming chat route in the shape of a Next.js App Router handler
// (app/api/chat/route.ts): export POST(req) returning a streaming Response.
// It uses only web-standard Request/Response/ReadableStream, so it also runs
// in other fetch-style runtimes. Check your framework's docs for where the
// file goes and which runtime it uses.
import Anthropic from "@anthropic-ai/sdk";

type ChatMessage = { role: "user" | "assistant"; content: string };

/** The subset of the client this route uses, so tests can pass a fake. */
export type StreamingClient = {
  messages: {
    stream(params: Anthropic.MessageStreamParams): AsyncIterable<Anthropic.MessageStreamEvent> & {
      finalMessage(): Promise<Anthropic.Message>;
      abort(): void;
    };
  };
};

const SYSTEM = "You are a concise support assistant for a fictional stationery shop.";
const MAX_HISTORY_CHARS = 20_000;

export function createChatHandler(getClient: () => StreamingClient) {
  return async function POST(req: Request): Promise<Response> {
    let messages: ChatMessage[];
    try {
      const body = (await req.json()) as { messages?: ChatMessage[] };
      messages = (body.messages ?? []).filter(
        (m) => (m.role === "user" || m.role === "assistant") && typeof m.content === "string",
      );
    } catch {
      return Response.json({ error: "send JSON: {messages: [{role, content}]}" }, { status: 400 });
    }
    if (!messages.length || messages[messages.length - 1].role !== "user") {
      return Response.json({ error: "the last message must come from the user" }, { status: 400 });
    }
    if (JSON.stringify(messages).length > MAX_HISTORY_CHARS) {
      return Response.json({ error: "conversation too long" }, { status: 413 });
    }

    const stream = getClient().messages.stream({
      model: "claude-haiku-5-5",
      max_tokens: 4000,
      system: [{ type: "text", text: SYSTEM, cache_control: { type: "ephemeral" } }],
      messages,
      output_config: { effort: "low" },
    });

    const encoder = new TextEncoder();
    const body = new ReadableStream<Uint8Array>({
      async start(controller) {
        try {
          for await (const event of stream) {
            if (event.type === "content_block_delta" && event.delta.type === "text_delta") {
              controller.enqueue(encoder.encode(event.delta.text));
            }
          }
          const final = await stream.finalMessage();
          // A refusal can arrive mid-stream: tell the client instead of leaving half an answer.
          if (final.stop_reason === "refusal") {
            controller.enqueue(encoder.encode("\n[The assistant can't help with this request.]"));
          } else if (final.stop_reason === "max_tokens") {
            controller.enqueue(encoder.encode("\n[Answer cut off.]"));
          }
          controller.close();
        } catch (err) {
          const message = err instanceof Anthropic.APIError ? `upstream error ${err.status}` : "stream failed";
          controller.enqueue(encoder.encode(`\n[${message}]`));
          controller.close();
        }
      },
      cancel() {
        stream.abort(); // the browser went away: stop paying for tokens nobody reads
      },
    });

    return new Response(body, { headers: { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "no-store" } });
  };
}

// In a Next.js app: export const POST = createChatHandler(() => new Anthropic());
export const POST = createChatHandler(() => new Anthropic() as unknown as StreamingClient);
