---
title: "AI-Allowed Drill: An SSE Stream Client"
type: drill
minutes: 50
timeLimit: 45
aiAllowed: true
levels:
  - "Parse the stream"
  - "Ids and retry"
  - "Reconnection and replay"
  - "Assemble streamed messages"
hints:
  - "Before you prompt anything, write down the state you need: a line buffer, a 'skip the next \\n' flag, the data lines, the event type, a pending id, the committed id, retry, connection state and message records. Then ask the assistant for code against that state, not for 'an SSE parser'."
  - "The bug the assistant is most likely to hand you: splitting on '\\n' only, or treating a chunk that ends in '\\r' as complete. Write the check for a CRLF split across two chunks before you accept any parser."
  - "Commit the pending id to last_event_id at every blank line. On disconnect, throw away the line buffer, the data, the event type and the pending id (set it back to the committed id)."
  - "Dedupe needs to know whether the event's own block contained an id line. Keep a flag that resets at each blank line."
  - "Assemble messages after an event passes dedupe, so a replayed delta never reaches the message text."
---

**This drill is AI-allowed.** Use the tutor or any AI assistant you like while the clock runs. If the tutor panel shows as off during the drill, open Claude in another window instead. The clock is shorter and the spec longer than the other drills, on purpose.

Marram Commerce's internal gateway streams model output to its web app as server-sent events (SSE). Petra Havel (fictional) reports the symptom every streaming integration has at least once: "When a user's train goes into a tunnel, the answer comes back with a sentence printed twice." The event names and JSON shapes in Level 4 are Marram's own invented format, not any vendor's real streaming format.

## How AI-allowed screens differ

Some companies now run coding rounds where an AI assistant is allowed or even expected (**Reported**: candidate accounts and some company announcements describe it; the practice is new and varies by company and by round). Anthropic's candidate guidance says not to use AI in live interviews unless you're told you may (**Official**, [candidate AI guidance](https://www.anthropic.com/candidate-ai-guidance)). So ask your recruiter which rule applies, and never assume.

When AI is allowed, the bar moves:

- **More scope in less time.** Typing is no longer the bottleneck, so interviewers can ask for more. That's why this drill gives you 45 minutes for four levels.
- **Your judgement is what's graded.** Interviewers watch how you split the problem, what you ask for, and whether you read and test what comes back. Pasting the whole spec and submitting the result is the weak pattern.
- **You own every line.** Expect "why does this line exist?" on code you didn't type. If you can't explain it, delete it or rewrite it.
- **Verification beats generation.** Writing a five-line check for a tricky edge case (a `\r\n` split across chunks, a replayed event after reconnecting) is worth more than generating another hundred lines.

A good rhythm: model the state yourself (2 minutes), ask for one level at a time with your state named, read the diff, write one adversarial check, submit. After the drill, write down one place where the assistant was wrong and how you caught it.

## The rules

- Implement a class called `StreamClient`. Every method takes `timestamp` (an integer number of **milliseconds**) as its first argument, and timestamps never decrease from one call to the next.
- Press **Submit** to run the checks for the levels you can see. Hidden checks split streams at awkward places.
- Events are dicts: `{"type": ..., "data": ..., "id": ...}`.

## Level 1: Parse the stream

The client starts connected. `feed(timestamp, chunk)` receives the next piece of the stream (a string) and returns the list of events completed by it, in order. A chunk can end anywhere, even in the middle of a field name.

- A line ends at `"\r\n"`, `"\n"` or `"\r"`. A `"\r"` at the end of one chunk followed by `"\n"` at the start of the next is a single line ending.
- If the very first character of the stream is `"﻿"` (a byte order mark), ignore it.
- A line starting with `":"` is a comment: ignore it.
- Otherwise split the line at its first `":"` into a field name and a value, and remove **one** leading space from the value if there is one. A line with no `":"` is a field name with an empty value.
- Field `event` sets the event type. Field `data` adds a data line. Ignore other fields until Level 2.
- A **blank line** completes an event: its data is the data lines joined with `"\n"`, its type is the event type or `"message"` if none was set, and its id is `None` (until Level 2). If there are no data lines, nothing is dispatched. Either way the data lines and the event type reset.

```python
c = StreamClient()
c.feed(1, "event: update\ndata: one\nda")   # []
c.feed(2, "ta: two\n\n")                   # [{"type": "update", "data": "one\ntwo", "id": None}]
```

## Level 2: Ids and retry

- Field `id` sets a **pending id**, unless its value contains the NUL character `"\0"` (then ignore the line). An empty value is a valid id: the empty string.
- At every blank line, the pending id becomes the **last event id**, even if nothing is dispatched. The pending id stays as it is, so events without an id line carry the last id.
- A dispatched event's `"id"` is the last event id at that moment (or `None` if there has never been one).
- Field `retry` sets the reconnection delay in milliseconds, immediately, if its value is one or more ASCII digits. Otherwise ignore it.
- `last_event_id(timestamp)`: the last event id, or `None`.
- `retry_ms(timestamp)`: the reconnection delay. It starts at `3000`.

## Level 3: Reconnection and replay

- `disconnect(timestamp)`: close the connection. Discard any partial line, the data lines, the event type, and the pending id (set it back to the last event id). Return the earliest time a reconnect is allowed: `timestamp` plus the delay. While disconnected, `feed` returns `[]` and changes nothing.
  - If the connection that just closed dispatched at least one event, the delay is the retry value.
  - If it dispatched none, the delay is the retry value times `2 ** k`, where `k` is the number of connections in a row (ending with this one) that dispatched nothing. The delay never exceeds `30000`.
- `connect(timestamp)`: reopen the connection. Return `True`, or `False` if already connected or `timestamp` is earlier than the allowed time.
- `headers(timestamp)`: `{"Last-Event-ID": <last event id>}` for the reconnect request, or `{}` if the last event id is `None` or empty.
- **Replays.** After a reconnect, servers resend events. If an event's own block contained an id line, that id is all digits, and some earlier dispatched event had an all-digits id at least as large, drop the event: don't return it and change nothing, including the last event id.

## Level 4: Assemble streamed messages

Marram's gateway sends three event types with JSON data:

- `start`: `{"msg": "m1"}` opens message `m1` with empty text.
- `delta`: `{"msg": "m1", "text": "..."}` appends text to an open message.
- `stop`: `{"msg": "m1"}` marks the message done.

Events of any other type are ignored here (they are still returned by `feed`). Assemble only events that were dispatched (dropped replays never count).

- `message(timestamp, msg_id)`: `{"text": ..., "done": True/False}`, or `None` if the message never started.
- `completed(timestamp)`: the ids of done messages, in the order their `stop` arrived.
- `errors(timestamp)`: how many `start`, `delta` or `stop` events were bad and ignored: data that isn't valid JSON or has no `"msg"`, a `delta` or `stop` for a message that isn't open (never started or already done), a `delta` without string `text`, or a second `start` for the same message.
- A disconnect doesn't close open messages. After reconnecting, the stream continues them.
