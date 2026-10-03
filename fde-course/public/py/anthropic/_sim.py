"""Scripted replies for the simulated SDK.

Exercises configure this from a hidden setup file, for example:

    from anthropic import _sim
    _sim.queue(_sim.text("Here is the summary..."))
    _sim.queue(_sim.rate_limit())            # next call raises RateLimitError
    _sim.set_responder(lambda params: ...)   # or compute a reply from the request

Tests then inspect `_sim.calls` to check what the learner sent.
"""

import json

from ._types import Message, TextBlock, ThinkingBlock, ToolUseBlock, Usage
from ._errors import (
    APIConnectionError,
    APIStatusError,
    InternalServerError,
    OverloadedError,
    RateLimitError,
)

STRICT_NO_PREFILL = True
NO_FORCED_TOOL_MODELS = {"claude-opus-5-5", "claude-sonnet-5-5", "claude-fable-5-1"}

calls = []       # every request attempt: {"params": {...}, "attempt": n}
_queue = []
_responder = None


def reset():
    global _responder
    calls.clear()
    _queue.clear()
    _responder = None


def queue(*replies):
    """Queue replies (Message, list of blocks, str, or an exception) in order."""
    _queue.extend(replies)


def set_responder(fn):
    """fn(params) -> Message | list[block] | str | Exception. Used when the queue is empty."""
    global _responder
    _responder = fn


def requests():
    """Params of each attempt, oldest first."""
    return [c["params"] for c in calls]


def last_request():
    return calls[-1]["params"] if calls else None


# ---- reply builders -------------------------------------------------------

def text(s):
    return TextBlock(s)


def thinking(s=""):
    """A thinking block. Opus 5.5 returns these with empty text by default."""
    return ThinkingBlock(s)


def tool_use(name, input, id=None):
    return ToolUseBlock(name, input, id=id)


def message(*blocks, stop_reason=None):
    blocks = list(blocks)
    if stop_reason is None:
        stop_reason = "tool_use" if any(b.type == "tool_use" for b in blocks) else "end_turn"
    return {"__sim_message__": True, "blocks": blocks, "stop_reason": stop_reason}


def rate_limit():
    return RateLimitError("Error code: 429 - rate_limit_error")


def server_error():
    return InternalServerError("Error code: 500 - api_error")


def overloaded():
    return OverloadedError("Error code: 529 - overloaded_error")


def connection_error():
    return APIConnectionError()


def refusal(category="cyber"):
    return {"__sim_message__": True, "blocks": [], "stop_reason": "refusal",
            "stop_details": {"type": "refusal", "category": category, "explanation": "Declined by safety classifier."}}


# ---- internals ------------------------------------------------------------

def _record(params, attempt):
    calls.append({"params": _snapshot(params), "attempt": attempt})


def _snapshot(params):
    # Copy so later mutation of the learner's list doesn't rewrite history.
    try:
        return json.loads(json.dumps(params, default=_jsonable))
    except (TypeError, ValueError):
        return dict(params)


def _jsonable(o):
    if hasattr(o, "model_dump"):
        return o.model_dump()
    return repr(o)


def estimate_input_tokens(params):
    raw = json.dumps(params.get("messages", []), default=_jsonable)
    raw += json.dumps(params.get("system", ""), default=_jsonable)
    raw += json.dumps(params.get("tools", []), default=_jsonable)
    return max(1, len(raw) // 4)


def _last_user_text(params):
    content = params["messages"][-1].get("content", "")
    if isinstance(content, list):
        content = " ".join(b.get("text", "") for b in content if isinstance(b, dict))
    return str(content)


def _example_from_schema(node):
    """A minimal value matching a JSON Schema, used when no reply is scripted."""
    if not isinstance(node, dict):
        return None
    if "enum" in node:
        return node["enum"][0]
    t = node.get("type")
    if isinstance(t, list):
        t = next((x for x in t if x != "null"), "null")
    if t == "object":
        return {k: _example_from_schema(v) for k, v in node.get("properties", {}).items()}
    if t == "array":
        return [_example_from_schema(node.get("items", {}))]
    return {"string": "example", "integer": 0, "number": 0, "boolean": False}.get(t)


def _default_reply(params):
    fmt = (params.get("output_config") or {}).get("format")
    if fmt and fmt.get("type") == "json_schema":
        return json.dumps(_example_from_schema(fmt["schema"]))
    said = " ".join(_last_user_text(params).split())
    if len(said) > 80:
        said = said[:77] + "..."
    reply = TextBlock(
        f'[Simulated Claude] You said: "{said}". '
        "This offline simulator returns scripted replies; in exercises the replies are set up for you. "
        "The same code works against the real API."
    )
    # Opus 5.5 always runs adaptive thinking, so responses often lead with a thinking block.
    blocks = [ThinkingBlock(""), reply] if params["model"] in NO_FORCED_TOOL_MODELS else [reply]
    return {"__sim_message__": True, "blocks": blocks, "stop_reason": "end_turn"}


def _respond(params):
    if _queue:
        reply = _queue.pop(0)
    elif _responder is not None:
        reply = _responder(params)
    else:
        reply = _default_reply(params)

    if isinstance(reply, BaseException):
        raise reply

    stop_details = None
    if isinstance(reply, str):
        blocks, stop_reason = [TextBlock(reply)], "end_turn"
    elif isinstance(reply, Message):
        return reply
    elif isinstance(reply, dict) and reply.get("__sim_message__"):
        blocks, stop_reason = reply["blocks"], reply["stop_reason"]
        stop_details = reply.get("stop_details")
    elif isinstance(reply, list):
        blocks = reply
        stop_reason = "tool_use" if any(b.type == "tool_use" for b in blocks) else "end_turn"
    else:
        raise TypeError(f"Unsupported simulated reply: {reply!r}")

    out_chars = sum(
        len(b.text) if b.type == "text" else len(json.dumps(b.input)) if b.type == "tool_use" else 0
        for b in blocks
    )
    output_tokens = max(1, out_chars // 4)
    if stop_reason == "end_turn" and output_tokens > params["max_tokens"]:
        # Truncate like the real API does when max_tokens is too small.
        keep = params["max_tokens"] * 4
        blocks = [TextBlock(b.text[:keep]) if b.type == "text" else b for b in blocks]
        stop_reason, output_tokens = "max_tokens", params["max_tokens"]

    usage = Usage(input_tokens=estimate_input_tokens(params), output_tokens=output_tokens)
    return Message(blocks, model=params["model"], stop_reason=stop_reason, usage=usage, stop_details=stop_details)


__all__ = [
    "calls", "reset", "queue", "set_responder", "requests", "last_request",
    "text", "thinking", "tool_use", "message", "rate_limit", "server_error", "overloaded",
    "connection_error", "refusal", "APIStatusError",
]
