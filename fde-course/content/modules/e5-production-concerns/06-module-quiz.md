---
title: "Module E5 Quiz"
type: quiz
minutes: 12
questions:
  - q: "You turn on streaming for a chat feature. What changes?"
    options:
      - "The full answer finishes sooner because tokens are sent in parallel"
      - "Users see the first words much earlier, but the time to the complete answer is about the same"
      - "The model thinks less, so both first-token and total time drop"
      - "Output tokens are billed at a lower streaming rate"
    answer: 1
    explain: "Streaming improves perceived latency. Total time still depends on input processing, thinking and output length."
  - q: "On Claude Opus 5.5, users of a streaming assistant complain about a pause before any text appears, even with a cached prompt. What's the most likely cause and a first fix?"
    options:
      - "The SDK buffers the first 100 tokens; disable buffering"
      - "Streaming is off for Opus; switch to Sonnet"
      - "The cache write is slow; switch to the 1-hour TTL"
      - "The model thinks before its first visible word; lower effort for this route, or show summarized thinking as progress"
    answer: 3
    explain: "Opus 5.5 always uses adaptive thinking and omits the thinking text by default, so the first visible text waits for the reasoning. Effort controls how much it thinks; display: \"summarized\" lets you show progress."
  - q: "A request fans out to five independent model calls and waits for all of them. Each call finishes under its own p95 95% of the time. Roughly how often does the request avoid every slow call?"
    options:
      - "About 95% of the time"
      - "About 90% of the time"
      - "About 77% of the time"
      - "About 50% of the time"
    answer: 2
    explain: "0.95 to the fifth power is about 0.77. Fan-out widens the tail, so nearly one request in four waits on at least one slow call."
  - q: "You send 50 requests with the same 20,000-token cached prefix at the same moment, right after a deploy. What happens to caching, and what's the better pattern?"
    options:
      - "All 50 pay full price, because an entry is readable only once the first response starts streaming; send one, wait for its first token, then send the rest"
      - "The first request writes the cache and the other 49 read it, because writes are instant"
      - "The API rejects 49 of them as duplicates"
      - "Caching is disabled for concurrent requests, so mark them for the Batch API instead"
    answer: 0
    explain: "Parallel requests can't read a cache entry that's still being written. Warm it with one request first."
  - q: "Your retry wrapper sees each of these errors once. Which one should it raise immediately instead of retrying?"
    options:
      - "429 rate_limit_error with retry-after: 5"
      - "529 overloaded_error"
      - "APITimeoutError"
      - "400 invalid_request_error"
    answer: 3
    explain: "A 400 means the request itself is wrong; the same bytes will fail the same way. 429, 5xx (including 529) and connection errors or timeouts are transient."
  - q: "Your wrapper makes up to 4 attempts, and each attempt goes through an SDK client left at its default settings. Why does the lesson call with_options(max_retries=0)?"
    options:
      - "The SDK doesn't support retries for messages.create"
      - "The SDK already retries twice by default, so the two layers multiply: up to 12 requests instead of 4"
      - "max_retries=0 makes the SDK honor retry-after"
      - "It turns off the request timeout so your deadline logic can work"
    answer: 1
    explain: "Stacked retry layers multiply load during exactly the incidents where load hurts most. Keep one layer that owns the policy."
  - q: "Which definition of cost per completed task is the one to defend in a design review?"
    options:
      - "Price per million tokens of the model you route to"
      - "Average cost of the successful requests only"
      - "All spend on a task type, including failed attempts and retries, divided by the number of tasks that finished correctly"
      - "Monthly bill divided by the number of API requests"
    answer: 2
    explain: "A cheap call that fails still bills its tokens, then the retry. Only dividing total spend by completed tasks captures that."
  - q: "Which statement about the Message Batches API is correct?"
    options:
      - "It bills every token type at half price, cache reads and writes included, and results can come back in any order, so you key them by custom_id"
      - "It halves output prices only and returns results in submission order"
      - "It guarantees completion within one hour and supports tool loops inside a batch"
      - "It's the right choice for a live chat feature with high volume"
    answer: 0
    explain: "Batch is 50% off every meter and stacks with caching. Most batches finish within an hour but the limit is 24 hours, each request is single-shot, and results arrive in any order."
  - q: "A teammate proposes splitting one high-volume route across three models by complexity. Besides evaluating each route, what cost effect should you raise?"
    options:
      - "Cheaper models disable prompt caching entirely"
      - "Caches are per model, so the same prefix is written three times and hit rates fall on each route"
      - "Routing doubles the input price on every model"
      - "Only one model per organization can be used at a time"
    answer: 1
    explain: "Prompt caches are model-scoped. Try the strongest model at lower effort first: one model means one cache and one eval."
  - q: "You enabled fallbacks=\"default\" on Claude Opus 5.5. During a traffic spike the API returns 429s for Opus 5.5. What happens?"
    options:
      - "The request is retried on the fallback model automatically"
      - "The request is queued server-side until capacity frees up"
      - "Nothing special: server-side fallbacks trigger on refusals only, so the 429 comes back and your own retry and degradation logic must handle it"
      - "The API returns stop_reason \"refusal\" with category \"rate_limit\""
    answer: 2
    explain: "Server-side fallbacks handle policy declines. Rate limits, overloads and server errors are returned as they are; availability stays your code's job."
---

Ten questions on latency, retries, cost and degradation. You need 8 correct to pass.
