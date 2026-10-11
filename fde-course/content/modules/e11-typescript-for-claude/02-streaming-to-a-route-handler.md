---
title: "Streaming Claude to a Next.js Route Handler"
type: reading
minutes: 15
---

> **By the end of this lesson** you'll be able to write a Next.js App Router route handler that streams Claude's text to the browser, handle a refusal or truncation mid-stream, stop paying for tokens when the user closes the tab, and spot the three streaming bugs that show up most in customer code.

## Why streaming is a server-side job

Fernhollow's booking assistant runs in the browser, but the API key must never reach the browser. So the browser calls Fernhollow's own server route, and that route calls Claude and streams the answer back. In the Next.js App Router, that route is a file like `app/api/chat/route.ts` that exports an async function named after the HTTP method. It receives a web-standard `Request` and returns a `Response`. Check your Next.js version's docs for the exact file conventions and runtime options; they change between major versions.

## The route

```typescript
// app/api/chat/route.ts
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

export async function POST(request: Request): Promise<Response> {
  const { messages } = (await request.json()) as { messages: Anthropic.MessageParam[] };

  const stream = client.messages.stream({
    model: "claude-sonnet-5-5",
    max_tokens: 4000,
    output_config: { effort: "low" },
    system: [{ type: "text", text: "You are a concise travel assistant.", cache_control: { type: "ephemeral" } }],
    messages,
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
        if (final.stop_reason === "refusal") controller.enqueue(encoder.encode("\n[declined]"));
        if (final.stop_reason === "max_tokens") controller.enqueue(encoder.encode("\n[cut off]"));
        controller.close();
      } catch (err) {
        controller.error(err);
      }
    },
    cancel() {
      stream.abort();
    },
  });

  return new Response(body, {
    headers: { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "no-store" },
  });
}
```

Read it top to bottom:

1. **`client.messages.stream(...)`** starts the request and returns a stream object you can iterate with `for await`. Each item is a server-sent event: `message_start`, `content_block_start`, `content_block_delta`, `content_block_stop`, `message_delta`, `message_stop`.
2. **Only text deltas go to the browser.** With adaptive thinking, the stream can contain `thinking` blocks first. Under the default display their text is empty, so they show up as a pause before the first visible token. Effort is set to `low` here because a chat reply doesn't need deep reasoning, and thinking sits inside time to first token.
3. **`finalMessage()`** resolves with the complete `Anthropic.Message` once the stream ends: `stop_reason`, full `usage`, every block. Use it instead of wrapping `.on()` callbacks in your own `Promise`.
4. **Stop reasons still matter mid-stream.** A refusal can arrive after some text was already sent, and a long answer can hit `max_tokens`. Tell the user instead of leaving half an answer that looks complete.
5. **`cancel()` aborts the upstream call.** When the browser disconnects, the `ReadableStream` is cancelled. Calling `stream.abort()` stops generation, so you stop paying for tokens nobody reads.

A simpler way to read text only:

```typescript
let out = "";
stream.on("text", (delta) => { out += delta; });
await stream.finalMessage();
```

Use the `for await` form when you need to forward bytes as they arrive, and `on("text")` when you just want the deltas.

## Plain text or server-sent events to the browser?

The route above streams plain text, which is the simplest thing a front end can read with `fetch` and a reader. If the browser also needs structured signals (a "tool running" indicator, a typed error, usage at the end), forward your own small event format instead, for example newline-delimited JSON objects such as `{"type": "text", "text": "..."}`. Either way, the browser never sees the API key or the raw upstream stream.

## Three bugs you'll find in customer code

**1. Buffering the whole answer.**

```typescript
const msg = await client.messages.create({ ...params });
return Response.json({ text: msg.content });
```

This isn't streaming. The user waits for the entire answer. For long outputs it can also hit HTTP timeouts. The SDK docs recommend streaming for large `max_tokens` (above roughly 16K). Proxies and some hosting setups buffer responses too, so check that the first bytes actually arrive early in production, not just locally.

**2. Ignoring disconnects.** Without `cancel()` and `abort()`, a user who closes the tab leaves the model generating to the end. At scale that's real money and rate-limit headroom spent on nothing.

**3. Trusting the client's message history.** The route accepts `messages` from the browser. A malicious client can send a fake `assistant` turn, a huge history, or a system-style instruction in a user turn. Validate roles and types, cap the size, and keep the system prompt on the server. Also note that a final `assistant` message (a prefill) returns a 400 on Opus 5.5 and other current models, so make sure the last message is from the user.

## Where to put the key

- Only in server-side environment variables, read by `new Anthropic()`.
- Never in a variable that your framework exposes to the browser bundle. Many frameworks expose variables with a public prefix; check yours.
- Rate-limit the route per user. Your own endpoint is now a way to spend your API budget.

> **Key takeaways**
> - The browser calls your route, and only the route calls Claude. The key stays on the server.
> - Iterate the stream, forward text deltas, then read `finalMessage()` for the stop reason and usage.
> - Report refusals and truncation mid-stream instead of leaving half an answer.
> - Abort the upstream stream when the client disconnects.
> - Validate the client's history, cap its size, and make sure the last message comes from the user.
