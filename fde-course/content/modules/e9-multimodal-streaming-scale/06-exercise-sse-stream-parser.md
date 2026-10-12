---
title: "Exercise: An SSE Parser with Cancellation and TTFT"
type: exercise
minutes: 45
hints:
  - "`iter_sse`: keep one string buffer. After appending each chunk, replace `\\r\\n` with `\\n` on the whole buffer (a chunk can end between `\\r` and `\\n`), then pull out complete events with `split(\"\\n\\n\", 1)` while a blank line is present."
  - "`iter_sse`: it must be a generator. Yield inside the loop over chunks, so an event comes out as soon as the chunk that completes it arrives. That's what makes cancellation cheap."
  - "`consume`: keep blocks in a dict keyed by the event's `index`, and a second dict of raw JSON strings for tool blocks. Parse the JSON at `content_block_stop`; an empty string means `{}`, and a `ValueError` means `None`."
  - "`consume`: `usage.output_tokens` in `message_delta` is cumulative, so overwrite, don't add. Decide the final status after the loop: an error or a cancel already set it; no `message_stop` means the stream was cut off."
  - "`consume`: wrap the loop in `try/finally` and call `chunks.close()` in the `finally` when it has a `close` method. Then breaking out for a cancel or an error always closes the source."
---

Leo here. Tallowmere's order-desk assistant streams its answers into the desk's web app through a small proxy their team wrote. Three bugs reached Imani this month: answers that "freeze" for three seconds before any text appears, a tool call that ran with half its arguments, and an answer about bypassing a credit check that stayed on screen after Claude refused it. Their proxy parses the raw event stream by hand. Write the parser they should have written.

You get recorded streams from the proxy's logs. Each is a list of `(t_ms, chunk)` pairs, where `t_ms` is milliseconds since the request was sent. Chunks are raw network reads: an event can be split across chunks, one chunk can hold two events, some lines end in `\r\n`, and there's a `: keep-alive` comment line.

## Given

`STREAMS` (`answer`, `tool`, `overloaded`, `refusal`, `truncated`, `cited`, `dropped`, `long`) and `stream_source(name)`, a generator over one stream that records how many chunks you read and whether you closed it.

## Your task

**1. `iter_sse(chunks)`**: a generator that yields `(t_ms, event_name, data)` for each complete event, where `t_ms` is the time of the chunk that completed it and `data` is the parsed JSON.

- Events end at a blank line. Normalise `\r\n` to `\n` first.
- Skip lines starting with `:`. Take the name from the `event:` line. Join several `data:` lines with `\n` before parsing. Skip an event with no data.
- Yield each event as soon as it completes. Don't read the whole stream first.

**2. `consume(chunks, on_text=None, should_cancel=None)`** returns:

```python
{"status": ..., "text": ..., "blocks": [...], "stop_reason": ..., "stop_details": ...,
 "usage": {"input_tokens": ..., "output_tokens": ...}, "ttft_ms": ..., "error": ...}
```

| Event | What to do |
|---|---|
| `message_start` | `usage` from `message.usage` |
| `content_block_start` | Create the block at `index`: text `{"type", "text": "", "citations": []}`, thinking `{"type", "thinking": "", "signature": ""}`, tool use `{"type", "id", "name", "input": None}` |
| `text_delta` | Skip empty text. Otherwise append to the block and to `text`, set `ttft_ms` on the first one, call `on_text(delta_text)`, then call `should_cancel(text)`: if true, status `"cancelled"` and stop reading |
| `thinking_delta`, `signature_delta` | Append the thinking text; store the signature |
| `input_json_delta` | Append `partial_json` to that block's raw string |
| `citations_delta` | Append `citation` to the block's `citations` |
| `content_block_stop` | For a tool block, parse the raw string: `""` gives `{}`, invalid JSON gives `None` |
| `message_delta` | Set `stop_reason` and `stop_details`; **replace** `output_tokens` (it's cumulative) |
| `message_stop` | Remember the stream finished |
| `error` | Status `"error"`, `error` = the event's `error` object, stop reading. Keep the partial `text` |
| `ping`, anything unknown | Ignore |

Then:

- `blocks` is the list of blocks in index order.
- If no status was set: a stream with no `message_stop` gets status `"error"` and `error={"type": "incomplete_stream", "message": ...}`. Otherwise map `stop_reason`: `end_turn` or `stop_sequence` to `"complete"`, and `tool_use`, `refusal` and `max_tokens` to themselves.
- On `"refusal"`, set `text` to `""` and drop the text blocks.
- Always call `chunks.close()` (when it exists) before returning, including after a cancel or an error.

## What each recorded stream teaches

- **answer**: the thinking block streams one empty delta and a signature, so the first visible word arrives 2.95 s after send. That's the "freeze": TTFT includes thinking. The fix is in the UI (show that work is happening) and in `effort`, not in the parser.
- **tool**: the input arrives as `""`, `{"sk`, `u": "TS-CB-3C25", ` and so on. Only the full string parses. There's also an event type the parser has never seen.
- **truncated**: `max_tokens` arrived mid-tool. The input must stay `None`, so nobody runs `create_return` with half a line list.
- **overloaded** and **dropped**: one ends with an `error` event, the other just stops. Both are failures, and both keep the partial text for a "continue" request.
- **refusal**: text started streaming, then the message ended with `stop_reason: "refusal"`. The partial text goes.
- **long**: the user clicks Stop. You stop reading and close the source, rather than draining 130 chunks you'll throw away.

## Example

```python
>>> r = consume(stream_source("answer"))
>>> r["status"], r["ttft_ms"], r["usage"]
('complete', 2950, {'input_tokens': 2104, 'output_tokens': 182})
>>> consume(stream_source("tool"))["blocks"][-1]["input"]
{'sku': 'TS-CB-3C25', 'qty': 150}
```

Press **Run** to see every stream's status and TTFT, then **Submit**.
