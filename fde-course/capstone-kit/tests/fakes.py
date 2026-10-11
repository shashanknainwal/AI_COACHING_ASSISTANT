"""Fake SDK objects so the agent loop can be tested without a key or network."""

from __future__ import annotations

from types import SimpleNamespace


def text(t):
    return SimpleNamespace(type="text", text=t)


def thinking(t="(reasoning)", signature="sig-123"):
    return SimpleNamespace(type="thinking", thinking=t, signature=signature)


def tool_use(id_, name, inp):
    return SimpleNamespace(type="tool_use", id=id_, name=name, input=inp)


def response(content, stop_reason, input_tokens=1000, output_tokens=200, cache_read=0, thinking_tokens=0):
    usage = SimpleNamespace(input_tokens=input_tokens, output_tokens=output_tokens,
                            cache_creation_input_tokens=0, cache_read_input_tokens=cache_read,
                            output_tokens_details=SimpleNamespace(thinking_tokens=thinking_tokens))
    return SimpleNamespace(content=content, stop_reason=stop_reason, usage=usage, stop_details=None,
                           _request_id="req_test")


class FakeClient:
    """Returns queued responses in order and records every request."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.requests = []
        self.messages = self

    def create(self, **kwargs):
        snapshot = dict(kwargs)
        snapshot["messages"] = list(kwargs.get("messages", []))
        self.requests.append(snapshot)
        if not self._responses:
            raise AssertionError("FakeClient ran out of responses")
        return self._responses.pop(0)
