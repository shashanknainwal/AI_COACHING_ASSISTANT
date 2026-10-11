import asyncio
import asyncio.base_events as _base_events
from asyncio import events as _events

import anthropic
from anthropic import _sim
from anthropic._types import Message, TextBlock, ThinkingBlock, Usage

MODEL = "claude-haiku-5-5"
MAX_TOKENS = 1024
BACKOFF_BASE = 0.5
SYSTEM_PROMPT = ("Label the order-desk email with one intent: delivery_status, billing, returns or other. "
                 "Reply with the label only.")

# ---- a virtual clock for asyncio --------------------------------------------
# The browser already runs an event loop, so asyncio.run() isn't available here.
# run_async() runs your coroutine on a private loop whose clock is virtual:
# asyncio.sleep(2) returns instantly but advances loop.time() by 2 seconds.


class _NoWaitSelector:
    def __init__(self, loop):
        self._loop = loop

    def select(self, timeout=None):
        if timeout:
            self._loop._virtual_now += timeout
        return []


class _VirtualLoop(_base_events.BaseEventLoop):
    def __init__(self):
        super().__init__()
        self._virtual_now = 0.0
        self._selector = _NoWaitSelector(self)

    def time(self):
        return self._virtual_now

    def _process_events(self, event_list):
        pass

    def _write_to_self(self):
        pass


def run_async(coro):
    """Use this where production code would call asyncio.run(coro)."""
    previous = _events._get_running_loop()
    _events._set_running_loop(None)
    loop = _VirtualLoop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()
        _events._set_running_loop(previous)


# ---- a simulated API server with a concurrency limit ---------------------------
SERVER_CONCURRENCY = 8
RETRY_AFTER_SECONDS = 2


class _Server:
    def __init__(self):
        self.reset()

    def reset(self):
        self.inflight = 0
        self.max_inflight = 0
        self.attempts = {}       # ticket text -> [(arrived_at, outcome, finished_at)]
        self.rate_limited = 0
        self.overloaded_once = set()


SERVER = _Server()
HOT_TICKET = "T-0031"
FLAKY_TICKET = "T-0017"


def _label(text):
    t = text.lower()
    if "return" in t or "damaged" in t:
        return "returns"
    if "where is" in t or "delivery" in t or "arrive" in t:
        return "delivery_status"
    if "invoice" in t or "charged" in t or "credit note" in t:
        return "billing"
    return "other"


class _AsyncMessages:
    def __init__(self, client):
        self._client = client

    async def create(self, **params):
        loop = asyncio.get_running_loop()
        arrived = loop.time()
        text = ""
        try:
            text = params["messages"][-1]["content"]
        except (KeyError, IndexError, TypeError):
            pass
        log = SERVER.attempts.setdefault(text, [])
        SERVER.inflight += 1
        SERVER.max_inflight = max(SERVER.max_inflight, SERVER.inflight)
        try:
            _sim.calls.append({"params": _sim._snapshot(params), "attempt": len(log), "stream": False})
            for key in ("model", "max_tokens", "messages"):
                if key not in params:
                    log.append((arrived, "BadRequestError", arrived))
                    raise anthropic.BadRequestError(f"{key}: Field required")
            if not isinstance(text, str) or not text.strip():
                log.append((arrived, "BadRequestError", arrived))
                raise anthropic.BadRequestError("messages.0.content: text content blocks must be non-empty")
            if SERVER.inflight > SERVER_CONCURRENCY or text.startswith(HOT_TICKET):
                await asyncio.sleep(0.05)
                SERVER.rate_limited += 1
                log.append((arrived, "RateLimitError", loop.time()))
                raise anthropic.RateLimitError("Error code: 429 - rate_limit_error",
                                               headers={"retry-after": str(RETRY_AFTER_SECONDS)})
            if text.startswith(FLAKY_TICKET) and text not in SERVER.overloaded_once:
                SERVER.overloaded_once.add(text)
                await asyncio.sleep(0.3)
                log.append((arrived, "OverloadedError", loop.time()))
                raise anthropic.OverloadedError("Error code: 529 - overloaded_error")
            await asyncio.sleep(1.0 + (sum(map(ord, text)) % 5) * 0.1)
            log.append((arrived, "ok", loop.time()))
            return Message([ThinkingBlock(""), TextBlock(_label(text))], model=params["model"],
                           usage=Usage(input_tokens=180, output_tokens=60))
        finally:
            SERVER.inflight -= 1


class SimAsyncAnthropic:
    """Simulated anthropic.AsyncAnthropic: same constructor and awaitable messages.create."""

    def __init__(self, api_key=None, max_retries=2, timeout=600.0, **_ignored):
        self.api_key = api_key
        self.max_retries = max_retries
        self.timeout = timeout
        self.messages = _AsyncMessages(self)


anthropic.AsyncAnthropic = SimAsyncAnthropic

_BODIES = [
    "Where is order PO-{n}? It was due yesterday.",
    "Invoice INV-{n} charged us twice for the cable ties.",
    "We need to return two boxes from PO-{n}, they arrived damaged.",
    "Can you quote 500 M10 bolts for next month?",
    "When will PO-{n} arrive at Dock 3?",
]
TICKETS = []
for i in range(1, 41):
    tid = f"T-{i:04d}"
    body = "" if i == 9 else _BODIES[i % 5].format(n=4400 + i)
    TICKETS.append({"id": tid, "text": f"{tid}: {body}" if body else ""})
