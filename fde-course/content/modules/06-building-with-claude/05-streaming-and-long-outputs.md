---
title: "Streaming and Long Outputs"
type: reading
minutes: 5
---

> **By the end of this lesson you will be able to:**
> - Explain why streaming matters for experience and reliability
> - Stream with the Python SDK's `messages.stream` helper
> - Get `stop_reason` and `usage` after streaming
> - Pass a stream through to a web front end

Priya's team leads want stand-up summaries to appear in their dashboard as they're written, not after a 20-second spinner. Agents on a live call won't wait either.

## Two reasons to stream

1. **Perceived speed.** Total time is the same, but words appear within a second or two. Stream anything a human watches.
2. **Long outputs.** A non-streaming request with a large `max_tokens` can run for minutes and time out; the Python SDK refuses non-streaming requests it estimates will take too long. Defaults: about **16,000** `max_tokens` without streaming, about **64,000** with it.

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

- `text_stream` yields only text; thinking is skipped.
- `get_final_message()` returns the assembled `Message`. **Check `stop_reason` here**: a stream that ended on `max_tokens` is truncated.
- The `with` block closes the connection even if your code raises.

For more than text (a "thinking…" indicator, tool use), iterate the events: `message_start`, `content_block_start`, `content_block_delta` (`text_delta` or `thinking_delta`), `content_block_stop`, `message_stop`. `messages.create(..., stream=True)` gives raw events without assembling the message; prefer the helper.

## Streaming to a web app

```
browser ──request──► your server ──stream──► Claude API
browser ◄──SSE text chunks── your server ◄──text_stream──┘
```

- **Keep the API key on the server**, never in browser code.
- **Handle cancellation:** stop reading when the user closes the tab, so you don't pay for unread output.
- **Handle mid-stream errors:** show "the response was interrupted" and log the request ID.

Track **time to first token** (what users feel as speed) and total generation time. Lower effort usually improves both.

> **Key takeaways**
> - Stream anything a human watches and any large `max_tokens`.
> - Iterate `text_stream`, then `get_final_message()` and check `stop_reason`.
> - Stream through your server; handle cancellation and errors; track time to first token.
