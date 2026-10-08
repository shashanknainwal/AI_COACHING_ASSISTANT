---
title: "Module C2 Quiz"
type: quiz
minutes: 12
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
      - "The API is stateless, so your code resends turns 1 to 19 as input on turn 20"
      - "The model charges a fee for each turn of memory it keeps"
      - "Output prices rise as the context window fills"
      - "It doesn't; the API remembers the conversation for free"
    answer: 0
    explain: "The model has no memory between requests. Every turn resends the history, and every input token is billed."
  - q: "A teammate adds `temperature=0` to a request to Claude Opus 5.5 to make the output consistent. What happens?"
    options:
      - "Outputs become fully deterministic"
      - "The parameter is ignored silently"
      - "The request is rejected with a 400; sampling parameters are removed on Opus 5.5"
      - "Thinking is turned off"
    answer: 2
    explain: "Opus 5.5 rejects temperature, top_p and top_k. Get consistency from clear prompts, structured outputs, enums and evals."
  - q: "On Claude Opus 5.5, how do you make the model spend less on reasoning for a simple classification route?"
    options:
      - "Send thinking: {type: \"disabled\"}"
      - "Set a small budget_tokens"
      - "Lower max_tokens until the answer just fits"
      - "Set output_config.effort to low"
    answer: 3
    explain: "Thinking can't be disabled on Opus 5.5 and budget_tokens is rejected. Effort is the control. max_tokens only cuts the answer off."
  - q: "The model's response has stop_reason \"tool_use\" with two tool_use blocks. What should your code send next?"
    options:
      - "Run both tools and send two separate user messages, one tool_result each"
      - "Append the assistant response, then one user message with both tool_result blocks, each with its matching tool_use_id"
      - "Send only the result of the first tool and wait for the model to ask again"
      - "Nothing; the API runs user-defined tools itself"
    answer: 1
    explain: "Your code runs the tools. Return all results in a single user message; splitting them teaches the model to stop making parallel calls."
  - q: "You need the model's final answer as JSON matching a schema, with no tool actions. On Claude Opus 5.5, what's the right approach?"
    options:
      - "Use output_config.format with a JSON schema"
      - "Prefill the assistant turn with an opening brace"
      - "Define a fake tool and force it with tool_choice"
      - "Ask nicely in the prompt and retry until json.loads succeeds"
    answer: 0
    explain: "Structured outputs guarantee schema-valid JSON. Prefill and forced tool_choice are both rejected on Opus 5.5."
  - q: "Your system prompt starts with \"Current time: {now}\" and then 30K tokens of stable instructions marked with cache_control. What happens to caching?"
    options:
      - "The instructions are cached; only the timestamp is reprocessed"
      - "It caches, but only with the 1-hour TTL"
      - "It caches after the first five requests"
      - "Nothing after the timestamp ever hits the cache, because the prefix changes every request"
    answer: 3
    explain: "Caching is a prefix match. A changing value at the front invalidates everything after it. Move the timestamp after the last breakpoint."
  - q: "How do you confirm a prompt cache is actually hitting in production?"
    options:
      - "Check that latency went down once"
      - "Watch usage.cache_read_input_tokens on responses, ideally with a standing test or monitor"
      - "Check that cache_control appears in the request"
      - "Look for a cache_hit header on the response"
    answer: 1
    explain: "The usage fields are the ground truth. Cache failures don't error, so keep a standing check."
  - q: "With the default 5-minute TTL (write about 1.25x base input, read about 0.1x), when does caching a shared prefix start saving money?"
    options:
      - "Only after about ten requests"
      - "Never, if the prefix is under 100K tokens"
      - "From the second request that reuses the prefix within the TTL"
      - "Only with the 1-hour TTL"
    answer: 2
    explain: "Two requests cost 1.25 + 0.1 = 1.35 prefix-units cached, against 2.0 uncached. The 1-hour TTL (2x write) needs three requests."
  - q: "An eval table: Model X quality 0.95, p95 4.5 s, $20/1k. Model Y quality 0.92, p95 2.0 s, $9/1k. Model Z quality 0.84, p95 0.8 s, $1/1k. Requirements: quality at least 0.90, p95 under 3 s, budget $12/1k. Which model?"
    options:
      - "Model X, because it has the highest quality"
      - "Model Z, because it's the cheapest"
      - "None of them"
      - "Model Y, the only one that meets every constraint"
    answer: 3
    explain: "Apply constraints first: X is too slow and too expensive, Z misses the quality bar. Y is the only candidate left, so it's also the cheapest that qualifies."
---

Ten questions on the fundamentals from this module. You need 8 correct to pass.
