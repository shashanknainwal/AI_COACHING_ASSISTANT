# TypeScript examples

The FDE posting asks for Python plus one other language. These examples use the official `@anthropic-ai/sdk`. They run on your machine with Node 20 or newer; the browser course can't run TypeScript.

| File | What it shows |
|---|---|
| `src/chatRoute.ts` | A streaming chat route in the shape of a Next.js App Router `POST` handler: text deltas streamed to the browser, a mid-stream refusal or `max_tokens` reported, the upstream stream aborted when the client disconnects |
| `src/toolLoop.ts` | A manual tool loop handling `tool_use`, `pause_turn`, `refusal`, `max_tokens` and `end_turn`, with append-only history and explicit `effort` |
| `src/mcpServer.ts` | A hand-written, minimal MCP server over stdio (JSON-RPC: `initialize`, `ping`, `tools/list`, `tools/call`). Teaching code: use an official MCP SDK for real work and check its docs |
| `src/tools.ts` | Tool definitions with `strict: true` and an executor that validates input and refuses writes without approval |
| `test/*.test.mts` | vitest tests with mocked clients: no key, no network (`.mts` keeps them out of the course site's own type-check) |

```bash
cd typescript
npm install
npm test             # no key needed
npm run typecheck
ANTHROPIC_API_KEY=sk-ant-... npm run loop -- "Where is my order QF-1002?"   # real call, a fraction of a cent on Haiku 5.5
```

To use the route in a Next.js app, put `export const POST = createChatHandler(() => new Anthropic());` in your route file, and check your Next.js version's docs for route conventions. Keep the API key on the server; never send it to the browser.
