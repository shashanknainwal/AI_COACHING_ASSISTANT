---
title: "Module E5 Quiz"
type: quiz
minutes: 14
questions:
  - q: "You turn on streaming for a chat feature. What changes?"
    options:
      - "The full answer finishes sooner, since tokens are sent in parallel"
      - "First words appear earlier; total time stays about the same"
      - "The model thinks less, so first-token and total time both drop"
      - "Output tokens are billed at a lower rate when they are streamed"
    answer: 1
    explain: "Streaming improves perceived latency. Total time still depends on input processing, thinking and output length."
  - q: "On Claude Opus 5.5, users of a streaming assistant complain about a pause before any text appears, even with a cached prompt. What's the most likely cause and a first fix?"
    options:
      - "The SDK buffers the first 100 tokens; turn buffering off"
      - "Streaming isn't supported on Opus; move the route to Sonnet"
      - "The cache write is slow; switch the prefix to the 1-hour TTL"
      - "It thinks first; lower effort or show summarized thinking"
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
      - "All 50 miss; warm with one request, then send the rest"
      - "One writes the cache and the other 49 read it instantly"
      - "The API rejects 49 of them as duplicate requests"
      - "Concurrent requests skip caching; use the Batch API"
    answer: 0
    explain: "Parallel requests can't read a cache entry that's still being written. Warm it with one request first."
  - q: "Your retry wrapper sees each of these errors once. Which one should it raise immediately instead of retrying?"
    options:
      - "429 rate_limit_error with retry-after: 5"
      - "529 overloaded_error during a busy period"
      - "APITimeoutError after the attempt deadline"
      - "400 invalid_request_error"
    answer: 3
    explain: "A 400 means the request itself is wrong; the same bytes will fail the same way. 429, 5xx (including 529) and connection errors or timeouts are transient."
  - q: "Your wrapper makes up to 4 attempts, and each attempt goes through an SDK client left at its default settings. Why does the lesson call with_options(max_retries=0)?"
    options:
      - "The SDK doesn't support retries on messages.create at all"
      - "The SDK retries twice itself, so layers multiply to 12 calls"
      - "max_retries=0 is what makes the SDK honor retry-after"
      - "It turns off the request timeout so your deadline can work"
    answer: 1
    explain: "Stacked retry layers multiply load during exactly the incidents where load hurts most. Keep one layer that owns the policy."
  - q: "Which definition of cost per completed task is the one to defend in a design review?"
    options:
      - "The price per million tokens of the model you route to"
      - "The average cost of the successful requests only"
      - "All spend, failures included, over tasks done right"
      - "The monthly bill divided by the number of API requests"
    answer: 2
    explain: "A cheap call that fails still bills its tokens, then the retry. Only dividing total spend by completed tasks captures that."
  - q: "Which statement about the Message Batches API is correct?"
    options:
      - "Every meter is half price; results arrive in any order"
      - "Only output is half price; results keep submission order"
      - "It finishes within an hour and supports tool loops inside"
      - "It's the right choice for a high-volume live chat feature"
    answer: 0
    explain: "Batch is 50% off every meter and stacks with caching. Most batches finish within an hour but the limit is 24 hours, each request is single-shot, and results arrive in any order."
  - q: "A teammate proposes splitting one high-volume route across three models by complexity. Besides evaluating each route, what cost effect should you raise?"
    options:
      - "Cheaper models turn prompt caching off entirely"
      - "Caches are per model, so each route writes its own"
      - "Routing doubles the input price on every model used"
      - "An organization can use only one model at a time"
    answer: 1
    explain: "Prompt caches are model-scoped. Try the strongest model at lower effort first: one model means one cache and one eval."
  - q: "You enabled fallbacks=\"default\" on Claude Opus 5.5. During a traffic spike the API returns 429s for Opus 5.5. What happens?"
    options:
      - "The request is retried on the fallback model automatically"
      - "The request waits in a server-side queue until capacity frees"
      - "The 429 comes back; fallbacks don't cover rate limits"
      - "The API returns a refusal stop reason with a rate_limit category"
    answer: 2
    explain: "Server-side fallbacks handle policy declines. Rate limits, overloads and server errors are returned as they are; availability stays your code's job."
  - q: "You estimate an extraction route on Sonnet 5.5 at 600 output tokens per request and send no effort setting. Why is the estimate likely too low?"
    options:
      - "Sonnet 5.5 bills structured output at twice the text rate"
      - "Output tokens are rounded up to the nearest thousand on bills"
      - "Sonnet 5.5 thinks at effort high by default, billed as output"
      - "Cached prefixes are billed again as output on every request"
    answer: 2
    explain: "Opus 5.5 and Haiku 5.5 default to medium effort and Sonnet 5.5 to high; all three think by default, and thinking tokens are billed as output. Set effort explicitly, or add a thinking line to the estimate, and confirm with usage.output_tokens."
  - q: "A classifier on Haiku 5.5 uses max_tokens=256 and no effort setting. Some responses come back with stop_reason \"max_tokens\" and no label. What's the best fix?"
    options:
      - "Retry the same request until a label comes back"
      - "Set effort low and give max_tokens room for thinking"
      - "Add 'answer in one word' in capitals to the prompt"
      - "Switch the route to Opus 5.5, which never truncates"
    answer: 1
    explain: "max_tokens covers thinking, and Haiku 5.5 thinks at medium effort by default. Lower the effort (or disable thinking, which Haiku 5.5 accepts at effort high or below) and leave headroom; a truncated answer is a failed attempt you still pay for."
---

Twelve questions on latency, retries, cost and degradation. You need 10 correct to pass.
