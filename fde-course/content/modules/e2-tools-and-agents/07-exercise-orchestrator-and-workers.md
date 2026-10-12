---
title: "Exercise: An Orchestrator With Cheap, Isolated Workers"
type: exercise
minutes: 45
hints:
  - "Start with `run_worker` on one booking and get the happy path passing before you think about failures. It's the same loop you hardened earlier, pointed at a different model, with a structured report as its last turn."
  - "List every way a worker can end before you write code: an exception from the SDK, a refusal, a cut-off answer, a report you can't trust, too many calls, too much output. Each one is a `failed` result with its own `error`, and none of them may raise."
  - "Budgets protect the next unit of work. Check them when the worker asks for more tools, before you run anything from that turn."
  - "Isolation is about what goes into each worker's `messages`. If a worker's first request contains anything about another booking, the orchestrator leaked context."
  - "The lead should be able to write its summary from the reports alone. Ask yourself what it needs to know about the bookings that produced no report, and what it must never see (tool results, internal errors)."
---

Leo is back with Fernway Travel, the fictional agency from the earlier exercises. "Their duty-of-care team got hit by the Lisbon strike last month. Someone had to check every affected booking by hand while travelers waited at the airport. They want an agent that takes a disruption and a list of bookings, checks each one, and writes one summary for the ops manager. A single agent loop over 40 bookings ends up with 160 tool results in its context, so we're splitting it: an orchestrator on Opus 5.5 that plans and writes, and one cheap Haiku 5.5 worker per booking that does the lookups. Build the fan-out and the fan-in. I care about three things: no worker sees another worker's data, one bad worker never sinks the run, and I can tell what the whole thing cost."

The tools, sample data, `WORKER_TOOLS`, `REPORT_SCHEMA`, `execute_tool` and `text_of` are given. The simulated workers behave like the real API: they think first, call tools, and sometimes fail.

## Your task

**1. `worker_task(event, booking_ref)`** returns the brief one worker gets as its only user message. It must contain the event text and that one booking reference, and nothing about any other booking. Wrap the event in `<event>` tags.

**2. `run_worker(client, event, booking_ref, max_iterations=4, max_output_tokens=3000)`** runs one worker's tool loop and returns:

```python
{"booking_ref": "FW7Q2K", "status": "ok", "report": {...}, "error": None,
 "iterations": 4, "usage": {"input_tokens": 1803, "output_tokens": 61}}
```

- Every request: `WORKER_MODEL`, `WORKER_MAX_TOKENS`, `WORKER_SYSTEM`, `WORKER_TOOLS`, and `output_config` with `"effort": "low"` and a `json_schema` format using `REPORT_SCHEMA`. Haiku 5.5 thinks at `medium` by default, so you set effort explicitly and give `max_tokens` room for thinking.
- Append each `response.content` unchanged. Run every `tool_use` block with `execute_tool` and send the results back in one user message.
- When the turn isn't `tool_use`, parse the text as the report. The status is `"ok"` only if it parses to an object whose `booking_ref` is the booking this worker was given.
- Otherwise the worker ends with status `"failed"`, `report` None, and one of these `error` values:

| What happened | `error` |
|---|---|
| The SDK raised an `anthropic.APIError` (after its own retries) | the exception's class name, such as `"OverloadedError"` |
| `stop_reason == "refusal"` | `"refused"` |
| `stop_reason == "max_tokens"` | `"max_tokens"` |
| The final text isn't JSON, or reports on a different booking | `"bad_report"` |
| A `tool_use` turn arrives when total output tokens already exceed `max_output_tokens` | `"budget"` |
| A `tool_use` turn arrives on call number `max_iterations` | `"max_iterations"` |

For the last two, run none of that turn's tools. Check the budget before the iteration cap. `iterations` counts the calls that returned; `usage` sums them.

**3. `lead_message(event, reports, failed_refs)`** returns the lead's only input: the event in `<event>` tags, `json.dumps(reports)` inside `<reports>` tags, the failed booking references comma-separated inside `<not_checked>` tags (or `none`), and a closing instruction.

**4. `orchestrate(client, event, booking_refs)`** runs one worker per booking, in order, then makes **one** lead call:

```python
{"answer": "...", "reports": [...], "failed": [{"booking_ref": "KM2B7Y", "error": "OverloadedError"}],
 "usage": {"workers": {...}, "lead": {...}, "total": {...}}}
```

- The lead call uses `LEAD_MODEL`, `LEAD_MAX_TOKENS`, `LEAD_SYSTEM`, `output_config={"effort": "medium"}`, no tools, and one user message built with `lead_message`. `answer` is its text.
- If no worker produced a report, don't call the lead: `answer` is `HANDOFF_MESSAGE` and lead usage is zero.
- `usage` has the summed worker tokens, the lead tokens and the total.

Press **Run** to check five bookings against the Lisbon strike, then open the **Trace** tab. Then **Submit**.

## Why it's built this way

- **Isolation is the point.** Each worker reads one booking's tool results and hands back a six-field report. The lead's context holds five reports, not twenty tool results. That's what lets the pattern scale to 40 bookings.
- **A tool failure isn't a worker failure.** RT5V1C's flight lookup crashes, the worker still reports `unknown`, and the summary says "check by phone". A worker failure (KM2B7Y) is different: nobody knows anything, so the lead is told explicitly what wasn't checked rather than silently leaving it out.
- **Check the report against the task.** A report about the wrong booking is worse than no report. The `booking_ref` check is one line of code that calls no model.
- **Budgets per worker, totals per run.** A wandering worker (BX8C3J in the tests) stops at its cap. The roll-up is what you quote to the customer: N workers times the per-booking cost, plus one lead call.
- **In production, run the workers concurrently.** Use a thread pool or `asyncio` with a semaphore sized to your rate limit. The browser runtime here has no threads, so they run in sequence. The function boundary is the same.

In a debrief, expect: "Why not one agent with all the tools?" and "What does this cost per disruption at 40 bookings?" Have the context-size argument and a per-worker token figure ready.
