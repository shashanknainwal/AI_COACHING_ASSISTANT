"""Fake HTTP server behind the simulated `requests` library.

Exercises define routes in a hidden setup file:

    from requests import _sim

    def list_shipments(req):
        return _sim.respond(200, json={"data": [...], "next_cursor": None})

    _sim.route("GET", r"/v1/shipments", list_shipments)
    _sim.route("GET", r"/v1/flaky", _sim.flaky(list_shipments, [503, "timeout"]))

Tests inspect `_sim.calls` to see exactly what the learner's code sent.
"""

import json as _json
import re
from urllib.parse import parse_qsl, urlsplit

calls = []      # SimRequest objects, oldest first
_routes = []


class SimRequest:
    def __init__(self, prepared, json_body, timeout):
        parts = urlsplit(prepared.url)
        self.method = prepared.method
        self.url = prepared.url
        self.path = parts.path
        self.query = parse_qsl(parts.query, keep_blank_values=True)
        self.params = dict(self.query)          # last value wins, like most frameworks
        self.headers = {k.lower(): v for k, v in prepared.headers.items()}
        self.body = prepared.body
        self.json = json_body
        self.timeout = timeout

    def header(self, name, default=None):
        return self.headers.get(name.lower(), default)

    def __repr__(self):
        return f"<SimRequest {self.method} {self.url}>"


def reset():
    calls.clear()
    _routes.clear()


def route(method, path_pattern, handler):
    """Register a handler for METHOD + a regex that must fully match the URL path."""
    _routes.append((method.upper(), re.compile(path_pattern), handler))


def respond(status=200, json=None, headers=None, text=None):
    from . import Response
    return Response(status_code=status, json_body=json, text=text, headers=headers)


def timeout():
    from .exceptions import ReadTimeout
    return ReadTimeout("HTTPSConnectionPool: Read timed out. (read timeout)")


def connection_error():
    from .exceptions import ConnectionError
    return ConnectionError("Failed to establish a new connection: [Errno 111] Connection refused")


def flaky(handler, failures):
    """Return each failure in order (a status code, "timeout", or "connection"), then delegate."""
    pending = list(failures)

    def wrapped(req):
        if pending:
            f = pending.pop(0)
            if f == "timeout":
                return timeout()
            if f == "connection":
                return connection_error()
            if isinstance(f, tuple):
                status, headers = f
                return respond(status, json={"error": "simulated failure"}, headers=headers)
            return respond(f, json={"error": "simulated failure"})
        return handler(req)

    return wrapped


def rate_limited(handler, max_requests, per_seconds):
    """Allow max_requests per window of per_seconds (virtual time); otherwise 429 + Retry-After."""
    import time
    window = {"start": None, "count": 0}

    def wrapped(req):
        now = time.monotonic()
        if window["start"] is None or now - window["start"] >= per_seconds:
            window["start"], window["count"] = now, 0
        if window["count"] >= max_requests:
            retry_after = max(1, int(per_seconds - (now - window["start"]) + 0.999))
            return respond(429, json={"error": "rate limit exceeded"}, headers={"Retry-After": str(retry_after)})
        window["count"] += 1
        return handler(req)

    return wrapped


def requests_to(path_pattern, method=None):
    rx = re.compile(path_pattern)
    return [c for c in calls if rx.fullmatch(c.path) and (method is None or c.method == method.upper())]


_DEMO = [
    {"id": "SHP-1001", "status": "in_transit", "origin": "Chicago, IL", "destination": "Dallas, TX"},
    {"id": "SHP-1002", "status": "delivered", "origin": "Newark, NJ", "destination": "Boston, MA"},
    {"id": "SHP-1003", "status": "exception", "origin": "Denver, CO", "destination": "Phoenix, AZ"},
]


def _default(req):
    if req.method == "GET" and req.path.rstrip("/") == "/v1/shipments":
        return respond(200, json={"data": _DEMO, "next_cursor": None})
    if req.method == "GET" and req.path.startswith("/v1/shipments/"):
        sid = req.path.rsplit("/", 1)[1]
        for s in _DEMO:
            if s["id"] == sid:
                return respond(200, json=s)
    return respond(404, json={"error": f"no route for {req.method} {req.path}"})


def _dispatch(prepared, json_body, timeout):
    req = SimRequest(prepared, json_body, timeout)
    calls.append(req)
    handler = None
    for method, rx, h in _routes:
        if method == req.method and rx.fullmatch(req.path):
            handler = h
            break
    if handler is None:
        handler = _default if not _routes else (lambda r: respond(404, json={"error": f"no route for {r.method} {r.path}"}))
    result = handler(req)
    if isinstance(result, BaseException):
        raise result
    if isinstance(result, tuple):
        result = respond(*result)
    elif isinstance(result, (dict, list)):
        result = respond(200, json=result)
    result.url = prepared.url
    result.request = prepared
    return result
