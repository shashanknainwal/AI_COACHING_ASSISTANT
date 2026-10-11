---
title: "Exercise: Debug a Broken Eval Harness"
type: exercise
minutes: 40
hints:
  - "Press Run first and read the output. 26 API attempts for five cases is a lot, the cache-read column is all zeros, and C2 shows up as an error even though nothing is wrong with the question."
  - "Cache reads need a byte-identical prefix: tools, then system. Anything in the system prompt that changes per request breaks it for every call. Keep the `cache_control` breakpoint, and drop the timestamp from the system prompt."
  - "Look at what `run_case` appends after a `tool_use` turn when there are two tool calls. The API requires every `tool_result` for a turn in the very next user message."
  - "Two functions edit history: one filters what the model returned, one rewrites old tool results. On models with preserved thinking, an edited history fails with a 400 by default, and it restarts the prompt cache at the edit."
  - "Count the attempts for C4: the loop's 5 tries times the SDK's own 3 attempts each. Then ask whether a 400 can ever succeed on a retry. The SDK's built-in retries are enough here."
---

Teodora Kessler at Gannet Home Energy (fictional) inherited an eval harness from a contractor. "It runs, it prints results, and I don't trust a single number from it. Our API bill for eval runs doubled last month, one case 'fails' every time even though the agent handles it fine in production, and a colleague says our history handling won't survive the move to Opus 5.5. Find what's wrong and fix it. Every fix needs to be proven by a test."

The harness is in the editor. `client` (simulated, Claude Opus 5.5), `MODEL`, `MAX_TOKENS`, `MAX_STEPS`, `SYSTEM_PROMPT`, `TOOLS`, `run_tool()`, `CASES` and `grade()` are loaded for you. In interviews, the same skills show up as "here's a trace, what's wrong?" (in the style of the trace-reading questions in module E2; not a real interview question).

## Your task

The harness has **four planted bugs**. Each test checks one of them, and a fifth checks the whole suite. Keep the functions `run_case(client, case)` and `run_suite(client, cases)` with the same return shapes. Change anything else.

| Test | What it checks |
|---|---|
| Bug 1 | Every request sends the same system prompt, exactly `SYSTEM_PROMPT`, with a `cache_control` breakpoint. Every call after the first reads the cached prefix (`usage.cache_read_input_tokens > 0`). |
| Bug 2 | When the model calls two tools in one turn, both `tool_result` blocks go back in one user message, and case C2 completes. |
| Bug 3 | The history is append-only. Each request starts with the previous request's messages, byte for byte, and every assistant turn goes back exactly as returned, thinking blocks included. |
| Bug 4 | An overloaded API gets at most 3 attempts per case, which is the SDK's own retries. A 400 is attempted once. Both end as an error row. |
| Suite | C1 to C3 pass, C4 and C5 are errors, and five cases take at most 11 attempts. |

If the model really needs today's date, put the date (not a timestamp) at the start of the first user message, never in the system prompt. For this exercise, leave it out.

## Example

```text
broken:  26 API attempts in total, cache-read tokens all 0, C2 = error
fixed:   11 API attempts in total, cache reads on every call after the first, C2 = pass
```

## Why each bug matters beyond this harness

- **The timestamp** makes every request a cache miss. On Opus 5.5 a cache read costs 0.05x the input price, so a 1,500-token prefix read from cache costs a twentieth of sending it fresh. A per-request timestamp quietly throws that away on every call. It also changes the conversation the model's thinking is bound to, so it is a preserved-thinking break as well.
- **Split tool results** are a 400. The harness caught the exception and logged an error, so a harness bug looked like an agent failure. That's why errors are reported separately (module E4) and why you read the error, not just the count.
- **Edited history** includes dropped thinking blocks and trimmed old tool results. On Opus 5.5, thinking-block signatures bind to every earlier message, so editing or trimming earlier turns returns a 400 by default. The fix is append-only history. To save tokens, use compaction or context editing (module C7) instead of rewriting turns yourself.
- **A retry storm** multiplies load exactly when the API is overloaded, and it retries errors that can never succeed. The SDK already retries 429, 5xx and connection errors with exponential backoff (`max_retries` defaults to 2). Wrap it in your own loop only if you set `max_retries=0` and retry only the retryable errors.

Press **Run** to see the broken numbers, fix the bugs one at a time, and **Submit** after each fix to watch the checks turn green.
