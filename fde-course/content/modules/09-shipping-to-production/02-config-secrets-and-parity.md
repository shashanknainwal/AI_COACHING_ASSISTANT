---
title: "Config, Secrets and Environment Parity"
type: reading
minutes: 3
---

> **By the end of this lesson you will be able to:**
> - Keep config and secrets out of code so one build runs everywhere
> - Validate config at startup and report every problem at once
> - Keep staging close enough to prod to predict it

Brightway's platform team will deploy your triage service to three environments, and their security team will ask where the API key lives. Get this right and the deploy is boring.

## One build, many environments

Settings that vary by environment live in the environment, not the code (the "twelve-factor app" rule):

```
APP_ENV=prod
TRIAGE_MODEL=claude-sonnet-5-5
MAX_TOKENS=1024
REQUEST_TIMEOUT_S=30
ENABLE_AUTO_CREDIT=false
ANTHROPIC_API_KEY=(injected from the secrets manager)
```

Config holds credentials, hosts, model names, limits and flags. Code holds logic, schemas and **prompts**: a prompt change goes through review, evals (Module 8) and the release gate, never a live dashboard edit.

## Secrets

- **Never in code or git.** Scanners find leaked keys within minutes; add secret scanning to CI.
- **Secrets manager**, injected at runtime as env vars or files.
- **Never logged** (log `****7f3a` to confirm which key) and **never pasted** into chat, tickets or email; share access to the manager instead.
- **Rotate** with two valid keys during the switch; **scope per environment** so a dev key can't touch prod.

If one leaks, **revoke it first**, then investigate.

## Validate at startup: fail fast, fail completely

- **Fail fast.** Refuse to start on any bad setting. A failed deploy is caught at once; a 3 a.m. crash on the first request that reads the bad value is an incident.
- **Fail completely.** Report **every** problem at once. One error per 20-minute deploy cycle wastes an afternoon.

| Pitfall | Example | Handle it by |
|---|---|---|
| Whitespace | Secret file ends with `\n` | Strip values |
| Empty strings | `MAX_TOKENS=` | Treat as "not set" |
| Booleans | `bool("false")` is `True` (non-empty string) | Parse `true/false/1/0/yes/no` explicitly, reject the rest |
| Typos in numbers | `MAX_TOKENS=2O48` (letter O) | Parse and report |
| Allowed values | `claude-sonnet` without a version | Check against a list |
| Cross-field rules | Debug logging or wildcard CORS in prod | Prod-only checks |

## Environment parity

Staging predicts prod only if it matches: same image, database version, network and proxy, Claude platform and model, similar rate limits, and realistic data (anonymized samples, with approval). Ten tidy tickets won't show what 4,000 messy ones will. Write down the gaps you can't close.

> **Key takeaways**
> - Environment-specific settings go in env vars; one image runs everywhere; prompts are reviewed like code.
> - Secrets live in a secrets manager, never in code, logs or chat; rotate, scope per environment, revoke first.
> - Validate all config at startup and report every problem at once.
> - Keep staging close to prod and document the gaps.
