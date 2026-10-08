---
title: "Post-Mortems, Runbooks and Handoff"
type: reading
minutes: 15
---

> **By the end of this lesson you will be able to:**
> - Write a blameless post-mortem that leads to real fixes
> - Write runbooks an on-call engineer can follow at 3 a.m.
> - Hand off a system so the customer's team can run it without you
> - Recognize when a deployment is truly done

## The blameless post-mortem

After every significant incident, write a post-mortem within a few days, while memories are fresh. **Blameless** means it focuses on how the system allowed the failure, not on who made a mistake. People who fear blame hide information, and hidden information means the same incident happens again.

"Dana pushed a bad prompt" is blame. "A prompt change could reach production without the eval gate, and the gate didn't check cost or cache hit rate" is a system problem you can fix.

### Structure

Here's a post-mortem for the incident you debugged:

> **Summary.** On March 10, 14:00-14:45 UTC, ticket triage was slow (average model latency up from 974 ms to 1,434 ms, and several seconds more for requests that hit rate limits) and 16 tickets failed. The cost per request rose about 3.8×. The cause was release v1.8.0, which added the current date and time to the system prompt.
>
> **Impact.** 16 tickets failed and were re-processed by 15:30; about 120 tickets were triaged slowly; about $0.80 of extra API cost (it would have been about $34 a day at 5,000 tickets a day).
>
> **Timeline.** 14:00 v1.8.0 deployed · 14:20 first rate-limit errors · 14:38 latency alert fires · 14:45 rollback to v1.7.3 · 14:52 customer update · 15:30 failed tickets re-processed.
>
> **Root cause.** The timestamp at the start of the system prompt made every request's prefix unique, so prompt caching stopped working. Every request paid for 3,000 uncached input tokens. Uncached input counts toward input-token rate limits, so the extra tokens triggered 429 errors, and retries added latency.
>
> **What went well.** Structured logs with versions made the diagnosis quick; the rollback took 4 minutes.
>
> **What went poorly.** The eval gate checked quality but not cost or cache hit rate; the latency alert fired 38 minutes after the deploy.
>
> **Action items.**
> | Action | Owner | Due |
> |---|---|---|
> | Move the date into the user message, after the cached prefix | Priya (FDE) | Mar 12 |
> | Add cost-per-request and cache-hit-rate checks to the release gate | Sam (Brightway platform) | Mar 17 |
> | Alert when the cache hit rate is below 80% for 10 minutes | Priya | Mar 14 |
> | Add a canary stage: 5% of traffic for 30 minutes before full rollout | Sam | Mar 24 |

Rules for action items: **specific, owned, dated, and tracked** like any other work. "Be more careful" is not an action item. Prefer fixes that make the mistake impossible or caught automatically over fixes that rely on people remembering.

To find root causes, keep asking "why?" until you reach something you can change. Why was it slow? Rate limits. Why? Many more input tokens. Why? Caching stopped. Why? The prefix changed every request. Why did that ship? The release gate didn't measure cost.

## Runbooks

A runbook tells the on-call engineer what to do when a specific thing goes wrong. Write one for every alert. Assume the reader is tired, stressed and new to the system.

```
RUNBOOK: Triage cache hit rate low
Alert:    cache_hit_rate < 0.8 for 10 minutes (ticket)
Impact:   Higher cost and latency; may lead to rate-limit errors.

1. Check recent deploys:  deploy log in #brightway-deploys. Deploy in the last hour? Roll it back (step 4).
2. Check logs by version: dashboard "Triage / by version". Cache writes on every call → the system prompt varies between requests.
3. Check for rate limits: error_type=RateLimitError rising? Treat as SEV2.
4. Roll back:            `deploy rollback triage --to previous` (takes about 4 minutes).
5. Still broken? Flip the kill switch (flag claude_triage=false). Tickets route by rules; quality drops, nothing fails.
Escalate: FDE on call (pager), then Brightway platform team lead.
```

Good runbooks are **specific** (exact commands, dashboard names, links), **ordered** (safest and most likely steps first), and **tested** (someone has followed them recently). Update them after every incident.

## Handoff: making yourself unnecessary

An FDE engagement ends; the system shouldn't end with it. Plan the handoff from the start, not in the last week. A system is ready to hand off when the customer's team can, **without you**:

- **Run it:** deploy, roll back, rotate secrets, scale, flip flags.
- **Watch it:** read the dashboards, receive the alerts, follow the runbooks.
- **Change it:** edit a prompt, run the eval suite, pass the release gate, ship.
- **Explain it:** to their users, their security team and their leadership.

The handoff package:

| Item | Contents |
|---|---|
| **Architecture doc** | Diagram, data flow, dependencies, key decisions and why they were made |
| **Operations guide** | Deploy, rollback, config reference, secrets, scaling, costs and budgets |
| **Runbooks** | One per alert, plus common tasks |
| **Eval suite** | The cases, graders, release gate, and how to add new cases |
| **Known issues** | Limitations, open bugs, ideas not built, and the risks of each |
| **Contacts** | Who owns what on their side; how to reach the vendor's support |

Then **prove it**: have their engineers do a real deploy, a rollback, a prompt change through the eval gate, and a simulated incident from a runbook while you watch and don't touch the keyboard. Each thing they get stuck on is a documentation gap to fix before you leave.

> **Key takeaways**
> - Blameless post-mortems fix systems, not people: summary, impact, timeline, root cause, what went well and poorly, and specific, owned, dated action items.
> - Ask "why?" until you reach something changeable; prefer fixes that catch mistakes automatically.
> - Write a specific, ordered, tested runbook for every alert, and update runbooks after incidents.
> - Hand off so the customer can run, watch, change and explain the system without you, then prove it with hands-on drills.
