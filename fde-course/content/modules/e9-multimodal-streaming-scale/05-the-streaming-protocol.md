---
title: "The Streaming Protocol, Event by Event"
type: reading
minutes: 16
---

> **By the end of this lesson** you'll be able to read a raw Messages API event stream, rebuild the final message from it, handle text, thinking, tool-input and citation deltas, react correctly to a mid-stream error or refusal, cancel cleanly, and measure time to first token the way users experience it.

## Why learn the wire format

The SDK's `messages.stream()` helper accumulates events for you, and you should use it in production. You still need the wire format, for three reasons:

- **You'll build proxies.** A gateway, a backend-for-frontend or a WebSocket bridge passes events through, and has to understand them to meter usage, cut off a refusal or forward a cancel.
- **Interviews use it.** Streaming parsers are a common practical coding prompt for applied AI roles, and Perplexity's coding round is reported to include streaming (Reported, see TRACKS_PLAN and E6).
- **Bugs live here.** "The UI shows half an answer and then nothing" is almost always an unhandled event type.

## The event flow

Set `"stream": true` (or use the SDK helper) and the response arrives as server-sent events (SSE). Each event is an `event:` line and a `data:` line of JSON, followed by a blank line:

```text
event: content_block_delta
data: {"type":"content_block_delta","index":1,"delta":{"type":"text_delta","text":"Your order"}}

```

Every stream follows the same shape (Official, streaming docs):

1. `message_start`: a `Message` object with empty `content`, plus initial `usage`.
2. For each content block: `content_block_start`, one or more `content_block_delta`, then `content_block_stop`. The `index` is the block's position in the final `content` array.
3. One or more `message_delta` events with top-level changes: `stop_reason`, `stop_details`, and `usage`. The token counts in `message_delta` are **cumulative**, so take the last one, don't sum them.
4. `message_stop`.

Two more event types can appear anywhere: `ping` (ignore it) and `error`. The docs also say new event types may be added, and your code should **ignore unknown types** rather than crash.

## Delta types

| Delta `type` | Belongs to | Field | What to do |
|---|---|---|---|
| `text_delta` | `text` block | `text` | Append and render |
| `thinking_delta` | `thinking` block | `thinking` | Append; render only if you show reasoning |
| `signature_delta` | `thinking` block | `signature` | Store it. It arrives just before `content_block_stop` and verifies the block |
| `input_json_delta` | `tool_use` block | `partial_json` | Append the string. Parse it once at `content_block_stop` |
| `citations_delta` | `text` block | `citation` | Append to that block's `citations` list |

**Thinking is usually invisible.** On Claude Opus 5.5, Sonnet 5.5 and other current models the default thinking display is omitted. The thinking block still opens, receives one `thinking_delta` with an **empty** string, then a `signature_delta`, and closes. That's why a stream can run for seconds before any visible text: the model is thinking, and the user sees nothing unless your UI says so. Request `thinking: {"type": "adaptive", "display": "summarized"}` if you want a readable summary to stream.

**Tool input arrives as fragments of a JSON string.** The first fragment is often an empty string, and fragments split anywhere, including inside a key. The final `tool_use.input` is an object, so accumulate the string and parse it at the block's stop (or use a partial-JSON parser for live previews). With `eager_input_streaming: true` on a tool, fragments arrive sooner, without server-side buffering, and the server no longer validates the input. Validate it yourself before running anything.

**A truncated tool input is still a string.** If the message ends with `stop_reason: "max_tokens"` during a tool block, the JSON is incomplete. Don't run that tool.

## Errors and refusals mid-stream

An HTTP 200 doesn't mean the stream will finish well. Three endings need code:

| Ending | What arrives | What to do |
|---|---|---|
| **Error event** | `event: error` with `{"type": "error", "error": {"type": "overloaded_error", "message": "Overloaded"}}` (the streaming equivalent of a 529) | Stop. Keep the partial text if you want to resume, mark the response incomplete, retry or offer a retry |
| **Refusal** | `message_delta` with `stop_reason: "refusal"` and `stop_details` (`category`, `explanation`) | The docs say to treat any partial output as incomplete and **discard it**. Show a refusal message instead |
| **max_tokens** | `message_delta` with `stop_reason: "max_tokens"` | Show what you have, labelled as cut off. Never run a truncated tool call |

A refusal can arrive before any output or after partial output. A mid-stream refusal bills the input and the output already streamed (Official, refusals page). Refusal handling (including server-side `fallbacks`) is covered in depth in the refusals docs; for this lesson, the rule is: don't leave a half-answer on screen.

**Resuming after an error.** For Claude 4.6 and later, the docs describe saving the partial response, then sending a new request with a **user** message that contains the partial text and asks the model to continue. (Older models used an assistant prefill instead, which current models reject.) Tool use and thinking blocks can't be partially recovered; resume from the most recent text block.

## Cancellation

A user who clicks Stop wants output to stop now. In the Python SDK, leaving the `with client.messages.stream(...)` block closes the connection; with the raw iterator, stop iterating and close the response. In your own parser, that means: check a cancel flag after each delta, and when it's set, **stop pulling events** and close the source. Don't drain the rest of the stream "to be tidy". That keeps generating tokens you'll throw away.

Record what you had at the moment of cancellation and mark it cancelled. Billing for a cancelled stream isn't something this course can state precisely; assume you pay for what was generated before the connection closed, and check the current docs if a customer's budget depends on it.

## Measuring time to first token

TTFT is the user's first impression, so measure it the way the user sees it:

- Start the clock when you **send** the request, not when the first byte arrives.
- Stop it at the first `text_delta` with **non-empty** text. Not at `message_start`, not at a `ping`, and not at an empty thinking delta.
- On thinking models, TTFT includes thinking time. Thinking tokens are billed as output and they count toward `max_tokens`. If TTFT is too long, effort is a lever (E5 covers the latency budget).

Also record time to last token and output tokens per second (from the final cumulative `usage`). Report p50 and p95 per route.

## Gotchas when parsing raw SSE

- **Chunks don't align with events.** A network read can end mid-line or hold three events. Buffer bytes and split on blank lines.
- **Lines may end in `\r\n`.** Strip carriage returns.
- **A line starting with `:` is a comment.** Ignore it.
- **An event can have several `data:` lines.** The SSE format joins them with newlines before you parse the JSON.

## How this comes up in interviews

A practice prompt in the style of applied AI coding rounds:

- "Here's a recorded event stream from an LLM API. Write a function that renders text as it arrives, returns the final message, and reports time to first token. Then: what changes if the stream contains a tool call? What if the connection drops halfway?"

Interviewers watch for buffering across chunk boundaries, unknown events ignored, cumulative usage read correctly, and a clear answer about partial output on errors and refusals.

> **Key takeaways**
>
> - A stream is `message_start`, then start/delta/stop per block, then `message_delta` (stop reason, cumulative usage), then `message_stop`. `ping` and unknown events are ignored; `error` can arrive mid-stream.
> - Text, thinking, signature, tool-input and citation deltas each update a different field. Tool input is a JSON string until the block stops.
> - Default thinking display is omitted on current models: an empty thinking delta, a signature, and seconds of silence your UI should explain.
> - On a refusal, discard partial output. On an error, keep it for a user-message continuation. Never run a truncated tool call.
> - Cancel by stopping consumption and closing the source. Measure TTFT from send to the first non-empty text delta.
