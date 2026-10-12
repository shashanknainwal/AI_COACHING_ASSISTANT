"""One function for single-shot calls (classify, extract, judge), with the
checks every production call needs.

- `effort` is always sent explicitly.
- The stable system prompt carries a cache breakpoint, so repeated calls can
  read it from the cache once it is at least 512 tokens long.
- `stop_reason` is checked before anything is parsed: `refusal`, `max_tokens`
  and `model_context_window_exceeded` never reach `json.loads`.
- Usage, cost, latency and the request id are recorded for every call.

The SDK is imported lazily so the pure parts of this kit (and its tests) run
without `anthropic` installed and without a key.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any

from app import config
from app.costs import CostMeter, cost_usd, usage_to_dict


def get_client():
    """Create a client from ANTHROPIC_API_KEY in the environment. Never hardcode a key."""
    import anthropic  # lazy: tests use fake clients

    return anthropic.Anthropic(max_retries=3)


@dataclass
class CallResult:
    model: str
    effort: str
    stop_reason: str | None
    text: str = ""
    parsed: Any = None
    usage: dict = field(default_factory=dict)
    cost_usd: float = 0.0
    latency_s: float = 0.0
    request_id: str | None = None
    refusal_category: str | None = None
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None and self.stop_reason in ("end_turn", "stop_sequence")

    @property
    def refused(self) -> bool:
        return self.stop_reason == "refusal"


def system_blocks(system: str, cache: bool = True) -> list[dict]:
    """The system prompt as one text block with a cache breakpoint.

    Put the breakpoint at the end of the shared part of the prompt (here, the
    whole system prompt) and the per-request text in `messages`. Do not use
    top-level automatic caching for one-shot calls whose last block changes
    every time: each call would write a new cache entry that is never read.
    """
    block: dict = {"type": "text", "text": system}
    if cache:
        block["cache_control"] = {"type": "ephemeral"}
    return [block]


def call(
    client,
    *,
    system: str,
    user: str,
    model: str = config.DEFAULT_MODEL,
    effort: str = config.DEFAULT_EFFORT,
    max_tokens: int = 4096,
    schema: dict | None = None,
    meter: CostMeter | None = None,
) -> CallResult:
    """Make one call and return a CallResult. Never raises on a bad stop_reason.

    `max_tokens` covers thinking as well as the answer, so leave room: a
    classification that needs 50 tokens of JSON can still think for 1,000.
    """
    if effort not in config.EFFORT_LEVELS:
        raise ValueError(f"effort must be one of {config.EFFORT_LEVELS}")
    output_config: dict = {"effort": effort}
    if schema is not None:
        output_config["format"] = {"type": "json_schema", "schema": schema}

    started = time.perf_counter()
    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_blocks(system),
            messages=[{"role": "user", "content": user}],
            output_config=output_config,
        )
    except Exception as exc:  # network, auth, 4xx/5xx after SDK retries
        return CallResult(model=model, effort=effort, stop_reason=None,
                          latency_s=time.perf_counter() - started,
                          error=f"{type(exc).__name__}: {exc}")
    latency = time.perf_counter() - started

    usage = usage_to_dict(getattr(response, "usage", None))
    result = CallResult(
        model=model,
        effort=effort,
        stop_reason=getattr(response, "stop_reason", None),
        usage=usage,
        cost_usd=cost_usd(model, usage),
        latency_s=latency,
        request_id=getattr(response, "_request_id", None),
    )
    if meter is not None:
        meter.add(model, usage)  # may raise BudgetExceeded, on purpose

    texts = [b.text for b in getattr(response, "content", []) if getattr(b, "type", None) == "text"]
    result.text = "".join(texts)

    if result.stop_reason == "refusal":
        details = getattr(response, "stop_details", None)
        result.refusal_category = getattr(details, "category", None) if details else None
        result.error = "refusal"
        return result
    if result.stop_reason == "max_tokens":
        result.error = "max_tokens: output (including thinking) hit the limit; raise max_tokens or lower effort"
        return result
    if result.stop_reason == "model_context_window_exceeded":
        result.error = "context window exceeded"
        return result

    if schema is not None:
        try:
            result.parsed = json.loads(result.text)
        except json.JSONDecodeError as exc:
            result.error = f"invalid JSON: {exc}"
    return result
