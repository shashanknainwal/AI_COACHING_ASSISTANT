---
title: "Incident Response and Graceful Degradation"
type: reading
minutes: 15
---

> **By the end of this lesson you will be able to:**
> - Run an incident calmly: declare it, assign roles, communicate, mitigate, then fix
> - Choose the fastest safe mitigation: rollback, kill switch, fallback or scaling back
> - Design LLM features that degrade gracefully when the model or network fails
> - Implement a circuit breaker and explain each of its states

## When things break

Something will break in production: a bad deploy, an API outage, a rate limit, a customer's network change. What separates a good team is not that nothing breaks, but **how quickly and calmly they recover**.

### Severity

Agree on severity levels with the customer in advance, so nobody argues during the incident:

| Severity | Example | Response |
|---|---|---|
| **SEV1** | Triage is down; tickets aren't being routed at all | Page immediately, all hands, updates every 30 minutes |
| **SEV2** | Degraded: slow, partial failures, or fallback mode | Page on-call, updates every hour |
| **SEV3** | Minor: one feature misbehaving, workaround exists | Ticket, fix within days |

### Roles

For anything above SEV3, name people for these roles, even if it's two people wearing several hats:

- **Incident lead:** coordinates, decides, keeps the timeline. Doesn't debug.
- **Investigators:** debug and mitigate.
- **Communications:** updates the customer's stakeholders on a regular schedule.

### Mitigate first, then find the root cause

The first goal is to **stop the harm**, not to understand it. If a deploy happened just before the problem started, roll it back now and investigate later. In the incident exercise, the team rolled back at 14:45, which ended the customer impact, and then found the cause from the logs.

Fast, safe mitigations, roughly in order of preference:

1. **Roll back** the last change (code, prompt, config or model).
2. **Flip a kill switch:** a feature flag that turns the LLM feature off and sends work to the fallback path, with no deploy needed.
3. **Shed or reduce load:** pause batch jobs, lower concurrency, queue non-urgent work.
4. **Switch to a fallback model or route,** if you've tested one.

### Communicate

Short, regular, factual updates beat long, rare ones:

> *"14:52, SEV2. Ticket triage was slow and ~5% of tickets failed between 14:20 and 14:45. We rolled back a deploy at 14:45 and the service has been normal since. Failed tickets are being re-processed. Next update at 15:30 with the cause."*

Say what's affected, since when, what you've done, and when the next update is. Don't guess at causes in updates; say "investigating."

## Graceful degradation

Design the system so that when Claude is unavailable, the business keeps running, more crudely:

- **A fallback path:** the old rules, a simpler model, a default queue, or "a human will handle this." For Brightway, keyword rules route tickets less accurately, but they still route.
- **Mark degraded results** (a `source: "fallback"` field) so you can re-process them later and measure how often it happens.
- **Timeouts that fit the use case:** a live chat can't wait 60 seconds; a nightly batch can.
- **Retries with limits:** the SDK retries transient errors with backoff. During a real outage, retries multiply load, so cap them.
- **Queue work that can wait:** if triage can be minutes late, put tickets on a queue and process them when the API recovers, instead of failing.

### The circuit breaker

When a dependency is failing, every request that tries it pays the full timeout before falling back, and the extra traffic can slow its recovery. A **circuit breaker** stops trying for a while:

- **Closed** (normal): requests go through. Count consecutive failures.
- **Open:** after N failures, skip the dependency entirely and use the fallback immediately. Wait for a cooldown.
- **Half-open:** after the cooldown, let a trial request through. Success closes the breaker; failure reopens it and restarts the cooldown.

Only count **dependency** failures (API errors, timeouts). A bug in your own code (a crash parsing a response) should surface as an error, not be hidden by the fallback.

### Kill switches

A kill switch is a feature flag, read at runtime, that turns a feature off without a deploy. Every LLM feature with real-world effects (sending emails, issuing credit) should have one, and the on-call engineer should know where it is. Make the safe state the default: if the flag can't be read, treat the feature as **off**.

> **Key takeaways**
> - Agree on severities in advance; name an incident lead, investigators and a communicator; post short, regular, factual updates.
> - Mitigate first (roll back, kill switch, shed load, fallback), then find the root cause.
> - Design fallback paths, mark degraded results, set timeouts per use case, cap retries and queue work that can wait.
> - A circuit breaker moves between closed, open and half-open to fail fast during outages; count only dependency failures; kill switches default to off.
