---
title: "Exercise: A Fail-Fast Config Loader"
type: exercise
minutes: 30
hints:
  - "`parse_value`: convert by `spec[\"type\"]` inside `try/except ValueError`, re-raising with the course's message. Return bools and lists right away; check `choices` and `min`/`max` for the rest."
  - "Format choices with `', '.join(spec['choices'])` and use `{raw!r}` to quote the raw value (`'abc'`). The range message uses the raw value without quotes."
  - "`load_config`: loop over `settings.items()`, read `env.get(name, \"\").strip()`, and append problems to an `errors` list instead of raising straight away."
  - "Run the prod rules after the loop using the parsed values (`config.get(\"log_level\")`), then `raise ConfigError(errors)` if the list isn't empty."
  - "`redacted`: look up `settings.get(key.upper(), {}).get(\"secret\")`; for secrets use `\"****\" + value[-4:]` when `len(value) >= 12`, otherwise `\"****\"`."
---

Brightway's assistant now runs in three environments (dev, staging, prod) inside Brightway's cloud account. All settings come from environment variables, filled from their secrets manager. Last week a staging deploy started with `MAX_TOKENS=2O48` (a letter O) and failed hours later, in the middle of the night. You'll write the loader that makes that impossible: **validate everything at startup, report every problem at once, and never log a secret.**

`SETTINGS` (the spec for every variable) and `ConfigError` (which takes a list of error strings) are given.

## Your task

**1. `parse_value(name, raw, spec)`** converts one raw string by `spec["type"]` and checks it. Raise `ValueError` with exactly these messages:

| Type / check | Accepts | Error message |
|---|---|---|
| `int` | `int(raw)` | `MAX_TOKENS must be an integer, got 'abc'` |
| `float` | `float(raw)` | `TIMEOUT must be a number, got 'fast'` |
| `bool` | `true/1/yes/on`, `false/0/no/off` (any case) | `FLAG must be true or false, got 'maybe'` |
| `list` | comma-separated; strip items, drop empty ones | (never fails) |
| `str` | anything | |
| `choices` | value in the list | `APP_ENV must be one of dev, prod, got 'production'` |
| `min`/`max` | inclusive range | `MAX_TOKENS must be between 1 and 100, got 0` |

**2. `load_config(env, settings=SETTINGS)`** returns `{lowercase_name: value}` for every setting:
- Strip whitespace from raw values (secrets files often end with a newline). An **empty** value counts as missing.
- Missing and `required` → error `"<NAME> is required"`. Missing and optional → use the `default`.
- Collect **every** error (in `SETTINGS` order), then apply the prod rules:
  - `"LOG_LEVEL must not be DEBUG when APP_ENV is prod"`
  - `"ALLOWED_ORIGINS must not contain * when APP_ENV is prod"`
- If there are any errors, `raise ConfigError(errors)`.

**3. `redacted(config, settings=SETTINGS)`** returns a copy that's safe to log. Secret values become `"****"` plus their last 4 characters, or just `"****"` if the secret is shorter than 12 characters.

Press **Run** to load a staging config and see a broken prod config's full error report, then **Submit**.
