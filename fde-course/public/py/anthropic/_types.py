import itertools

_ids = itertools.count(1)


class _Model:
    _fields = ()

    def model_dump(self):
        out = {}
        for f in self._fields:
            v = getattr(self, f)
            if isinstance(v, _Model):
                v = v.model_dump()
            elif isinstance(v, list):
                v = [x.model_dump() if isinstance(x, _Model) else x for x in v]
            out[f] = v
        return out

    def to_dict(self):
        return self.model_dump()

    def __repr__(self):
        args = ", ".join(f"{f}={getattr(self, f)!r}" for f in self._fields)
        return f"{type(self).__name__}({args})"

    def __eq__(self, other):
        return type(self) is type(other) and self.model_dump() == other.model_dump()


class TextBlock(_Model):
    _fields = ("type", "text")

    def __init__(self, text):
        self.type = "text"
        self.text = text


class ThinkingBlock(_Model):
    _fields = ("type", "thinking", "signature")

    def __init__(self, thinking="", signature="sim"):
        self.type = "thinking"
        self.thinking = thinking
        self.signature = signature


class ToolUseBlock(_Model):
    _fields = ("type", "id", "name", "input")

    def __init__(self, name, input, id=None):
        self.type = "tool_use"
        self.id = id or f"toolu_sim_{next(_ids):04d}"
        self.name = name
        self.input = input


class Usage(_Model):
    _fields = ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")

    def __init__(self, input_tokens=0, output_tokens=0, cache_read_input_tokens=0, cache_creation_input_tokens=0):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.cache_read_input_tokens = cache_read_input_tokens
        self.cache_creation_input_tokens = cache_creation_input_tokens


class StopDetails(_Model):
    _fields = ("type", "category", "explanation")

    def __init__(self, type="refusal", category=None, explanation=None):
        self.type = type
        self.category = category
        self.explanation = explanation


class Message(_Model):
    _fields = ("id", "type", "role", "model", "content", "stop_reason", "stop_details", "usage")

    def __init__(self, content, model, stop_reason="end_turn", usage=None, stop_details=None):
        self.id = f"msg_sim_{next(_ids):04d}"
        self.type = "message"
        self.role = "assistant"
        self.model = model
        self.content = content
        self.stop_reason = stop_reason
        if isinstance(stop_details, dict):
            stop_details = StopDetails(**stop_details)
        self.stop_details = stop_details
        self.usage = usage or Usage()
        self._request_id = f"req_sim_{next(_ids):06d}"
