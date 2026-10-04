---
title: Module 9 Quiz
type: quiz
minutes: 12
questions:
  - q: 'In week one at a new customer, what should you do before writing deployment code?'
    options:
      - Pick the cloud provider you know best
      - Deploy a prototype to your own account and migrate later
      - Wait for the security questionnaire
      - 'Map their environment: compute, network allowlists, data rules, identity, secrets, observability and change process'
    answer: 3
    explain: Their environment sets the rules. A one-page environment doc prevents late surprises like 'production can't reach the internet.'
  - q: A bank wants to use Claude through the cloud platform it already has a contract with. What should you check first?
    options:
      - Nothing; every platform is identical
      - 'That every feature your design depends on is available on that platform, and which client and model IDs it uses'
      - Whether you can bypass their proxy
      - That the bank switches to the Claude API instead
    answer: 1
    explain: 'Claude is available on the Claude API, Amazon Bedrock, Google Cloud Vertex AI and Microsoft Foundry, but feature availability and client setup differ.'
  - q: Where should ANTHROPIC_API_KEY live for the production service?
    options:
      - 'In the customer''s secrets manager, injected at runtime, scoped to production and rotated'
      - 'In config.py, so it''s versioned'
      - In the README for the customer's team
      - In a Slack message to the platform engineer
    answer: 0
    explain: 'Never in code, docs or chat. Inject from a secrets manager, scope per environment, rotate, and revoke first if it leaks.'
  - q: Why should a config loader report every problem at once and refuse to start?
    options:
      - It's faster to run
      - Python requires it
      - So the service can start with defaults
      - 'Errors caught at deploy time are cheap; one error per deploy cycle wastes hours, and a bad value discovered at 3 a.m. is an incident'
    answer: 3
    explain: Fail fast and fail completely.
  - q: Your loader treats ENABLE_AUTO_CREDIT="false" as enabled. What went wrong?
    options:
      - The variable name is too long
      - Environment variables can't hold booleans
      - 'bool("false") is True in Python, because any non-empty string is truthy; parse true/false values explicitly'
      - The secrets manager corrupted the value
    answer: 2
    explain: 'Parse true/1/yes/on and false/0/no/off explicitly, and reject anything else.'
  - q: What should you log for every Claude call by default?
    options:
      - 'The full prompt and response, for debugging'
      - Nothing; logs cost money
      - 'Metadata: request ID, version, model, tokens (including cache), latency, stop reason, cost and error type, with personal data redacted from any free text'
      - Only errors
    answer: 2
    explain: Metadata answers operational questions without copying customer conversations into widely shared logs.
  - q: The median latency is flat but customers complain about slowness. What should you check?
    options:
      - 'Tail latency (p95/p99): a flat median can hide slow requests for a minority of customers'
      - The average output length
      - Nothing; the median is fine
      - The number of deploys
    answer: 0
    explain: 'Always watch tail latency. In the metrics exercise, p50 barely moved while p95 tripled.'
  - q: An alert pages someone because 1 of 3 requests failed at 3 a.m. How should you improve it?
    options:
      - Require a minimum request count and a sustained window before paging
      - Delete all error alerts
      - Page more people
      - Lower the threshold
    answer: 0
    explain: Alerts must be actionable and urgent. Minimum volumes and windows cut noise; fatigue makes people ignore the alert that matters.
  - q: Error rates spike right after a deploy. What do you do first?
    options:
      - Find the root cause before changing anything
      - 'Roll back the deploy, then investigate'
      - Write the post-mortem
      - Increase max_retries to 10
    answer: 1
    explain: Mitigate first. Rolling back stops the harm; the investigation can happen calmly afterwards.
  - q: Your circuit breaker is open and the cooldown has passed. What happens on the next request?
    options:
      - It's rejected forever
      - The breaker resets the cooldown without trying
      - All queued requests are sent at once
      - 'The breaker goes half-open and lets a trial request through; success closes it, failure reopens it'
    answer: 3
    explain: Half-open tests whether the dependency has recovered without flooding it.
  - q: 'Your fallback catches every exception, including a JSON parsing bug in your own code. Why is that a problem?'
    options:
      - It isn't; fallbacks should catch everything
      - Python can't catch JSON errors
      - Real bugs get hidden behind the fallback and the breaker opens for the wrong reason; catch only dependency errors such as anthropic.APIError
      - It makes the code slower
    answer: 2
    explain: Degrade on dependency failures; let your own bugs surface so they get fixed.
  - q: 'After a deploy, cache writes happen on every call and 429 errors appear, with flat traffic. What''s the most likely cause?'
    options:
      - An outage at the model provider
      - A traffic spike
      - 'Something in the cached prefix (like a timestamp in the system prompt) now changes every request, so caching stopped and uncached input hit rate limits'
      - The model's output got longer
    answer: 2
    explain: 'Errors are 429s (not 5xx), traffic is flat, the timing matches the deploy, and the cache-write rate went to 100%.'
  - q: Which is a good post-mortem action item?
    options:
      - Be more careful with prompts
      - Dana should test better
      - 'Add cost-per-request and cache-hit-rate checks to the release gate. Owner: Sam. Due: March 17'
      - Consider improving monitoring
    answer: 2
    explain: 'Blameless, specific, owned, dated, and it catches the mistake automatically.'
---

Thirteen questions on customer environments, config and secrets, observability, incident response, graceful degradation and post-mortems. You need **11 out of 13** to pass. You can retry as many times as you like.
