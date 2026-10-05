"""In-browser simulator of the official `anthropic` Python SDK.

It mirrors the real SDK's surface for the calls this course teaches
(`Anthropic().messages.create`, typed content blocks, `stop_reason`, `usage`,
typed errors and automatic retries), so code written here runs unchanged
against the real API once you `pip install anthropic` and set ANTHROPIC_API_KEY.

No network calls are made. Responses come from `anthropic._sim`, which each
exercise configures with scripted replies.
"""

import time

from . import _sim
from ._types import (
    StopDetails,
    Message,
    TextBlock,
    ToolUseBlock,
    ThinkingBlock,
    Usage,
)
from ._errors import (
    AnthropicError,
    APIError,
    APIStatusError,
    APIConnectionError,
    APITimeoutError,
    BadRequestError,
    AuthenticationError,
    PermissionDeniedError,
    NotFoundError,
    RateLimitError,
    InternalServerError,
    OverloadedError,
)

__all__ = [
    "Anthropic",
    "Message",
    "TextBlock",
    "ToolUseBlock",
    "ThinkingBlock",
    "Usage",
    "AnthropicError",
    "APIError",
    "APIStatusError",
    "APIConnectionError",
    "APITimeoutError",
    "BadRequestError",
    "AuthenticationError",
    "PermissionDeniedError",
    "NotFoundError",
    "RateLimitError",
    "InternalServerError",
    "OverloadedError",
]

_RETRYABLE = (RateLimitError, InternalServerError, OverloadedError, APIConnectionError)


class _Messages:
    def __init__(self, client):
        self._client = client

    def create(self, **params):
        if params.pop("stream", False):
            raise BadRequestError("The simulator supports streaming through client.messages.stream(...)")
        return self._send(params, stream=False)

    def _send(self, params, stream):
        _validate(params)
        attempts = self._client.max_retries + 1
        for attempt in range(attempts):
            _sim._record(params, attempt, stream=stream)
            try:
                response = _sim._respond(params)
                _sim._record_response(response)
                return response
            except _RETRYABLE as exc:
                _sim._record_error(exc)
                if attempt == attempts - 1:
                    raise
                # Like the real SDK: honor retry-after when present, otherwise back off exponentially.
                retry_after = getattr(getattr(exc, "response", None), "headers", {}).get("retry-after")
                time.sleep(float(retry_after) if retry_after else min(8.0, 0.5 * 2 ** attempt))

    def stream(self, **params):
        return MessageStream(self, params)

    def count_tokens(self, **params):
        if "model" not in params or "messages" not in params:
            raise BadRequestError("count_tokens requires model and messages")
        return _types_count(params)


def _types_count(params):
    class _Count:
        def __init__(self, n):
            self.input_tokens = n

        def __repr__(self):
            return f"MessageTokensCount(input_tokens={self.input_tokens})"

    return _Count(_sim.estimate_input_tokens(params))


class _Event:
    def __init__(self, type, **fields):
        self.type = type
        for k, v in fields.items():
            setattr(self, k, v)

    def __repr__(self):
        return f"<Event {self.type}>"


def _chunks(text, words=3):
    parts = text.split(" ")
    for i in range(0, len(parts), words):
        piece = " ".join(parts[i:i + words])
        yield piece if i + words >= len(parts) else piece + " "


class MessageStream:
    """Simulated `client.messages.stream(...)` context manager."""

    def __init__(self, messages, params):
        self._messages = messages
        self._params = params
        self._final = None

    def __enter__(self):
        self._final = self._messages._send(self._params, stream=True)
        return self

    def __exit__(self, *exc):
        return False

    def __iter__(self):
        yield _Event("message_start", message=self._final)
        for index, block in enumerate(self._final.content):
            yield _Event("content_block_start", index=index, content_block=block)
            if block.type == "text":
                for piece in _chunks(block.text):
                    yield _Event("content_block_delta", index=index, delta=_Event("text_delta", text=piece))
            elif block.type == "thinking":
                yield _Event("content_block_delta", index=index, delta=_Event("thinking_delta", thinking=block.thinking))
            yield _Event("content_block_stop", index=index)
        yield _Event("message_stop")

    @property
    def text_stream(self):
        for event in self:
            if event.type == "content_block_delta" and event.delta.type == "text_delta":
                yield event.delta.text

    def get_final_message(self):
        return self._final

    def get_final_text(self):
        return "".join(b.text for b in self._final.content if b.type == "text")


class Anthropic:
    def __init__(self, api_key=None, max_retries=2, timeout=600.0, base_url=None, **_ignored):
        self.api_key = api_key
        self.max_retries = max_retries
        self.timeout = timeout
        self.base_url = base_url or "https://api.anthropic.com"
        self.messages = _Messages(self)

    def with_options(self, max_retries=None, timeout=None, **_ignored):
        clone = Anthropic(
            api_key=self.api_key,
            max_retries=self.max_retries if max_retries is None else max_retries,
            timeout=self.timeout if timeout is None else timeout,
            base_url=self.base_url,
        )
        return clone


def _validate(params):
    for key in ("model", "max_tokens", "messages"):
        if key not in params:
            raise BadRequestError(f"{key}: Field required")
    if not isinstance(params["max_tokens"], int) or params["max_tokens"] < 1:
        raise BadRequestError("max_tokens: must be a positive integer")
    messages = params["messages"]
    if not isinstance(messages, list) or not messages:
        raise BadRequestError("messages: must be a non-empty list")
    for i, m in enumerate(messages):
        if not isinstance(m, dict) or "role" not in m or "content" not in m:
            raise BadRequestError(f"messages.{i}: each message needs 'role' and 'content'")
        if m["role"] not in ("user", "assistant", "system"):
            raise BadRequestError(f"messages.{i}.role: must be 'user' or 'assistant'")
    if messages[0]["role"] != "user":
        raise BadRequestError("messages.0.role: the first message must use the 'user' role")
    if messages[-1]["role"] == "assistant" and _sim.STRICT_NO_PREFILL:
        raise BadRequestError(
            "This model does not support assistant message prefill. "
            "The conversation must end with a user message."
        )
    if "temperature" in params and params["model"].startswith(("claude-opus-5", "claude-sonnet-5", "claude-fable")):
        raise BadRequestError("temperature: sampling parameters are not supported on this model")
    if "tools" in params:
        _validate_tools(params["tools"])
    _validate_tool_results(messages)
    if "output_config" in params:
        _validate_output_config(params["output_config"])
        if "effort" in params["output_config"] and params["model"].startswith("claude-haiku-4-5"):
            raise BadRequestError("output_config.effort: effort is not supported on this model")
    tc = params.get("tool_choice")
    if isinstance(tc, dict) and tc.get("type") in ("any", "tool") and params["model"] in _sim.NO_FORCED_TOOL_MODELS:
        raise BadRequestError('tool_choice: type "tool" and "any" are not supported for this model.')


_EFFORTS = ("low", "medium", "high", "xhigh", "max")


def _validate_output_config(cfg):
    if not isinstance(cfg, dict):
        raise BadRequestError("output_config: must be an object")
    unknown = set(cfg) - {"format", "effort", "task_budget"}
    if unknown:
        raise BadRequestError(f"output_config: unexpected field(s) {sorted(unknown)}")
    if "effort" in cfg and cfg["effort"] not in _EFFORTS:
        raise BadRequestError(f"output_config.effort: must be one of {list(_EFFORTS)}")
    fmt = cfg.get("format")
    if fmt is None:
        return
    if not isinstance(fmt, dict) or fmt.get("type") != "json_schema":
        raise BadRequestError('output_config.format.type: must be "json_schema"')
    schema = fmt.get("schema")
    if not isinstance(schema, dict):
        raise BadRequestError("output_config.format.schema: must be a JSON Schema object")
    _check_schema(schema, "output_config.format.schema")


def _check_schema(node, path):
    """Structured outputs require every object to list its properties and forbid extras."""
    if not isinstance(node, dict):
        return
    t = node.get("type")
    if t == "object" or (isinstance(t, list) and "object" in t):
        if node.get("additionalProperties") is not False:
            raise BadRequestError(f"{path}: objects must set additionalProperties to false")
        props = node.get("properties", {})
        missing = [k for k in node.get("required", []) if k not in props]
        if missing:
            raise BadRequestError(f"{path}.required: {missing} not defined in properties")
        for k, v in props.items():
            _check_schema(v, f"{path}.properties.{k}")
    if "items" in node:
        _check_schema(node["items"], f"{path}.items")
    for key in ("anyOf", "allOf"):
        for i, sub in enumerate(node.get(key, [])):
            _check_schema(sub, f"{path}.{key}.{i}")


def _block_get(block, key, default=None):
    if isinstance(block, dict):
        return block.get(key, default)
    return getattr(block, key, default)


def _validate_tools(tools):
    if not isinstance(tools, list):
        raise BadRequestError("tools: must be a list")
    names = set()
    for i, t in enumerate(tools):
        if not isinstance(t, dict) or not t.get("name"):
            raise BadRequestError(f"tools.{i}: each tool needs a name")
        if "type" in t and "input_schema" not in t:
            continue  # Anthropic-defined / server tools have no input_schema
        if not t.get("description"):
            raise BadRequestError(f"tools.{i}.description: write a description so Claude knows when to use the tool")
        schema = t.get("input_schema")
        if not isinstance(schema, dict) or schema.get("type") != "object":
            raise BadRequestError(f"tools.{i}.input_schema: must be a JSON Schema with type 'object'")
        if t.get("strict"):
            _check_schema(schema, f"tools.{i}.input_schema")
        if t["name"] in names:
            raise BadRequestError(f"tools.{i}.name: duplicate tool name {t['name']!r}")
        names.add(t["name"])


def _validate_tool_results(messages):
    """Every tool_use must be answered by tool_result blocks in the very next user message."""
    for i, m in enumerate(messages):
        content = m.get("content")
        if m.get("role") != "assistant" or not isinstance(content, list):
            continue
        ids = [_block_get(b, "id") for b in content if _block_get(b, "type") == "tool_use"]
        if not ids:
            continue
        if i + 1 >= len(messages):
            raise BadRequestError("messages: the conversation ends with tool_use blocks; send the tool_result blocks in a user message")
        nxt = messages[i + 1]
        nxt_content = nxt.get("content") if nxt.get("role") == "user" else None
        results = [] if not isinstance(nxt_content, list) else [_block_get(b, "tool_use_id") for b in nxt_content if _block_get(b, "type") == "tool_result"]
        missing = [x for x in ids if x not in results]
        if missing:
            raise BadRequestError(
                f"messages.{i + 1}: tool_use ids were found without tool_result blocks immediately after: {missing}. "
                "Each tool_use block must have a corresponding tool_result block in the next message."
            )
        unknown = [x for x in results if x not in ids]
        if unknown:
            raise BadRequestError(f"messages.{i + 1}: tool_result blocks reference unknown tool_use ids: {unknown}")
