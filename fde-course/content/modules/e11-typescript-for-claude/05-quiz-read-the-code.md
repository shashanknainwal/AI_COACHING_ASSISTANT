---
title: "Code-Reading Check: What Does This Do?"
type: quiz
minutes: 15
questions:
  - q: "Snippet 1. A Sonnet 5.5 call with max_tokens 64 and no effort set. What is the most likely output?"
    options:
      - "end_turn text, because 64 tokens is plenty for a short policy answer"
      - "A 400 error, because max_tokens must be at least 1,024"
      - "max_tokens thinking, because thinking used up the token limit first"
      - "refusal text, because short limits trigger the safety classifiers"
    answer: 2
    explain: "Sonnet 5.5 defaults to high effort and thinks before answering. Thinking counts toward max_tokens, so a tiny limit is spent on an (empty under the default display) thinking block before any text."
  - q: "Snippet 2. What happens when you run tsc with strict mode on this line?"
    options:
      - "A compile error, because content[0] may be a block with no text field"
      - "It compiles, then throws at runtime only if the first block is thinking"
      - "It compiles cleanly, because the SDK types content as text blocks"
      - "A compile error, because response must be awaited a second time"
    answer: 0
    explain: "response.content is a union of block types. TypeScript refuses .text until you narrow with block.type === \"text\", which is exactly the bug Python would only show at runtime."
  - q: "Snippet 3. The route streams fine in testing. What goes wrong in production?"
    options:
      - "The API key is sent to the browser inside the stream"
      - "Text arrives out of order because the deltas are never sorted by index"
      - "The stream never closes, so the browser waits forever"
      - "When users close the tab, generation keeps running and is billed"
    answer: 3
    explain: "There's no cancel() handler calling stream.abort(), so a disconnect doesn't stop the upstream call. Tokens nobody reads are still generated and billed."
  - q: "Snippet 4. The loop runs a tool and sends the result back. What does the second API call return?"
    options:
      - "A normal answer, because the tool result carries the tool name"
      - "A 400, because the tool_result has no matching tool_use in the previous assistant turn"
      - "A refusal, because the model can't see where the result came from"
      - "A pause_turn, because the history now needs to be resumed later"
    answer: 1
    explain: "The assistant turn was replaced with its text only, so the tool_use block (and its id) is gone. Append response.content unmodified."
  - q: "Snippet 5. The policy document is 20,000 tokens and has cache_control on it. Why is cache_read_input_tokens always 0?"
    options:
      - "Automatic caching must also be turned on at the top level"
      - "The timestamp before the document changes the prefix on every request"
      - "Documents over 10,000 tokens are too large to be cached"
      - "Cache reads are reported only on the Batches API"
    answer: 1
    explain: "Caching is a prefix match. The ISO timestamp in the earlier system block changes every request, which invalidates everything after it. Move volatile content after the cached prefix."
  - q: "Snippet 6. The model asked for three tools in one turn. Is this code correct?"
    options:
      - "No: Promise.all may reorder results, so ids won't match"
      - "No: each tool_result must be sent in its own user message"
      - "No: parallel tool calls must be disabled on current models"
      - "Yes: each result carries its tool_use_id, and all go back in one message"
    answer: 3
    explain: "Running tools concurrently is fine. Promise.all keeps the input order anyway, and matching is by tool_use_id. All results go in the next user message."
  - q: "Snippet 7. What does the TypeScript compiler say about this catch block under strict mode?"
    options:
      - "Error: err is of type unknown, so err.message is not allowed"
      - "Nothing: err is typed as Anthropic.APIError automatically"
      - "Nothing: catch variables are always typed as any in TypeScript"
      - "Error: a catch block must rethrow every error it receives"
    answer: 0
    explain: "Strict mode types catch variables as unknown. The fix is also the better design: check err instanceof Anthropic.RateLimitError instead of matching message strings."
  - q: "Snippet 8. Claude Code launches this MCP server over stdio and immediately reports a connection error. Why?"
    options:
      - "registerTool must be called after server.connect, never before it"
      - "Zod shapes are not accepted as inputSchema by the SDK"
      - "console.log writes to stdout, which corrupts the JSON-RPC stream"
      - "stdio servers need an OAuth token before initialize"
    answer: 2
    explain: "On stdio, stdout carries the protocol. Log to stderr (console.error) instead."
---

Eight short snippets from Fernhollow's codebase (fictional). Read each one, then answer the matching question below. All of them use `@anthropic-ai/sdk` or `@modelcontextprotocol/sdk`. You need 7 correct to pass.

**Snippet 1**

```typescript
const r = await client.messages.create({
  model: "claude-sonnet-5-5",
  max_tokens: 64,
  messages: [{ role: "user", content: "Explain our refund policy for group bookings." }],
});
console.log(r.stop_reason, r.content.map((b) => b.type).join(","));
```

**Snippet 2**

```typescript
const response = await client.messages.create(params);
const answer: string = response.content[0].text;
```

**Snippet 3**

```typescript
export async function POST(request: Request) {
  const { messages } = await request.json();
  const stream = client.messages.stream({ model: "claude-sonnet-5-5", max_tokens: 4000, messages });
  const body = new ReadableStream({
    async start(controller) {
      for await (const event of stream) {
        if (event.type === "content_block_delta" && event.delta.type === "text_delta") {
          controller.enqueue(new TextEncoder().encode(event.delta.text));
        }
      }
      controller.close();
    },
  });
  return new Response(body);
}
```

**Snippet 4**

```typescript
const response = await client.messages.create({ model, max_tokens: 8000, tools, messages });
const toolUse = response.content.find((b): b is Anthropic.ToolUseBlock => b.type === "tool_use");
const text = response.content.filter((b): b is Anthropic.TextBlock => b.type === "text").map((b) => b.text).join("");
if (toolUse) {
  messages.push({ role: "assistant", content: text });
  messages.push({
    role: "user",
    content: [{ type: "tool_result", tool_use_id: toolUse.id, content: await runTool(toolUse.name, toolUse.input) }],
  });
  const next = await client.messages.create({ model, max_tokens: 8000, tools, messages });
}
```

**Snippet 5**

```typescript
const r = await client.messages.create({
  model: "claude-sonnet-5-5",
  max_tokens: 2000,
  system: [
    { type: "text", text: `You are Fernhollow's policy assistant. Now: ${new Date().toISOString()}` },
    { type: "text", text: policyDoc, cache_control: { type: "ephemeral" } },
  ],
  messages: [{ role: "user", content: question }],
});
console.log(r.usage.cache_read_input_tokens);
```

**Snippet 6**

```typescript
const toolUses = response.content.filter((b): b is Anthropic.ToolUseBlock => b.type === "tool_use");
const results: Anthropic.ToolResultBlockParam[] = await Promise.all(
  toolUses.map(async (t) => ({ type: "tool_result" as const, tool_use_id: t.id, content: await run(t.name, t.input) })),
);
messages.push({ role: "assistant", content: response.content });
messages.push({ role: "user", content: results });
```

**Snippet 7**

```typescript
try {
  await client.messages.create(params);
} catch (err) {
  if (err.message.includes("rate")) await retryLater();
}
```

**Snippet 8**

```typescript
const server = new McpServer({ name: "fernhollow-bookings", version: "0.1.0" });
server.registerTool("get_booking", { description: "Look up a booking.", inputSchema: { ref: z.string() } },
  async ({ ref }) => {
    console.log("looking up", ref);
    return { content: [{ type: "text", text: lookup(ref) }] };
  });
await server.connect(new StdioServerTransport());
```
