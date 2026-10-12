---
title: "TypeScript With Claude: Setup, Types and Your First Call"
type: reading
minutes: 15
---

> **By the end of this lesson** you'll be able to set up a TypeScript project with `@anthropic-ai/sdk`, make a typed Messages API call, narrow content blocks correctly, handle errors with the SDK's typed classes, and explain how TypeScript work in this module is practised and graded.

## Read this first: the TypeScript in this module runs on your machine

The course's browser editor runs Python only. **TypeScript can't run in this browser course.** So this module teaches TypeScript in four ways:

1. **Readings with idiomatic code.** Every snippet in this module was type-checked against `@anthropic-ai/sdk` 0.128 and `@modelcontextprotocol/sdk` 1.32 with `tsc --strict` before it was published.
2. **Code-reading quizzes.** What does this print? Where's the bug?
3. **Written lessons graded by a rubric.** You'll review a buggy handler and port a Python tool loop to TypeScript.
4. **A local lab.** You run the TypeScript examples in `capstone-kit/typescript/` on your own machine with Node and paste your results.

Why bother? Many customer teams build their product in TypeScript, often a Next.js front end with route handlers on the server. The Anthropic FDE posting reviewed for this course asks for Python plus one other language (**Official**, from the posting; postings change, so check the current one). An FDE who can review the customer's TypeScript route on the first call is more useful than one who asks for a Python version.

Fernhollow Travel is this module's fictional customer: a booking site built on Next.js. Their staff engineer, Ada Wexley, is fictional too.

## Setup

You need Node 20 or newer.

```bash
mkdir claude-ts && cd claude-ts
npm init -y
npm install @anthropic-ai/sdk
npm install -D typescript tsx @types/node
npx tsc --init
```

Set `"type": "module"` in `package.json` and `"strict": true` in `tsconfig.json`. Run files with `npx tsx file.ts`, and check types with `npx tsc --noEmit`.

Two habits from the SDK docs:

- **Don't hardcode the key.** `new Anthropic()` reads `ANTHROPIC_API_KEY` from the environment (or `ANTHROPIC_AUTH_TOKEN`, or an `ant auth login` profile).
- **In ES modules, `__dirname` doesn't exist.** Using it throws a `ReferenceError` at runtime. Read cwd-relative paths directly, or derive the directory from `import.meta.url`.

## A first call, done properly

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic(); // reads ANTHROPIC_API_KEY from the environment

export async function ask(question: string): Promise<string> {
  try {
    const response = await client.messages.create({
      model: "claude-haiku-5-5",
      max_tokens: 2000, // covers thinking as well as the answer
      output_config: { effort: "low" },
      system: "You answer in one short paragraph.",
      messages: [{ role: "user", content: question }],
    });

    if (response.stop_reason === "refusal") return "[declined]";

    const text = response.content
      .filter((b): b is Anthropic.TextBlock => b.type === "text")
      .map((b) => b.text)
      .join("");

    console.log(response._request_id, response.usage.input_tokens, response.usage.output_tokens);
    return text;
  } catch (err) {
    if (err instanceof Anthropic.RateLimitError) {
      console.error("429: back off, honour retry-after");
    } else if (err instanceof Anthropic.BadRequestError) {
      console.error("400: fix the request, don't retry", err.message);
    } else if (err instanceof Anthropic.APIError) {
      console.error(`API error ${err.status}`);
    }
    throw err;
  }
}
```

What each piece is for:

- **`effort` is explicit.** Defaults differ by model: Haiku 5.5 and Opus 5.5 default to `medium`, Sonnet 5.5 to `high`. All three think by default. Thinking is billed as output, counts toward `max_tokens` and sits inside time to first token. A classification call at `low` thinks little.
- **`stop_reason` is checked before content.** A refusal arrives as a normal HTTP 200 with `stop_reason: "refusal"`.
- **Content is narrowed by type.** `response.content` is a discriminated union. A response can start with a `thinking` block (empty text under the default display) before the `text` block.
- **`_request_id`** is the id support asks for. Log it with the usage numbers.
- **Errors use typed classes, most specific first.** Every class extends `Anthropic.APIError`, which has a typed `status`. Never match on error message strings. The SDK already retries 429s and 5xx errors a couple of times with backoff, so don't stack your own retry loop on top without turning that off.

## The bug TypeScript catches for you

```typescript
const answer = response.content[0].text; // does not compile
```

This is a type error, and a good one. `content[0]` might be a `thinking` block or a `tool_use` block, which have no `text`. Python lets the equivalent line run and fails at runtime on the day the model starts its answer with thinking. In TypeScript, narrow with `block.type === "text"` (as above) or with `find` plus a type guard.

## Types to reuse, not redefine

Use the SDK's own types for every API structure:

| Type | For |
|---|---|
| `Anthropic.MessageParam` | One entry in `messages` |
| `Anthropic.Message` | A full response |
| `Anthropic.TextBlock`, `Anthropic.ToolUseBlock` | Narrowed content blocks |
| `Anthropic.Tool` | A custom tool definition (not server tools like web search) |
| `Anthropic.ToolResultBlockParam` | A `tool_result` you send back |

Redefining these as your own interfaces drifts from the SDK the first time the API adds a field. Don't mix beta and non-beta types either. A `client.beta.messages` response has beta block types.

## Model IDs

Use exact IDs from the docs: `claude-opus-5-5`, `claude-sonnet-5-5`, `claude-haiku-5-5`, `claude-fable-5-1`. On Amazon Bedrock the IDs carry an `anthropic.` prefix. Never construct an ID from a pattern.

> **Key takeaways**
> - TypeScript in this module runs locally with Node. The course teaches it through readings, code-reading quizzes, rubric-graded written lessons and a local lab.
> - Set `effort` explicitly, size `max_tokens` for thinking, and check `stop_reason` before reading content.
> - Narrow content blocks by `type`. `content[0].text` is a type error for a good reason.
> - Catch the SDK's typed errors from most to least specific, and remember the SDK already retries 429 and 5xx.
> - Reuse the SDK's types. Keep the key on the server, in the environment.
