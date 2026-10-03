"""In-browser simulator of the official `anthropic` Python SDK.

It mirrors the real SDK's surface for the calls this course teaches
(`Anthropic().messages.create`, typed content blocks, `stop_reason`, `usage`,
typed errors and automatic retries), so code written here runs unchanged
against the real API once you `pip install anthropic` and set ANTHROPIC_API_KEY.

No network calls are made. Responses come from `anthropic._sim`, which each
exercise configures with scripted replies.
"""

from . import _sim
from ._types import (
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
        _validate(params)
        attempts = self._client.max_retries + 1
        last_exc = None
        for attempt in range(attempts):
            _sim._record(params, attempt)
            try:
                return _sim._respond(params)
            except _RETRYABLE as exc:
                last_exc = exc
                continue
        raise last_exc

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
    tc = params.get("tool_choice")
    if isinstance(tc, dict) and tc.get("type") in ("any", "tool") and params["model"] in _sim.NO_FORCED_TOOL_MODELS:
        raise BadRequestError('tool_choice: type "tool" and "any" are not supported for this model.')
