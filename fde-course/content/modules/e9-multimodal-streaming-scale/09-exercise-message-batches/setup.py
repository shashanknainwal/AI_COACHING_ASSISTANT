import itertools
import re
import time

import anthropic
from anthropic._types import Message, TextBlock, ThinkingBlock, Usage

MODEL = "claude-haiku-5-5"
MAX_TOKENS = 1024
SYSTEM_PROMPT = ("Label the archived order-desk email with one intent: delivery_status, billing, returns or other. "
                 "Reply with the label only.")
CUSTOM_ID_PATTERN = r"^[a-zA-Z0-9_-]{1,64}$"
MAX_BATCH_REQUESTS = 100_000
PROCESSING_SECONDS = 1500          # this simulated batch takes 25 minutes


class _Obj:
    def __init__(self, **kw):
        self.__dict__.update(kw)

    def __repr__(self):
        return f"{type(self).__name__}({', '.join(f'{k}={v!r}' for k, v in self.__dict__.items())})"


class MessageBatch(_Obj):
    pass


class BatchResult(_Obj):
    pass


def _label(text):
    t = text.lower()
    if "return" in t or "damaged" in t:
        return "returns"
    if "where is" in t or "arrive" in t:
        return "delivery_status"
    if "invoice" in t or "charged" in t:
        return "billing"
    return "other"


# Scripted outcomes by order text marker and attempt number (1-based). Anything unlisted succeeds.
_SCRIPT = {
    "[A]": ["api_error"],                                  # transient server error, then fine
    "[E]": ["expired"],                                    # expired in round 1, fine after
    "[O]": ["overloaded_error", "overloaded_error"],       # fails twice, fine in round 3
    "[S]": ["api_error", "api_error", "api_error", "api_error"],   # never succeeds
}


class _Batches:
    def __init__(self):
        self._ids = itertools.count(1)
        self.store = {}
        self.attempts = {}        # order text -> number of times it was batched
        self.results_read_early = 0
        self.created = []         # list of lists of custom_ids, one per create()

    def create(self, requests):
        if not isinstance(requests, list) or not requests or len(requests) > MAX_BATCH_REQUESTS:
            raise anthropic.BadRequestError("requests: must be a list of 1 to 100,000 requests")
        seen = set()
        for i, r in enumerate(requests):
            cid = r.get("custom_id") if isinstance(r, dict) else None
            if not isinstance(cid, str) or not re.match(CUSTOM_ID_PATTERN, cid):
                raise anthropic.BadRequestError(f"requests.{i}.custom_id: must match {CUSTOM_ID_PATTERN}, got {cid!r}")
            if cid in seen:
                raise anthropic.BadRequestError(f"requests.{i}.custom_id: duplicate custom_id {cid!r}")
            seen.add(cid)
            if not isinstance(r.get("params"), dict):
                raise anthropic.BadRequestError(f"requests.{i}.params: required")
        bid = f"msgbatch_sim_{next(self._ids):03d}"
        self.store[bid] = {"created": time.time(), "requests": [dict(r) for r in requests]}
        self.created.append([r["custom_id"] for r in requests])
        return self.retrieve(bid)

    def _ended(self, bid):
        return time.time() - self.store[bid]["created"] >= PROCESSING_SECONDS

    def retrieve(self, batch_id):
        b = self.store[batch_id]
        n = len(b["requests"])
        ended = self._ended(batch_id)
        counts = {"processing": 0 if ended else n, "succeeded": 0, "errored": 0, "canceled": 0, "expired": 0}
        if ended:
            for r in self._outcomes(batch_id):
                counts[r.result.type] += 1
        return MessageBatch(id=batch_id, type="message_batch", processing_status="ended" if ended else "in_progress",
                            request_counts=_Obj(**counts))

    def _outcomes(self, batch_id):
        b = self.store[batch_id]
        if "outcomes" in b:
            return b["outcomes"]
        out = []
        for r in b["requests"]:
            p = r["params"]
            content = ""
            try:
                content = p["messages"][-1]["content"]
            except (KeyError, IndexError, TypeError):
                pass
            if "stream" in p or not isinstance(p.get("max_tokens"), int) or p["max_tokens"] < 1 \
                    or not isinstance(content, str) or not content.strip() or "model" not in p:
                err = {"type": "error", "error": {"type": "invalid_request_error", "message": "invalid request params"}}
                out.append(BatchResult(custom_id=r["custom_id"], result=_Obj(type="errored", error=_err(err))))
                continue
            n = self.attempts[content] = self.attempts.get(content, 0) + 1
            script = next((v for k, v in _SCRIPT.items() if k in content), [])
            outcome = script[n - 1] if n <= len(script) else "ok"
            if outcome == "ok":
                msg = Message([ThinkingBlock(""), TextBlock(_label(content))], model=p["model"],
                              usage=Usage(input_tokens=210, output_tokens=55))
                out.append(BatchResult(custom_id=r["custom_id"], result=_Obj(type="succeeded", message=msg)))
            elif outcome == "expired":
                out.append(BatchResult(custom_id=r["custom_id"], result=_Obj(type="expired")))
            else:
                err = {"type": "error", "error": {"type": outcome, "message": outcome.replace("_", " ")}}
                out.append(BatchResult(custom_id=r["custom_id"], result=_Obj(type="errored", error=_err(err))))
        out.reverse()   # results can come back in any order
        b["outcomes"] = out
        return out

    def results(self, batch_id):
        if not self._ended(batch_id):
            self.results_read_early += 1
            raise anthropic.BadRequestError("Batch results are not available until processing has ended")
        return iter(list(self._outcomes(batch_id)))


def _err(d):
    return _Obj(type=d["type"], error=_Obj(**d["error"]))


client = anthropic.Anthropic()
client.messages.batches = _Batches()

_TEXT = [
    "Where is PO#{n}? Still not here.",
    "Invoice for PO#{n} charged twice.",
    "Returning damaged gloves from PO#{n}.",
    "Do you stock M12 washers?",
]
ORDERS = []
for i in range(1, 25):
    oid = f"PO#{4400 + i}/{i % 3 + 1}"
    text = _TEXT[i % 4].format(n=4400 + i)
    marker = {3: " [A]", 7: " [E]", 11: " [O]", 19: " [S]"}.get(i, "")
    ORDERS.append({"order_id": oid, "text": "" if i == 15 else text + marker})
