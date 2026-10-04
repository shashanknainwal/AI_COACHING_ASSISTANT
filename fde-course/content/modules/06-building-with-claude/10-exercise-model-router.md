---
title: "Exercise: Route Requests to the Right Model"
type: exercise
minutes: 30
hints:
  - "`choose`: start with `route = dict(ROUTES[task])` (a copy, so you never modify the table). Raise `ValueError(f\"unknown task: {task}\")` if the task isn't there."
  - "The fast path: `if task == \"classify\" and latency_budget_ms is not None and latency_budget_ms < 1000:` replace the route with `{\"model\": FAST_MODEL, \"effort\": None, \"max_tokens\": 1024}`."
  - "Context check: if `input_tokens > CONTEXT_LIMITS[route[\"model\"]]` and the model is `FAST_MODEL`, switch to `claude-sonnet-5-5` with effort `low`. If it's still too large, raise `ValueError(\"input too large\")`."
  - "`build_params`: only add `output_config` when `route[\"effort\"] is not None`. Haiku rejects the effort parameter."
  - "`run`: wrap the create call in `try/except (anthropic.OverloadedError, anthropic.InternalServerError)`. On failure, look up `FALLBACK[model]`; if it's None, re-raise with a bare `raise`."
---

Harbor Bank's assistant handles very different requests. You'll build the router that picks the model, effort and output size per task, respects latency budgets and context limits, builds valid parameters for each model, estimates cost, and falls back when a model is overloaded.

## Your task

**1. `choose(task, input_tokens, latency_budget_ms=None)`** returns a route dict `{"model", "effort", "max_tokens"}`:
- Start from a **copy** of `ROUTES[task]`; unknown tasks raise `ValueError("unknown task: <task>")`.
- **Fast path:** for `"classify"` with a latency budget under 1000 ms, use `{"model": FAST_MODEL, "effort": None, "max_tokens": 1024}`.
- **Context limit:** if `input_tokens` exceeds `CONTEXT_LIMITS` for the chosen model and that model is `FAST_MODEL`, switch to `"claude-sonnet-5-5"` with effort `"low"` (keep `max_tokens`). If the input still exceeds the chosen model's limit, raise `ValueError("input too large")`.

**2. `build_params(route, system, user_text)`** returns the keyword arguments for `messages.create`: `model`, `max_tokens`, `system`, `messages` (one user turn), plus `output_config={"effort": ...}` **only when the route has an effort**.

**3. `estimate_cost(route, input_tokens, output_tokens)`** returns the dollar cost (rounded to 6 decimals) using `PRICES[route["model"]]`.

**4. `run(client, task, system, user_text, input_tokens, latency_budget_ms=None)`** chooses a route, calls `client.messages.create(**build_params(...))`, and returns `{"text": ..., "model": <model that answered>, "fallback_used": False}`. If the call raises `anthropic.OverloadedError` or `anthropic.InternalServerError` (after the SDK's own retries), retry **once** on `FALLBACK[model]` and return with `fallback_used: True`. If there's no fallback, re-raise.

Press **Run** to route four requests, then **Submit**.
