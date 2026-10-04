---
title: "Streaming and Long Outputs"
type: reading
minutes: 14
---

> **By the end of this lesson you will be able to:**
> - Explain why streaming matters for both user experience and reliability
> - Stream responses with the Python SDK's `messages.stream` helper
> - Get the complete final message, including `stop_reason` and `usage`, after streaming
> - Pass a stream through to a web front end

## Two reasons to stream

**1. Perceived speed.** A long answer might take 20 seconds to generate. Without streaming, the user stares at a spinner for 20 seconds. With streaming, words start appearing within a second or two. The total time is the same; the experience is completely different. For anything a human watches, stream.

**2. Long outputs and timeouts.** Large `max_tokens` values (tens of thousands of tokens) can take minutes to complete. A single non-streaming HTTP request that long risks timing out somewhere along the way. Streaming keeps data flowing over the connection. That's why the SDK guidance is to use streaming for large outputs, and it's why the Python SDK requires streaming for very large `max_tokens` values.

Sensible defaults: about **16,000** `max_tokens` for non-streaming calls, and about **64,000** when streaming.

## The `messages.stream` helper

```python
with client.messages.stream(
    model="claude-opus-5-5",
    max_tokens=64000,
    system="Summarize meeting transcripts for Harbor Bank's operations team.",
    messages=[{"role": "user", "content": transcript}],
) as stream:
    for text in stream.text_stream:          # text pieces as they're generated
        print(text, end="", flush=True)
    message = stream.get_final_message()     # the complete Message, same as create() returns

print()
print(message.stop_reason, message.usage.output_tokens)
```

- `stream.text_stream` yields **only text pieces**. Thinking blocks are skipped automatically, which is usually what you want to show a user.
- `stream.get_final_message()` gives you the fully assembled `Message`: all content blocks, `stop_reason`, `usage`. **Always check `stop_reason` here**, exactly as you would after `create()`. A stream that ended with `max_tokens` is truncated.
- The `with` block makes sure the connection is closed even if your code raises an exception mid-stream.

## Lower-level events

If you need more than text (for example, showing a "thinking…" indicator, or reacting to tool use in Module 7), iterate over the stream's events instead:

```python
with client.messages.stream(...) as stream:
    for event in stream:
        if event.type == "content_block_start" and event.content_block.type == "thinking":
            show_thinking_indicator()
        elif event.type == "content_block_delta" and event.delta.type == "text_delta":
            render(event.delta.text)
```

The main event types are `message_start`, `content_block_start`, `content_block_delta` (with `text_delta` or `thinking_delta`), `content_block_stop`, and `message_stop`. There's also a raw form, `client.messages.create(..., stream=True)`, which yields events without assembling the final message for you. Prefer the helper unless you have a specific reason not to.

## Streaming to a web app

In a web product, your server talks to Claude and forwards the text to the browser, usually as **server-sent events (SSE)**:

```
browser ──request──► your server ──stream──► Claude API
browser ◄──SSE text chunks── your server ◄──text_stream──┘
```

Three practical points:

- **Keep the API key on the server.** Never call the Claude API directly from browser code; anyone could read the key.
- **Handle cancellation.** If the user closes the tab or presses "stop," stop reading the stream on the server so you don't pay for output nobody will read.
- **Handle errors mid-stream.** A network error can happen after some text was already shown. Show a clear "the response was interrupted" message, and log the request ID.

## Measuring what users feel

Two latency numbers matter for streamed responses:

- **Time to first token (TTFT):** how long until the first words appear. This is what users perceive as "speed."
- **Total generation time:** how long until the response is complete.

Lower effort usually reduces both, because there's less thinking before the answer begins. Measure them on real requests before and after any change.

> **Key takeaways**
> - Stream anything a human watches, and anything with large `max_tokens` (about 64,000 when streaming).
> - Use `messages.stream(...)`: iterate `text_stream` for text, then `get_final_message()` for stop_reason and usage.
> - Check `stop_reason` after streaming, just as after `create()`.
> - Stream through your server (never expose the key), handle cancellation and mid-stream errors, and track time to first token.
