---
title: "Exercise: Circuit Breaker, Fallback and Kill Switch"
type: exercise
minutes: 30
hints:
  - "`allow`: if the state is `\"open\"` and `self.clock() - self.opened_at >= self.cooldown_s`, switch to `\"half_open\"`. Then return `self.state != \"open\"`."
  - "`record_failure`: add 1 to `failures`; if the state is `\"half_open\"` or `failures >= failure_threshold`, set `state = \"open\"` and `opened_at = self.clock()`."
  - "`record_success`: back to `\"closed\"`, `failures = 0`, `opened_at = None`."
  - "`triage`: check the flag (`flags.get(\"claude_triage\", False)`), then `breaker.allow()`, then try `claude_triage` and catch only `anthropic.APIError`."
  - "Add the source with `dict(result, source=\"claude\")`."
---

When the Claude API has a bad minute (or Brightway's network does), the assistant must keep sorting tickets, more crudely, rather than piling up timeouts. You'll add three standard production defenses:

- A **fallback**: the old keyword rules (`rules_triage`, given) answer when Claude can't.
- A **circuit breaker**: after repeated failures, stop calling Claude for a while instead of making every request wait for a timeout.
- A **kill switch**: a feature flag the on-call engineer can flip to turn Claude off instantly, with no deploy.

`claude_triage(client, text)` (one API call) and `rules_triage(text)` are given.

## Your task

**1. `CircuitBreaker`** (`__init__` is given) has three states:

```
closed ──(failure_threshold consecutive failures)──▶ open ──(cooldown_s passes)──▶ half_open
  ▲                                                    ▲                              │
  └──────────────────── success ───────────────────────┼──────────────────────────────┤
                                                       └────────── failure ───────────┘
```

- `allow()`: `True` when closed or half-open. When open, switch to `"half_open"` and return `True` once `clock() - opened_at >= cooldown_s`; otherwise return `False`.
- `record_success()`: back to `"closed"` with `failures = 0` and `opened_at = None`.
- `record_failure()`: add one failure. Open the breaker (setting `opened_at = clock()`) when failures reach `failure_threshold`, or **immediately** if the state was `"half_open"`.

**2. `triage(client, breaker, text, flags=FEATURE_FLAGS)`** returns the triage dict plus a `"source"` key:

| Situation | Result | `source` |
|---|---|---|
| `flags["claude_triage"]` is false or missing | rules, no API call | `"disabled"` |
| `breaker.allow()` is false | rules, no API call | `"circuit_open"` |
| `claude_triage` raises `anthropic.APIError` | record the failure, use rules | `"fallback"` |
| success | record the success, Claude's result | `"claude"` |

Catch **only** `anthropic.APIError`. A bug in your own code (such as invalid JSON) should still raise, not hide behind the fallback.

Press **Run** to watch the breaker open during a simulated outage and recover after the cooldown, then **Submit**.
