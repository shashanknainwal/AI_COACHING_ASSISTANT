---
title: "Exercise: Stream a Meeting Summary"
type: exercise
minutes: 25
hints:
  - "`make_collector`: create `chunks = []`, define `def on_text(piece): chunks.append(piece)`, and `return on_text, chunks`."
  - "Use `with client.messages.stream(...) as stream:` and loop `for text in stream.text_stream: on_text(text)`."
  - "After the loop (still inside the `with`), `message = stream.get_final_message()`."
  - "Build the user message with `f\"<transcript>\\n{transcript}\\n</transcript>\"`."
  - "The result's text comes from the final message's text blocks, not from your chunks, so it's correct even if your callback does something else."
---

Harbor Bank's operations leads record their daily stand-ups and want a summary to appear in their dashboard as it's being written. You'll build the streaming summarizer.

## Your task

**1. `make_collector()`** returns a tuple `(on_text, chunks)`: a callback function, and the list it appends every text piece to. (This is how you'd test streaming code, or buffer text before sending it to a browser.)

**2. `stream_summary(client, transcript, on_text)`**:
- Calls `client.messages.stream(...)` with `model=MODEL`, `max_tokens` of **at least 32000**, `system=SYSTEM_PROMPT`, and one user message containing the transcript wrapped in `<transcript>` tags (on their own lines, like the tickets in the last exercise).
- Calls `on_text(piece)` for **every** piece from `stream.text_stream`.
- After streaming, gets the final message with `stream.get_final_message()` and returns:

```python
{"text": "...full summary...", "stop_reason": "end_turn", "output_tokens": 182, "truncated": False}
```

`text` joins the final message's text blocks; `truncated` is `True` when `stop_reason` is `"max_tokens"`.

Press **Run** to watch the summary stream in, piece by piece, then **Submit**.
