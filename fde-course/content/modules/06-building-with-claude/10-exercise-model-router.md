---
title: "Exercise: Route Requests to the Right Model"
type: exercise
minutes: 30
hints:
  - "`choose`: start with `route = dict(ROUTES[task])` (a copy, so you never modify the table). Raise `ValueError(f\"unknown task: {task}\")` if the task isn't there."
  - "The fast path: `if task == \"classify\" and latency_budget_ms is not None and latency_budget_ms < 1000:` replace the route with `{\"model\": FAST_MODEL, \"effort\": \"low\", \"max_tokens\": 2048}`."
  - "Context check: every model here has a 1M window, so one rule covers it: `if input_tokens > CONTEXT_LIMITS[route[\"model\"]]: raise ValueError(\"input too large\")`."
  - "`build_params`: only add `output_config` when `route[\"effort\"] is not None`. `None` means 'use the model's default', which is `high` on Sonnet 5.5 and `medium` on Opus 5.5 and Haiku 5.5."
  - "`estimate_cost`: if the price entry has `long_above` and `input_tokens > p[\"long_above\"]`, use `long_input` and `long_output` for the whole request. `run`: wrap the create call in `try/except (anthropic.OverloadedError, anthropic.InternalServerError)`; if `FALLBACK[model]` is None, re-raise with a bare `raise`."
---

Harbor Bank's assistant handles very different requests. You'll build the router that picks the model, effort and output size per task, respects latency budgets and context limits, builds valid parameters for each model, estimates cost, and falls back when a model is overloaded.

## Your task

**1. `choose(task, input_tokens, latency_budget_ms=None)`** returns a route dict `{"model", "effort", "max_tokens"}`:
- Start from a **copy** of `ROUTES[task]`; unknown tasks raise `ValueError("unknown task: <task>")`.
- **Fast path:** for `"classify"` with a latency budget under 1000 ms, use `{"model": FAST_MODEL, "effort": "low", "max_tokens": 2048}`. `FAST_MODEL` is Claude Haiku 5.5: $0.10/$0.50 per million tokens for prompts up to 100K, 20 times cheaper than Sonnet 5.5. It supports `effort` and thinks by default, so set `low` explicitly and leave `max_tokens` room for the thinking.
- **Context limit:** if `input_tokens` exceeds `CONTEXT_LIMITS` for the chosen model, raise `ValueError("input too large")`. All three current models accept 1 million tokens. (The legacy Haiku 4.5 had a 200K window; that is no longer a reason to reroute.)

**2. `build_params(route, system, user_text)`** returns the keyword arguments for `messages.create`: `model`, `max_tokens`, `system`, `messages` (one user turn), plus `output_config={"effort": ...}` **only when the route sets an effort**. An effort of `None` means "use the model's default".

**3. `estimate_cost(route, input_tokens, output_tokens)`** returns the dollar cost (rounded to 6 decimals) using `PRICES[route["model"]]`. `output_tokens` includes thinking tokens, which bill as output. Haiku 5.5 has two rate cards: when the prompt is **over** 100,000 tokens (`long_above`), the whole request bills at `long_input` / `long_output` ($0.50/$2.50).

**4. `run(client, task, system, user_text, input_tokens, latency_budget_ms=None)`** chooses a route, calls `client.messages.create(**build_params(...))`, and returns `{"text": ..., "model": <model that answered>, "fallback_used": False}`. If the call raises `anthropic.OverloadedError` or `anthropic.InternalServerError` (after the SDK's own retries), retry **once** on `FALLBACK[model]` and return with `fallback_used: True`. If there's no fallback, re-raise.

## Example

`estimate_cost({"model": "claude-haiku-5-5", ...}, 300, 200)` is `0.00013`. The same call with a 150,000-token prompt is `0.0755`: the long-prompt rate applies to every token, not only the ones above 100K.

Press **Run** to route four requests, then **Submit**.
