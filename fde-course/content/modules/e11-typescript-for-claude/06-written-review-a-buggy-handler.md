---
title: "Write It: Review Fernhollow's Assistant Route"
type: written
minutes: 35
sections:
  - key: blockers
    label: Blocking findings
    prompt: "The issues that must be fixed before this ships, most severe first. For each: the line or construct, what goes wrong in production, and the fix."
    words: [150, 400]
  - key: other
    label: Other findings
    prompt: "Issues that won't cause an outage on day one but cost money, quality or debuggability. Same format, shorter."
    words: [80, 250]
  - key: fixed
    label: The fixed core
    prompt: "Rewrite the core of the handler (the client setup and the API call, plus how the result is returned) in TypeScript. It doesn't need to compile, but it should use real SDK calls and fields."
    words: [80, 300]
  - key: tests
    label: How you'd test it
    prompt: "The tests you'd add (unit with a fake client, and one manual check against the real API) to prove the fixes hold."
    words: [50, 160]
  - key: note
    label: Note to Ada
    prompt: "Three or four sentences to Ada, the staff engineer who asked for the review: what to fix first and why, in plain language."
    words: [40, 110]
rubric:
  - name: Finds the request-breaking bugs
    points: 25
    lookFor: "Identifies that this request 400s on claude-opus-5-5 for three separate reasons: the forced tool_choice, the assistant prefill as the last message, and temperature. Gives the right replacement for each: auto plus strict tools plus a prompt instruction and a check (or no tool at all here), structured outputs via output_config.format with messages.parse, and removing temperature."
  - name: Finds the security and data bugs
    points: 25
    lookFor: "Flags the NEXT_PUBLIC_ key (Next.js inlines NEXT_PUBLIC_ variables into any browser bundle that references them, so a secret must never carry that prefix), the client-supplied system prompt and unvalidated history (a user can rewrite the assistant's instructions), the SQL string built from model-supplied tool input (injection; use a parameterised query and validate the ref format), and logging the full request body with customer data."
  - name: Finds the reliability and cost bugs
    points: 20
    lookFor: "Notes the hand-rolled retry that retries every error including 400s, with no backoff, on top of the SDK's own retries; content[0] cast to any (breaks when the response starts with a thinking block); no streaming with a large max_tokens (timeouts, and the user waits for the whole answer); no stop_reason check; the timestamp at the start of the system prompt that defeats caching; effort not set."
  - name: The fix uses real SDK features correctly
    points: 20
    lookFor: "The rewritten core uses new Anthropic() with a server-side env key, a fixed server-side system prompt with cache_control, validated messages ending with a user turn, client.messages.parse with zodOutputFormat (or output_config.format) or a streamed reply, explicit output_config.effort, narrowing by block type or parsed_output with a null check, a stop_reason check, typed error classes. No invented SDK methods."
  - name: Prioritised, testable and clear
    points: 10
    lookFor: "Orders findings by severity, proposes concrete tests (fake client asserting no tool_choice, no prefill and no temperature in params; a test that an injected ref is rejected; one real call checking cache_read_input_tokens on the second request), and writes Ada a short plain-language note that leads with the blockers."
passScore: 70
graderNotes: |
  The handler is in the lesson body. Planted issues: (1) NEXT_PUBLIC_ANTHROPIC_KEY: the prefix marks the variable for inlining into browser bundles, so the key leaks as soon as any client code references it; (2) system prompt taken from the request body; (3) messages from the client unvalidated; (4) assistant prefill "{" as the last message, a 400 on claude-opus-5-5; (5) tool_choice {type: "tool"}, a 400 on claude-opus-5-5; (6) temperature: 0, a 400 on claude-opus-5-5; (7) (response.content[0] as any).text; (8) SQL built by string concatenation from the model's tool input; (9) retry loop on every error, no backoff, on top of SDK retries; (10) console.log of the full body (customer names and emails); (11) Date in the system prompt defeats caching; (12) no effort, no stop_reason check, non-streaming call with max_tokens 64000.
  Cap 'Finds the request-breaking bugs' at 10 if fewer than two of the three 400 causes are named. Cap 'Finds the security and data bugs' at 10 if the exposed key or the SQL injection is missed. Mark down any fix that invents SDK methods or parameters, recommends a prefill, or keeps forced tool_choice. Do not require all twelve; a strong review finds at least nine and ranks them sensibly. Don't penalise minor TypeScript syntax slips in the rewrite; it doesn't need to compile.
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Blocking: the code is a bit messy and should use async/await consistently. The SQL could be cleaner. Other: add more comments and maybe use a newer model. Fixed: same code with better variable names and a try/catch around everything. Tests: add unit tests. Note: Ada, looks mostly good, just tidy it up."
  - label: strong
    expect: [75, 100]
    answer: "Blocking, most severe first. (1) The key is read from NEXT_PUBLIC_ANTHROPIC_KEY; Next.js inlines NEXT_PUBLIC_ variables into any browser bundle that references them, so one client import leaks the key. Rotate it now and use a server-only ANTHROPIC_API_KEY read by new Anthropic(). (2) The SQL query concatenates the model's tool input: a prompt-injected ref like x' OR '1'='1 dumps every booking. Validate /^FH-\\d{4}$/ and use a parameterised query. (3) system comes from the request body and messages are unvalidated, so a user can rewrite the assistant's rules. Keep the system prompt on the server, accept only user/assistant string turns, cap size, require the last turn to be the user's. (4) Three 400s on claude-opus-5-5: tool_choice {type: 'tool'} (forced tool use is rejected), the trailing assistant '{' prefill, and temperature: 0. Drop tool_choice (use auto, strict tools and an instruction, then check a tool_use came back), replace the prefill with output_config.format via messages.parse and zodOutputFormat, remove temperature. (5) Logging JSON.stringify(body) writes customer names and emails to logs; log ids, token counts and the request id instead. Other: the retry loop retries 400s with no backoff on top of the SDK's two retries, so remove it or retry only 429/5xx honouring retry-after with SDK retries off; (content[0] as any).text breaks when the first block is thinking, narrow by type; max_tokens 64000 without streaming risks HTTP timeouts, so stream or lower it; no stop_reason check, so refusals and truncation look like answers; the Date at the start of system changes every request and defeats caching, move it to the user turn; effort isn't set, so Opus 5.5 runs at medium by default - set it explicitly. Fixed core: const client = new Anthropic(); const r = await client.messages.parse({ model: 'claude-opus-5-5', max_tokens: 8000, output_config: { effort: 'low', format: zodOutputFormat(Answer) }, system: [{ type: 'text', text: SYSTEM, cache_control: { type: 'ephemeral' } }], tools, messages: validated }); if (r.stop_reason === 'refusal') ...; if (!r.parsed_output) ...; catch with instanceof Anthropic.RateLimitError / BadRequestError. Tests: a fake client asserting params contain no tool_choice, temperature or trailing assistant turn; a tool test rejecting x' OR '1'='1; one real call run twice checking cache_read_input_tokens > 0 on the second. Note: Ada, rotate the key today and fix the SQL query before anything else: those are a data breach waiting to happen. Then three settings make every request fail on Opus 5.5; the fixes are small. The rest is cost and reliability work for this sprint."
---

Ada Wexley, a staff engineer at Fernhollow Travel, asked for a review of the assistant route before it goes live. Ada and Fernhollow are fictional. The code below is TypeScript for a Next.js App Router route handler. It runs locally, not in this browser course, and it's deliberately bad. Find what's wrong, rank it, fix the core, and say how you'd test it.

```typescript
// app/api/assistant/route.ts
import Anthropic from "@anthropic-ai/sdk";
import { db } from "@/lib/db";

const client = new Anthropic({ apiKey: process.env.NEXT_PUBLIC_ANTHROPIC_KEY });

const tools: Anthropic.Tool[] = [
  {
    name: "get_booking",
    description: "Look up a booking by reference.",
    input_schema: { type: "object", properties: { ref: { type: "string" } }, required: ["ref"] },
  },
];

export async function POST(request: Request) {
  const body = await request.json();
  console.log("assistant request", JSON.stringify(body)); // includes customer names and emails

  const messages = [...body.messages, { role: "assistant", content: "{" }];

  let response;
  for (let attempt = 0; attempt < 5; attempt++) {
    try {
      response = await client.messages.create({
        model: "claude-opus-5-5",
        max_tokens: 64000,
        temperature: 0,
        system: `Today is ${new Date().toISOString()}. ${body.system}`,
        tools,
        tool_choice: { type: "tool", name: "get_booking" },
        messages,
      } as any);
      break;
    } catch (e) {
      continue; // try again
    }
  }

  const block = (response!.content[0] as any);
  if (block.type === "tool_use") {
    const rows = await db.query(`SELECT * FROM bookings WHERE ref = '${block.input.ref}'`);
    return Response.json({ booking: rows[0] });
  }
  return Response.json(JSON.parse("{" + block.text));
}
```

## How you're graded

The rubric rewards finding the request-breaking, security and reliability problems, ranking them, and fixing the core with real SDK features from lessons 01 to 03. You don't need every issue. A strong review finds most of them and puts the dangerous ones first. Your rewrite doesn't need to compile, but it must not invent SDK methods.
