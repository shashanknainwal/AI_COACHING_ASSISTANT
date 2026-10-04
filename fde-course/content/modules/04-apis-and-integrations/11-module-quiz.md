---
title: "Module 4 Quiz"
type: quiz
minutes: 10
questions:
  - q: "Your sync job hung for 6 hours overnight on a single request. What was most likely missing?"
    options:
      - "A Session"
      - "A timeout on the request"
      - "raise_for_status()"
      - "JSON parsing"
    answer: 1
    explain: "Without a timeout, a hung server can block forever. Set timeout= on every call."
  - q: "An API returns 403 Forbidden. What should your code do?"
    options:
      - "Retry with exponential backoff"
      - "Stop and ask the customer for the right permissions"
      - "Wait for Retry-After"
      - "Switch to POST"
    answer: 1
    explain: "403 means valid credentials without permission. Retrying won't help; fix access."
  - q: "Which failures should a resilient GET retry?"
    options:
      - "400, 401, 404"
      - "Timeouts, connection errors, 429, and 5xx"
      - "Every non-200 response"
      - "Only 500"
    answer: 1
    explain: "Retry transient failures; fail fast on other 4xx, which won't improve on retry."
  - q: "A 429 response includes Retry-After: 12. Your backoff formula says wait 2 seconds. What do you do?"
    options:
      - "Wait 2 seconds"
      - "Wait 12 seconds"
      - "Retry immediately"
      - "Give up"
    answer: 1
    explain: "The server knows its own limits. Honor Retry-After when it's present."
  - q: "Why add jitter to backoff delays in production?"
    options:
      - "To make debugging harder"
      - "To spread out retries from many clients so they don't all hit the server at the same moment"
      - "To make delays shorter"
      - "Because Retry-After requires it"
    answer: 1
    explain: "Without jitter, clients that failed together retry together, causing retry storms."
  - q: "A POST to create an order times out. What's the safest way to retry?"
    options:
      - "Retry immediately, it's probably fine"
      - "Retry with the same Idempotency-Key, if the API supports it; otherwise check whether the order exists first"
      - "Retry with a new Idempotency-Key"
      - "Switch the request to GET"
    answer: 1
    explain: "A timeout doesn't tell you whether the server processed the POST. Idempotency keys make retries safe."
  - q: "You fetched page 1 of an API and got 50 records and a next_cursor. What's the bug if you stop here?"
    options:
      - "None, 50 is the limit"
      - "You silently miss every record after the first page"
      - "The cursor will expire"
      - "You'll get a 429"
    answer: 1
    explain: "Always follow pagination until there's no next cursor."
  - q: "Why must webhook signatures be compared with hmac.compare_digest instead of ==?"
    options:
      - "== doesn't work on strings"
      - "compare_digest takes the same time regardless of where the strings differ, preventing timing attacks"
      - "compare_digest is faster"
      - "It also checks the timestamp"
    answer: 1
    explain: "A normal comparison stops at the first difference, which leaks timing information to attackers."
  - q: "What does checking the webhook timestamp protect against?"
    options:
      - "Duplicate events"
      - "Replay attacks: re-sending a captured, validly signed request later"
      - "Out-of-order events"
      - "Malformed JSON"
    answer: 1
    explain: "Reject requests older than a few minutes so captured requests can't be replayed."
  - q: "The same webhook event (same id) arrives twice. What should your endpoint return the second time?"
    options:
      - "500, so the sender knows something is wrong"
      - "200, after recognizing it as a duplicate and skipping it"
      - "409 Conflict, and process it again"
      - "401"
    answer: 1
    explain: "Delivery is at-least-once. Acknowledge duplicates with 2xx so the sender stops retrying."
  - q: "Your incremental sync sets the watermark to the time the job started. What's the risk?"
    options:
      - "None"
      - "Records committed during the job, or with clock differences between servers, can fall into a gap and be missed"
      - "The job will run twice"
      - "Duplicates in the target"
    answer: 1
    explain: "Advance the watermark from the data (max updated_at received), save it after success, and fetch with an overlap."
  - q: "You re-run yesterday's sync for the same time range. What should happen if the job is well built?"
    options:
      - "Every record is created again"
      - "Zero created and zero updated: upserts make the job idempotent"
      - "It errors because records exist"
      - "The watermark moves backward"
    answer: 1
    explain: "Idempotent upserts are what make it safe to re-run failed jobs."
  - q: "Claude suggests mapping a source field named \"amount\", but the samples have \"amt_usd\". What should happen?"
    options:
      - "Use it; Claude knows best"
      - "Reject the suggestion in validation as an unknown source field, and have a human map the target"
      - "Rename the source field to amount"
      - "Lower the confidence threshold"
    answer: 1
    explain: "Validate every suggestion in code. Hallucinated field names get rejected, and required targets left uncovered get flagged."
---

Thirteen questions on HTTP and auth, pagination, retries and rate limits, webhooks, sync jobs, and using Claude for integration work. You need **11 out of 13** to pass. You can retry as many times as you like.
