---
title: "Tool Loops, Structured Outputs and Prompt Caching in TypeScript"
type: reading
minutes: 18
---

> **By the end of this lesson** you'll be able to write a manual tool loop that handles every stop reason, use the SDK's tool runner with Zod tools, get schema-checked JSON with `messages.parse`, cache a stable prefix and prove the cache hit, and explain each choice to a customer's TypeScript team.

## A manual tool loop

You met this loop in Python in E2. Here it is in TypeScript for Fernhollow's booking assistant.

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

const tools: Anthropic.Tool[] = [
  {
    name: "get_booking",
    description: "Look up one booking by reference, for example FH-2041. Read-only.",
    strict: true,
    input_schema: {
      type: "object",
      properties: { ref: { type: "string" } },
      required: ["ref"],
      additionalProperties: false,
    },
  },
];

async function runTool(name: string, input: unknown): Promise<{ content: string; isError: boolean }> {
  if (name !== "get_booking") return { content: `unknown tool ${name}`, isError: true };
  const ref = (input as { ref?: unknown }).ref;
  if (typeof ref !== "string") return { content: "ref must be a string", isError: true };
  return { content: JSON.stringify({ ref, status: "confirmed" }), isError: false };
}

export async function agent(question: string): Promise<string> {
  const messages: Anthropic.MessageParam[] = [{ role: "user", content: question }];
  for (let turn = 0; turn < 8; turn++) {
    const response = await client.messages.create({
      model: "claude-sonnet-5-5",
      max_tokens: 8000,
      output_config: { effort: "medium" },
      tools,
      messages,
    });
    if (response.stop_reason === "pause_turn") {
      messages.push({ role: "assistant", content: response.content });
      continue;
    }
    if (response.stop_reason !== "tool_use") {
      return response.content
        .filter((b): b is Anthropic.TextBlock => b.type === "text")
        .map((b) => b.text)
        .join("");
    }
    messages.push({ role: "assistant", content: response.content }); // unmodified, thinking included
    const results: Anthropic.ToolResultBlockParam[] = [];
    for (const block of response.content) {
      if (block.type !== "tool_use") continue;
      const out = await runTool(block.name, block.input);
      results.push({ type: "tool_result", tool_use_id: block.id, content: out.content, is_error: out.isError });
    }
    messages.push({ role: "user", content: results });
  }
  throw new Error("too many turns");
}
```

The points an interviewer or a customer's reviewer will look for:

- **`response.content` goes back unmodified**, thinking blocks included. On Opus 5.5, Sonnet 5.5, Haiku 5.5 and Fable 5.1, thinking blocks are tied to the conversation, and editing earlier turns returns a 400 by default for newer accounts. History is append-only.
- **Every `tool_use` gets exactly one `tool_result`**, matched by `tool_use_id`, all in the next user message. There can be several tool calls in one turn.
- **Tool input is model output.** `strict: true` makes the arguments match the schema, but the values are still untrusted. Validate before acting, and never let a model-supplied path or id reach a system unchecked.
- **Tool errors are results, not exceptions.** `is_error: true` with a message the model can act on lets it recover.
- **`pause_turn`** happens with server-side tools: append the paused turn and send again.
- **A turn cap.** Agents loop. Cap turns and spend.
- **This loop is simplified.** It treats `max_tokens` and `refusal` as "return the text". A production loop handles them separately: never run tools from a turn that hit `max_tokens` or was refused, because a tool input can be cut off. The `capstone-kit/typescript/src/toolLoop.ts` file in the lab does this.

### Don't force a tool

Older code often forced a call with `tool_choice: { type: "tool", name: "get_booking" }`. On Opus 5.5, Sonnet 5.5 and Fable 5.1, forcing a tool (`any` or `tool`) returns a 400. Use `auto` (the default), say in the prompt which tool to use, keep `strict: true`, and check that a `tool_use` came back. If you only wanted JSON, use structured outputs instead.

## The tool runner

The SDK has a tool runner (beta) that runs the loop for you. With Zod, the tool's schema and its implementation live together:

```typescript
import Anthropic from "@anthropic-ai/sdk";
import { betaZodTool } from "@anthropic-ai/sdk/helpers/beta/zod";
import { z } from "zod";

const client = new Anthropic();

const getBooking = betaZodTool({
  name: "get_booking",
  description: "Look up one booking by reference. Read-only.",
  inputSchema: z.object({ ref: z.string().describe("Booking reference, e.g. FH-2041") }),
  run: async ({ ref }) => JSON.stringify({ ref, status: "confirmed" }),
});

export async function viaRunner(question: string) {
  const final = await client.beta.messages.toolRunner({
    model: "claude-sonnet-5-5",
    max_tokens: 8000,
    output_config: { effort: "medium" },
    tools: [getBooking],
    messages: [{ role: "user", content: question }],
  });
  return final.stop_reason;
}
```

With `betaZodTool`, the runner validates each input against the Zod schema before calling `run`. Two cautions from the SDK docs:

- **The runner doesn't resume `pause_turn`.** If you mix in server tools, check `stop_reason` on each iteration and resume yourself.
- **The runner doesn't apply the stop-reason rules for you.** Check for `max_tokens` with a pending tool call, and for `refusal`.

When should you write the loop by hand? When you need control the runner doesn't give: a custom transport, approval flows wired in a particular way, or avoiding a beta dependency. For a customer's first agent, the runner is less code to get wrong.

## Structured outputs with Zod

To get JSON that matches a schema, use `output_config.format`. With Zod and `messages.parse`, you get a typed object back:

```typescript
import Anthropic from "@anthropic-ai/sdk";
import { z } from "zod";
import { zodOutputFormat } from "@anthropic-ai/sdk/helpers/zod";

const client = new Anthropic();

const Trip = z.object({
  destination: z.string(),
  nights: z.number().int(),
  travellers: z.number().int(),
  flexible_dates: z.boolean(),
});

export async function extractTrip(text: string) {
  const response = await client.messages.parse({
    model: "claude-haiku-5-5",
    max_tokens: 2000,
    output_config: { effort: "low", format: zodOutputFormat(Trip) },
    messages: [{ role: "user", content: `Extract the trip request: ${text}` }],
  });
  if (response.parsed_output === null) throw new Error(`no parsed output (stop_reason ${response.stop_reason})`);
  return response.parsed_output;
}
```

- `parsed_output` is typed from the Zod schema, so `trip.nights` is a `number`.
- It can be `null`, for example after a refusal or when the output was cut off at `max_tokens`. Guard it, and log the stop reason.
- This replaces the old prefill trick (starting the assistant turn with `{`). A prefill returns a 400 on current models.
- The schema guarantees shape, not truth. `nights: 3` can still be wrong. Your eval checks correctness.

## Prompt caching

Caching is a prefix match over tools, then system, then messages. Any byte change invalidates everything after it. Two ways to opt in:

```typescript
// Block-level breakpoint: cache everything up to and including the policy text
const r = await client.messages.create({
  model: "claude-sonnet-5-5",
  max_tokens: 4000,
  output_config: { effort: "low" },
  system: [
    { type: "text", text: "You answer questions about the policy below." },
    { type: "text", text: doc, cache_control: { type: "ephemeral" } },
  ],
  messages: [{ role: "user", content: q }],
});

// Automatic caching: top-level cache_control caches the last cacheable block
const auto = await client.messages.create({
  model: "claude-sonnet-5-5",
  max_tokens: 4000,
  cache_control: { type: "ephemeral" },
  system: doc,
  messages: [{ role: "user", content: q }],
});
```

**Prove it worked.** Look at `usage.cache_creation_input_tokens` on the first call and `usage.cache_read_input_tokens` on later ones. The minimum cacheable prefix is 512 tokens on current models (4,096 on Haiku 4.5), so a short system prompt silently doesn't cache. On Sonnet 5.5, cache reads cost $0.10 per million tokens against $2 for uncached input. Cache writes cost about 1.25x input for the default 5-minute lifetime.

TypeScript-specific invalidators to look for in review:

- `new Date().toISOString()` or a request id interpolated into the system prompt.
- Tools built from `Object.keys(...)` or a `Map` whose order changes between deploys or requests.
- `JSON.stringify` of an object assembled in different key orders on different code paths.
- Changing the top-level `effort` between requests, which also invalidates the cache.

> **Key takeaways**
> - Append `response.content` unmodified, answer every `tool_use` with one `tool_result`, validate tool input, cap turns.
> - Don't force tools on Opus 5.5, Sonnet 5.5 or Fable 5.1: use `auto`, `strict: true` and a check.
> - The tool runner (beta) runs the loop and validates Zod inputs, but doesn't resume `pause_turn` or apply stop-reason rules.
> - `messages.parse` with `zodOutputFormat` gives typed JSON. Guard against `null` `parsed_output`.
> - Cache a stable prefix, prove it with `cache_read_input_tokens`, and hunt for timestamps and unstable ordering in the prefix.
