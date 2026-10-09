---
title: "Incident Response and Graceful Degradation"
type: reading
minutes: 5
---

> **By the end of this lesson you will be able to:**
> - Run an incident: roles, updates, mitigation first
> - Design LLM features that degrade gracefully
> - Explain each state of a circuit breaker

It's Black Friday at Brightway and Claude calls start failing. Tickets still have to reach the right queue, and Jordan Lee wants an update every half hour. The next hour depends on choices you made weeks ago.

## Severity and roles

Agree severities with the customer in advance:

| Severity | Example | Response |
|---|---|---|
| **SEV1** | Triage down; tickets not routed | Page now, all hands, updates every 30 min |
| **SEV2** | Degraded: slow, partial failures, fallback mode | Page on-call, updates hourly |
| **SEV3** | One feature misbehaving, workaround exists | Ticket, fix within days |

Above SEV3, name an **incident lead** (decides, keeps the timeline, doesn't debug), **investigators**, and a **communicator**.

## Mitigate first, then find the cause

Stop the harm before you understand it. If a deploy just happened, roll it back now. In order of preference:

1. **Roll back** the last change (code, prompt, config or model).
2. **Flip a kill switch** to send work to the fallback path, no deploy needed.
3. **Shed load:** pause batch jobs, lower concurrency, queue non-urgent work.
4. **Switch to a tested fallback model or route.**

## Communicate

Short, regular, factual: what's affected, since when, what you did, next update time. Say "investigating" rather than guess.

> *"14:52, SEV2. Ticket triage was slow and ~5% of tickets failed between 14:20 and 14:45. We rolled back a deploy at 14:45 and the service has been normal since. Failed tickets are being re-processed. Next update at 15:30 with the cause."*

## Graceful degradation

- **A fallback path:** old rules, a simpler model, a default queue, or a human. Brightway's keyword rules route worse, but they route.
- **Mark degraded results** (`source: "fallback"`) to re-process and count them.
- **Timeouts per use case:** live chat can't wait 60 seconds; a nightly batch can.
- **Cap retries:** the SDK retries with backoff, but in an outage retries multiply load.
- **Queue work that can wait.**

### The circuit breaker

Without one, every request waits a full timeout before falling back, and slows the dependency's recovery.

- **Closed:** requests go through; count consecutive failures.
- **Open:** after N failures, skip the dependency and use the fallback at once, for a cooldown.
- **Half-open:** after the cooldown, one trial request. Success closes the breaker; failure reopens it and restarts the cooldown.

Count only **dependency** failures (API errors, timeouts). Your own bugs, like a parsing crash, must surface, not hide behind the fallback.

<div data-diagram="circuit-breaker"></div>

### Kill switches

A runtime flag that turns a feature off without a deploy. Every LLM feature with real-world effects (emails, credits) needs one. If the flag can't be read, the feature is **off**.

> **Key takeaways**
> - Agree severities in advance; name roles; post short, regular, factual updates.
> - Mitigate first (roll back, kill switch, shed load, fallback), then find the cause.
> - Circuit breaker: closed, open, half-open; count only dependency failures; kill switches default to off.
