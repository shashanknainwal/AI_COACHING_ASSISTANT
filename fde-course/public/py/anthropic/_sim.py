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

calls = []       # every request attempt: {"params": {...}, "attempt": n, "stream": bool}
_queue = []
_responder = None
_cache = set()   # prompt-cache prefixes written so far
CACHE_MIN_TOKENS = 512  # current models (Opus 5.5, Sonnet 5.5, Haiku 5.5, ...)
# Older models with a higher minimum cacheable prefix (from the prompt-caching docs).
CACHE_MIN_TOKENS_BY_MODEL = {
    "claude-haiku-4-5": 4096,
    "claude-opus-4-6": 4096,
    "claude-opus-4-5": 4096,
    "claude-opus-4-7": 2048,
    "claude-opus-4-8": 1024,
    "claude-sonnet-5": 1024,
    "claude-sonnet-4-6": 1024,
    "claude-sonnet-4-5": 1024,
}


def _cache_min_tokens(model):
    return CACHE_MIN_TOKENS_BY_MODEL.get(str(model), CACHE_MIN_TOKENS)


def reset():
    global _responder
    calls.clear()
    _queue.clear()
    _cache.clear()
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


def last_tool_results(params):
    """{tool_use_id: content} from the newest user message, for scripting multi-step replies."""
    content = params["messages"][-1].get("content")
    if not isinstance(content, list):
        return {}
    out = {}
    for b in content:
        if isinstance(b, dict) and b.get("type") == "tool_result":
            out[b["tool_use_id"]] = b.get("content")
    return out


def tool_calls_so_far(params):
    """Names of every tool Claude has called earlier in this conversation."""
    names = []
    for m in params["messages"]:
        if m.get("role") == "assistant" and isinstance(m.get("content"), list):
            for b in m["content"]:
                if (b.get("type") if isinstance(b, dict) else getattr(b, "type", None)) == "tool_use":
                    names.append(b.get("name") if isinstance(b, dict) else b.name)
    return names


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


def rate_limit(retry_after=None):
    headers = {"retry-after": str(retry_after)} if retry_after is not None else None
    return RateLimitError("Error code: 429 - rate_limit_error", headers=headers)


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

def _record(params, attempt, stream=False):
    calls.append({"params": _snapshot(params), "attempt": attempt, "stream": stream})


def _record_response(response):
    """Attach a compact copy of the reply to the latest call (used by the trace viewer)."""
    if not calls:
        return
    blocks = []
    for b in response.content:
        if b.type == "text":
            blocks.append({"type": "text", "text": b.text})
        elif b.type == "tool_use":
            blocks.append({"type": "tool_use", "id": b.id, "name": b.name, "input": _jsonable(b.input) if not isinstance(b.input, dict) else b.input})
        elif b.type == "thinking":
            blocks.append({"type": "thinking"})
    u = response.usage
    calls[-1]["response"] = {
        "stop_reason": response.stop_reason,
        "blocks": blocks,
        "usage": {"input": u.input_tokens, "output": u.output_tokens,
                  "cache_read": u.cache_read_input_tokens, "cache_write": u.cache_creation_input_tokens},
    }


def _record_error(exc):
    if calls:
        calls[-1]["error"] = type(exc).__name__


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


def _cache_prefix(params):
    """The cached prefix (as text) for this request, or None if caching isn't requested."""
    system = params.get("system")
    tools = params.get("tools", [])
    if params.get("cache_control"):
        # Automatic caching: everything up to the last cacheable block (here, all but the newest message).
        return json.dumps([tools, system, params["messages"][:-1]], default=_jsonable, sort_keys=True)
    if isinstance(system, list):
        marked = [i for i, b in enumerate(system) if isinstance(b, dict) and b.get("cache_control")]
        if marked:
            return json.dumps([tools, system[: marked[-1] + 1]], default=_jsonable, sort_keys=True)
    return None


def _cache_usage(params):
    prefix = _cache_prefix(params)
    if prefix is None:
        return 0, 0
    tokens = len(prefix) // 4
    if tokens < _cache_min_tokens(params.get("model")):
        return 0, 0          # too short to cache: silently not cached, like the real API
    key = (params["model"], prefix)
    if key in _cache:
        return 0, tokens
    _cache.add(key)
    return tokens, 0


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

    total_in = estimate_input_tokens(params)
    written, read = _cache_usage(params)
    usage = Usage(input_tokens=max(1, total_in - written - read), output_tokens=output_tokens,
                  cache_creation_input_tokens=written, cache_read_input_tokens=read)
    return Message(blocks, model=params["model"], stop_reason=stop_reason, usage=usage, stop_details=stop_details)


__all__ = [
    "calls", "reset", "queue", "set_responder", "requests", "last_request",
    "text", "thinking", "tool_use", "message", "rate_limit", "server_error", "overloaded",
    "connection_error", "refusal", "APIStatusError",
]
