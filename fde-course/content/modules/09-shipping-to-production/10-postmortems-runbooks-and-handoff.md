---
title: "Post-Mortems, Runbooks and Handoff"
type: reading
minutes: 7
---

> **By the end of this lesson you will be able to:**
> - Write a blameless post-mortem that leads to real fixes
> - Write runbooks usable at 3 a.m.
> - Hand off a system the customer can run without you

The incident is over. Jordan Lee wants proof it won't recur, and a team that can run the system after you leave.

## The blameless post-mortem

Write it within days. **Blameless** asks how the system allowed the failure, not who erred; people who fear blame hide information. "Dana pushed a bad prompt" is blame. "A prompt change could ship without a gate checking cost" is fixable. For the incident you debugged:

> **Summary.** March 10, 14:00-14:45 UTC: triage slowed (model latency 974 → 1,434 ms, more on rate-limited requests), 16 tickets failed, cost per request rose about 3.8×. Cause: release v1.8.0 added the date and time to the system prompt.
>
> **Impact.** 16 failed tickets re-processed by 15:30; about 120 slow; about $0.80 extra API cost (about $34 a day at 5,000 tickets a day).
>
> **Timeline.** 14:00 v1.8.0 deployed · 14:20 first rate-limit errors · 14:38 latency alert fires · 14:45 rollback to v1.7.3 · 14:52 customer update · 15:30 failed tickets re-processed.
>
> **Root cause.** The timestamp made every prefix unique, so caching stopped. Each request paid for 3,000 uncached input tokens, which count toward input-token rate limits: 429s followed, and retries added latency.
>
> **Went well.** Versioned structured logs; a 4-minute rollback. **Went poorly.** The gate checked quality, not cost or cache hit rate; the alert fired 38 minutes after the deploy.
>
> **Action items.**
> | Action | Owner | Due |
> |---|---|---|
> | Move the date into the user message, after the cached prefix | Priya (FDE) | Mar 12 |
> | Add cost-per-request and cache-hit-rate checks to the release gate | Sam (Brightway platform) | Mar 17 |
> | Alert when the cache hit rate is below 80% for 10 minutes | Priya | Mar 14 |
> | Add a canary stage: 5% of traffic for 30 minutes before full rollout | Sam | Mar 24 |

Action items are **specific, owned, dated and tracked**; "be more careful" isn't one. Prefer fixes that catch the mistake automatically. Ask "why?" until you reach something changeable: slow → rate limits → more input tokens → caching stopped → prefix changed → the gate didn't measure cost.

## Runbooks

One per alert, for a tired reader new to the system:

```
RUNBOOK: Triage cache hit rate low
Alert:    cache_hit_rate < 0.8 for 10 minutes (ticket)
Impact:   Higher cost and latency; may lead to rate-limit errors.

1. Deploy in the last hour? (#brightway-deploys) Roll it back (step 4).
2. Dashboard "Triage / by version": cache writes on every call → system prompt varies per request.
3. error_type=RateLimitError rising? Treat as SEV2.
4. Roll back: `deploy rollback triage --to previous` (about 4 minutes).
5. Still broken? Kill switch claude_triage=false. Rules route tickets; quality drops, nothing fails.
Escalate: FDE on call (pager), then Brightway platform team lead.
```

Make them **specific**, **ordered** (safest, likeliest first) and **tested**; update after every incident.

## Handoff

Plan it from day one. You're done when their team can, without you, **run** it (deploy, roll back, rotate, flip flags), **watch** it, **change** it (prompt edit through the eval gate) and **explain** it.

| Item | Contents |
|---|---|
| **Architecture doc** | Diagram, data flow, decisions and why |
| **Operations guide** | Deploy, rollback, config, secrets, costs |
| **Runbooks** | One per alert, plus common tasks |
| **Eval suite** | Cases, graders, gate, how to add cases |
| **Known issues** | Limitations, open bugs, risks |
| **Contacts** | Owners; vendor support |

Then **prove it**: their engineers deploy, roll back, ship a prompt change and run a simulated incident while you keep your hands off the keyboard. Each place they get stuck is a doc gap.

> **Key takeaways**
> - Blameless post-mortems end in specific, owned, dated action items that catch mistakes automatically.
> - A specific, ordered, tested runbook for every alert.
> - Hand off so they can run, watch, change and explain it; prove it with drills.
