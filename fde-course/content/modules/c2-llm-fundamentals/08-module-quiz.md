---
title: "Module C2 Quiz"
type: quiz
minutes: 14
questions:
  - q: "A request on Claude Sonnet 5.5 ($2 input, $10 output per million tokens) uses 4,000 input tokens and 1,000 output tokens, with no caching. What does it cost?"
    options:
      - "$0.008"
      - "$0.012"
      - "$0.018"
      - "$0.050"
    answer: 2
    explain: "4,000 x $2/M = $0.008 for input, plus 1,000 x $10/M = $0.010 for output. Total $0.018."
  - q: "Your chat assistant keeps the whole conversation in the request. Why does turn 20 cost more than turn 2?"
    options:
      - "Your code resends turns 1 to 19 as input"
      - "The API charges a monthly fee for stored conversation memory"
      - "Output prices per token rise as the context window fills up"
      - "It doesn't: the API remembers earlier turns for free"
    answer: 0
    explain: "The API is stateless. Every turn resends the history, and every input token is billed."
  - q: "A teammate says: 'Set temperature to 0 and the model becomes fully deterministic.' What's the strongest reply?"
    options:
      - "Correct: temperature 0 always picks the same token, so outputs never change"
      - "Wrong: temperature only changes the length of the output, not the content"
      - "Wrong: temperature 0 only removes randomness from the thinking blocks"
      - "Close to greedy, but logits can shift between runs, so no guarantee"
    answer: 3
    explain: "Temperature 0 approaches greedy decoding, but batching and floating-point order on GPUs can change logits slightly, and a near-tie can flip. On Opus 5.5 the parameter is rejected anyway, so consistency comes from prompts, schemas and evals."
  - q: "On Claude Opus 5.5, how do you make the model spend less on reasoning for a simple classification route?"
    options:
      - "Send thinking with type disabled"
      - "Set a small budget_tokens value for thinking"
      - "Lower max_tokens until the answer just fits"
      - "Set output_config.effort to low"
    answer: 3
    explain: "Thinking can't be disabled on Opus 5.5 and budget_tokens is rejected. Effort is the control. max_tokens covers thinking and the answer together, so lowering it just cuts the reply off."
  - q: "Which statement about default effort levels is accurate?"
    options:
      - "Every current Claude model defaults to high unless told otherwise"
      - "Opus 5.5 and Haiku 5.5 default to medium; Sonnet 5.5 defaults to high"
      - "Only Opus 5.5 defaults to medium; every other model defaults to low"
      - "Effort has no default, so any request without it returns a 400 error"
    answer: 1
    explain: "Opus 5.5 and Haiku 5.5 default to medium, Sonnet 5.5 to high. Because defaults differ by model, cost examples should set effort explicitly."
  - q: "The model's response has stop_reason \"tool_use\" with two tool_use blocks. What should your code send next?"
    options:
      - "Two separate user messages, one tool_result in each, sent in the same order as the calls"
      - "The assistant turn appended unchanged, then one user message with both results"
      - "Only the first tool's result, then wait for the model to ask again"
      - "Nothing at all, because the API runs user-defined tools itself"
    answer: 1
    explain: "Your code runs the tools. Append the assistant response as it came back, then return all results in a single user message, each with its matching tool_use_id."
  - q: "Your agent on Opus 5.5 trims the oldest turns to save tokens. For a new account, what happens on the next request that replays a thinking block?"
    options:
      - "Nothing happens, because trimming old turns is the recommended way to save tokens"
      - "The request returns a 400, because the thinking signatures no longer match"
      - "The model silently ignores the trimmed turns and carries on"
      - "Only the prompt cache misses; the request otherwise succeeds exactly as before"
    answer: 1
    explain: "Preserved thinking binds each signature to every earlier message. For accounts created on or after 2026-08-31, an edited history returns a 400 by default. Keep history append-only and use compaction or context editing."
  - q: "You need the model's final answer as JSON matching a schema, with no tool actions. On Claude Opus 5.5, what's the right approach?"
    options:
      - "Use output_config.format with a JSON schema"
      - "Prefill the assistant turn with an opening brace character"
      - "Define a fake tool and force it with tool_choice set to that tool"
      - "Ask for JSON in the prompt and retry until json.loads succeeds"
    answer: 0
    explain: "Structured outputs guarantee schema-valid JSON. Prefill and forced tool_choice are both rejected on Opus 5.5."
  - q: "Your system prompt starts with \"Current time: {now}\" and then 30K tokens of stable instructions marked with cache_control. What happens to caching?"
    options:
      - "The instructions are cached; only the timestamp is reprocessed each time"
      - "It caches normally, but only if you switch to the 1-hour TTL"
      - "Nothing after the timestamp hits, because the prefix changes"
      - "It starts caching after the first five requests have warmed it"
    answer: 2
    explain: "Caching is a prefix match. A changing value at the front invalidates everything after it. Move the timestamp after the last breakpoint."
  - q: "A teammate wants to send a 600K-token knowledge base on every request 'because it fits in the 1M window'. Besides cost and latency, what's the main objection?"
    options:
      - "Requests over 500K tokens are rejected on current models"
      - "Long contexts disable prompt caching on every current model"
      - "Accuracy at finding one fact tends to drop as context grows"
      - "The model only reads the first 100K tokens of any request"
    answer: 2
    explain: "Context rot: as the context grows, models get worse at recalling a specific fact in it. Retrieving the relevant chunks and caching the stable prefix addresses cost, latency and quality together."
  - q: "With the default 5-minute TTL (write about 1.25x base input, read about 0.1x), when does caching a shared prefix start saving money?"
    options:
      - "Only after about ten requests have reused the same prefix"
      - "Never, if the prefix is shorter than about 100K tokens"
      - "Only once you switch the breakpoint to the 1-hour TTL"
      - "From the second request within the TTL"
    answer: 3
    explain: "Two requests cost 1.25 + 0.1 = 1.35 prefix-units cached, against 2.0 uncached. The 1-hour TTL (2x write) needs three requests."
  - q: "An eval table: Model X quality 0.95, p95 4.5 s, $20/1k. Model Y quality 0.92, p95 2.0 s, $9/1k. Model Z quality 0.84, p95 0.8 s, $1/1k. Requirements: quality at least 0.90, p95 under 3 s, budget $12/1k. Which model?"
    options:
      - "Model X, because it has the highest quality score"
      - "Model Z, because it's cheapest and fastest by far"
      - "Model Y"
      - "None of them meets all three requirements"
    answer: 2
    explain: "Apply constraints first: X is too slow and too expensive, Z misses the quality bar. Y is the only candidate left, so it's also the cheapest that qualifies."
---

Twelve questions on the fundamentals from this module. You need 10 correct to pass.
