---
title: "Written Design: Streaming UX for the Order Desk"
type: written
minutes: 35
sections:
  - key: first_paint
    label: "First paint and the thinking gap"
    prompt: "What does the user see from the moment they press Enter until the first word of the answer? Give a TTFT target, say how you'd measure it, and name the levers you'd use if it's too long."
    words: [80, 220]
  - key: tools
    label: "Tool calls while streaming"
    prompt: "The assistant often calls check_stock or get_order mid-answer. What does the UI show while a tool runs, and what does your backend check before running a tool from a streamed tool_use block?"
    words: [60, 180]
  - key: failures
    label: "Failure states"
    prompt: "Describe exactly what the user sees, and what your backend does, for: an error event mid-stream, a stream that just stops, a refusal after partial text, and stop_reason max_tokens."
    words: [100, 250]
  - key: cancel
    label: "Cancellation"
    prompt: "The user clicks Stop halfway through an answer. Walk through what happens in the browser, the proxy and the connection to the API, and what's kept in the conversation history."
    words: [50, 160]
  - key: metrics
    label: "Citations and metrics"
    prompt: "Answers cite the returns policy. How do citations appear while the answer streams? Then list the metrics you'd put on the dashboard for this feature and the alert thresholds you'd start with."
    words: [60, 200]
rubric:
  - name: First paint and TTFT
    points: 20
    lookFor: "Shows an immediate working state, explains that thinking (display omitted by default on current models) happens before the first visible text, sets a concrete TTFT target and measures it from request send to the first non-empty text delta, and names levers: effort, a cached prefix, smaller model or summarized thinking display, less work before the call."
  - name: Tool calls handled safely
    points: 20
    lookFor: "Shows a specific status while a tool runs (for example 'Checking stock for TS-CB-3C25'), accumulates input JSON until content_block_stop, validates the parsed input before running (especially with eager input streaming, where the server doesn't validate), and never runs a tool from a truncated (max_tokens) or refused turn."
  - name: Failure states are distinct and correct
    points: 25
    lookFor: "Error event and silent drop both mark the answer incomplete and offer retry or continue (continuation via a user message on current models, not assistant prefill); refusal discards the partial text and shows a clear message rather than leaving half an answer; max_tokens is labelled as cut off. Backend logs request id and stop reason for each."
  - name: Cancellation stops generation
    points: 15
    lookFor: "Stop closes the stream all the way to the API (proxy forwards the cancel, stops reading, closes the upstream connection) rather than hiding output while it keeps generating. States what is stored in history (the partial text marked as interrupted, or nothing) and keeps history append-only."
  - name: Citations and measurable operations
    points: 20
    lookFor: "Renders citations as they arrive via citations_delta (or attaches markers at block end) and handles uncited claims. Dashboard has TTFT p50/p95, time to last token, error and refusal rates, cancel rate, output tokens including thinking per answer, with starting thresholds tied to the targets."
passScore: 70
graderNotes: "Mark down generic UX advice that never names a protocol event or stop reason. If the answer says it would keep partial text on screen after a refusal, cap 'Failure states are distinct and correct' at 10. If TTFT is measured from message_start or the first byte instead of the first visible text, cap 'First paint and TTFT' at 12. If Stop only hides the text while the stream keeps running upstream, cap 'Cancellation stops generation' at 6. If tools run on unvalidated or truncated input, cap 'Tool calls handled safely' at 8. Reward concrete numbers (targets, thresholds) and specific UI copy. Don't reward claims about exact billing of cancelled streams; the course says to check current docs."
anchors:
  - label: weak
    expect: [0, 45]
    answer:
      first_paint: "We stream tokens so the user sees the answer right away. If it's slow we'll use a faster model."
      tools: "Show a spinner while tools run and then continue the answer."
      failures: "If there's an error we show 'Something went wrong, please try again'. Otherwise we just show whatever text came back."
      cancel: "The Stop button hides the rest of the answer."
      metrics: "We'll show citations at the end and track latency and errors in Datadog."
  - label: strong
    expect: [75, 100]
    answer:
      first_paint: "On Enter the message appears instantly with a 'Looking into it' state. Sonnet 5.5 thinks before it writes, and thinking display is omitted by default, so the stream opens with an empty thinking block; that's the silent gap. Target: TTFT p50 under 2 s and p95 under 4 s, measured from request send to the first non-empty text_delta, not message_start. Levers in order: effort low for this route (set explicitly, Sonnet defaults to high), keep the system prompt and tools cached and stable, cut retrieval before the call, and if we still need reassurance, request summarized thinking and show a one-line progress note."
      tools: "When a tool_use block starts we show its name in plain words ('Checking stock for TS-CB-3C25') using the partial input for the preview only. The backend accumulates input_json_delta strings and parses at content_block_stop, validates against our own schema (the server doesn't validate with eager input streaming), and checks the SKU and PO format. We never run a tool from a turn that ended max_tokens or refusal."
      failures: "Error event (for example overloaded_error) or a stream with no message_stop: keep the partial text greyed with 'Answer interrupted' and two buttons, Retry and Continue. Continue sends a new user message with the partial text and asks the model to carry on (no assistant prefill on current models). Refusal: remove the partial text and show 'I can't help with that here. The order desk can.' with a link; log stop_details.category. max_tokens: keep the text with 'Answer cut off', offer 'Show more'. Each case logs request id, stop reason, TTFT and tokens."
      cancel: "Stop sends a cancel to the proxy, which stops reading and closes the upstream connection so generation actually stops; the browser stops rendering at once. History keeps the partial assistant text marked 'stopped by user' so the next turn makes sense, appended, never edited later. We assume tokens generated before the close are billed and track cancel rate to see the cost."
      metrics: "Citations arrive as citations_delta events; we attach a superscript marker to the current text block and fill the source panel live, and flag uncited sentences longer than a few words for review sampling. Dashboard: TTFT p50/p95 (alert if p95 over 5 s for 10 min), time to last token, error and drop rate (alert over 1%), refusal rate (alert on a 3x jump), cancel rate, output tokens per answer split into thinking and text, and cost per answer."
---

Imani Ferrowell (fictional) is rolling out the policy assistant from earlier in this module to 40 order-desk staff. In the pilot they complained about three things: "it sits there doing nothing for a few seconds", "it showed me half an answer about bypassing a credit check and then went blank", and "Stop doesn't stop it, the fans keep spinning". She's asked you for a one-page design of the streaming experience before the rollout, which her front-end team will build against.

Write it as you would for that team: concrete UI states, the events or stop reasons that trigger each one, the numbers you're committing to, and what the backend does. Use what you built in the SSE parser exercise. This is also the shape of answer interviewers look for when a design round turns to "and how does this feel to the user?": specific states tied to specific signals, with targets.

You'll be graded on whether each state is tied to the right protocol signal, whether failures are handled distinctly and safely, and whether the design is measurable.
