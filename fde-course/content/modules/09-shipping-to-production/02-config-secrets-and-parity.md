---
title: "Config, Secrets and Environment Parity"
type: reading
minutes: 14
---

> **By the end of this lesson you will be able to:**
> - Separate code from configuration so one build runs in every environment
> - Handle secrets so they never end up in code, logs or chat messages
> - Validate configuration at startup and fail fast with a complete error report
> - Keep dev, staging and prod similar enough that staging actually predicts prod

## One build, many environments

The rule from the widely used "twelve-factor app" approach: **configuration that varies between environments lives in the environment, not in the code.** The same container image runs in dev, staging and prod; only environment variables differ:

```
APP_ENV=prod
TRIAGE_MODEL=claude-sonnet-5-5
MAX_TOKENS=1024
REQUEST_TIMEOUT_S=30
ENABLE_AUTO_CREDIT=false
ANTHROPIC_API_KEY=(injected from the secrets manager)
```

What belongs in config: credentials, hostnames and URLs, model names, limits and timeouts, feature flags. What stays in code: logic, prompts (version them like code, reviewed in pull requests), schemas.

Prompts deserve a note. They change behavior as much as code does, so treat a prompt change like a code change: review, evals (Module 8), release gate, deploy. Don't let them be edited live in a config dashboard without that process.

## Secrets

A secret is anything that grants access: API keys, database passwords, signing keys, OAuth client secrets.

- **Never in code or git.** Not even in a "temporary" commit: git history is forever, and leaked keys are found by automated scanners within minutes. Add secret scanning to CI.
- **Store them in a secrets manager** and inject them at runtime as environment variables or mounted files.
- **Never log them.** Log a redacted form (`****7f3a`) when you need to confirm which key is in use.
- **Never paste them into chat, tickets or emails,** including to the customer's own team. Share access to the secrets manager instead.
- **Rotate them:** support two valid keys during a rotation, so you can switch without downtime.
- **Least privilege:** separate keys per environment, so a leaked dev key can't touch prod. Per-service keys also make usage easier to track.

If a secret leaks: revoke it first, then investigate. Revoking takes a minute; an investigation takes days.

## Validate at startup: fail fast, fail completely

Configuration bugs are among the most common causes of production incidents: a typo in a variable name, `MAX_TOKENS=2O48` with a letter O, a missing key in the new region. Two principles:

- **Fail fast.** Validate every setting when the service starts and refuse to start if anything is wrong. A service that won't start during a deploy is caught immediately; one that crashes at 3 a.m. on the first request that reads the bad value is an incident.
- **Fail completely.** Report **every** problem at once. Fixing one error per deploy cycle, with each cycle taking 20 minutes, wastes an afternoon.

Common pitfalls a loader should handle:

- **Whitespace:** secrets read from files often end with a newline.
- **Empty strings:** `MAX_TOKENS=` usually means "not set," not "empty."
- **Booleans:** `"false"` is a non-empty string, so it's truthy in Python. Parse `true/false/1/0/yes/no` explicitly.
- **Allowed values:** check model names against a list, so `claude-sonnet` (missing the version) fails at startup instead of on the first API call.
- **Cross-field rules:** some combinations are invalid only in prod (debug logging, wildcard CORS origins).

## Environment parity

Staging is only useful if it predicts prod. Keep them as similar as you can:

- **Same image and same deployment method** (only config differs).
- **Same dependencies:** same database engine and version, same network setup (including the proxy!), same Claude platform and model.
- **Realistic data:** a staging environment with ten tidy test tickets won't reveal what 4,000 messy real ones will. Use anonymized production samples, with the customer's approval.
- **Same limits:** if prod has rate limits or quotas, staging should hit similar ones in load tests.

Differences you can't avoid (smaller scale, synthetic users) should be written down, so nobody assumes staging proved something it couldn't.

> **Key takeaways**
> - Keep environment-specific settings in environment variables; one image runs everywhere; prompts are versioned and reviewed like code.
> - Secrets live in a secrets manager, never in code, logs or chat; rotate them, scope them per environment, and revoke first when they leak.
> - Validate all configuration at startup and report every problem at once; handle whitespace, empty values, booleans, allowed values and prod-only rules.
> - Keep staging close to prod (same image, dependencies, network and realistic data) and write down the differences.
