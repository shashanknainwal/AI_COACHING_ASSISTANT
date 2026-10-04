"""In-browser simulator of the `requests` HTTP library.

It mirrors the parts of the real library this course uses (`get`/`post`/...,
`Session`, `Response`, `raise_for_status`, timeouts, and the exception
classes), so code written here runs unchanged with `pip install requests`.

No network calls are made. Each exercise defines a fake API with
`requests._sim.route(...)`, including pagination, rate limits, flaky
servers and timeouts.
"""

import json as _json
from urllib.parse import parse_qsl, urlencode, urlsplit

from . import _sim
from . import exceptions
from .exceptions import (
    ConnectionError,
    ConnectTimeout,
    HTTPError,
    ReadTimeout,
    RequestException,
    Timeout,
)

__all__ = [
    "get", "post", "put", "patch", "delete", "request", "Session", "Response",
    "RequestException", "HTTPError", "ConnectionError", "Timeout", "ConnectTimeout",
    "ReadTimeout", "exceptions", "codes",
]

_REASONS = {
    200: "OK", 201: "Created", 202: "Accepted", 204: "No Content", 304: "Not Modified",
    400: "Bad Request", 401: "Unauthorized", 403: "Forbidden", 404: "Not Found",
    409: "Conflict", 422: "Unprocessable Entity", 429: "Too Many Requests",
    500: "Internal Server Error", 502: "Bad Gateway", 503: "Service Unavailable", 504: "Gateway Timeout",
}


class _CaseInsensitiveDict(dict):
    def __init__(self, data=None):
        super().__init__()
        for k, v in (data or {}).items():
            self[k] = v

    def __setitem__(self, key, value):
        super().__setitem__(key.lower(), value)

    def __getitem__(self, key):
        return super().__getitem__(key.lower())

    def __contains__(self, key):
        return super().__contains__(key.lower())

    def get(self, key, default=None):
        return super().get(key.lower(), default)


class PreparedRequest:
    def __init__(self, method, url, headers, body):
        self.method = method
        self.url = url
        self.headers = headers
        self.body = body


class Response:
    def __init__(self, status_code=200, json_body=None, text=None, headers=None, url="", request=None):
        self.status_code = status_code
        self.headers = _CaseInsensitiveDict(headers)
        self.url = url
        self.request = request
        self.reason = _REASONS.get(status_code, "")
        if text is None:
            text = "" if json_body is None else _json.dumps(json_body)
            if json_body is not None and "content-type" not in self.headers:
                self.headers["Content-Type"] = "application/json"
        self.text = text
        self.content = text.encode()

    @property
    def ok(self):
        return self.status_code < 400

    def json(self):
        try:
            return _json.loads(self.text)
        except ValueError as e:
            raise exceptions.JSONDecodeError(f"Response body is not valid JSON: {e}") from None

    def raise_for_status(self):
        if 400 <= self.status_code < 500:
            kind = "Client Error"
        elif 500 <= self.status_code < 600:
            kind = "Server Error"
        else:
            return
        raise HTTPError(f"{self.status_code} {kind}: {self.reason} for url: {self.url}", response=self)

    def __repr__(self):
        return f"<Response [{self.status_code}]>"


def _build_url(url, params):
    if not params:
        return url
    parts = urlsplit(url)
    query = parse_qsl(parts.query, keep_blank_values=True)
    for k, v in params.items():
        if v is None:
            continue
        if isinstance(v, (list, tuple)):
            query.extend((k, str(x)) for x in v)
        else:
            query.append((k, str(v)))
    return parts._replace(query=urlencode(query)).geturl()


def request(method, url, params=None, data=None, json=None, headers=None, timeout=None, auth=None, **_ignored):
    method = method.upper()
    full_url = _build_url(url, params)
    hdrs = {str(k): str(v) for k, v in (headers or {}).items()}
    if auth is not None:
        import base64
        user, pwd = auth
        hdrs["Authorization"] = "Basic " + base64.b64encode(f"{user}:{pwd}".encode()).decode()
    body = None
    if json is not None:
        body = _json.dumps(json)
        hdrs.setdefault("Content-Type", "application/json")
    elif data is not None:
        body = data if isinstance(data, str) else urlencode(data)
    prepared = PreparedRequest(method, full_url, hdrs, body)
    return _sim._dispatch(prepared, json_body=json, timeout=timeout)


def get(url, params=None, **kwargs):
    return request("GET", url, params=params, **kwargs)


def post(url, data=None, json=None, **kwargs):
    return request("POST", url, data=data, json=json, **kwargs)


def put(url, data=None, json=None, **kwargs):
    return request("PUT", url, data=data, json=json, **kwargs)


def patch(url, data=None, json=None, **kwargs):
    return request("PATCH", url, data=data, json=json, **kwargs)


def delete(url, **kwargs):
    return request("DELETE", url, **kwargs)


class Session:
    """Reuses headers (and, in the real library, connections) across requests."""

    def __init__(self):
        self.headers = {"User-Agent": "python-requests/2.32"}
        self.auth = None

    def request(self, method, url, headers=None, **kwargs):
        merged = dict(self.headers)
        merged.update(headers or {})
        if self.auth is not None and "auth" not in kwargs:
            kwargs["auth"] = self.auth
        return request(method, url, headers=merged, **kwargs)

    def get(self, url, params=None, **kwargs):
        return self.request("GET", url, params=params, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        return self.request("POST", url, data=data, json=json, **kwargs)

    def put(self, url, data=None, json=None, **kwargs):
        return self.request("PUT", url, data=data, json=json, **kwargs)

    def patch(self, url, data=None, json=None, **kwargs):
        return self.request("PATCH", url, data=data, json=json, **kwargs)

    def delete(self, url, **kwargs):
        return self.request("DELETE", url, **kwargs)

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


class _Codes:
    ok = 200
    created = 201
    no_content = 204
    bad_request = 400
    unauthorized = 401
    forbidden = 403
    not_found = 404
    conflict = 409
    too_many_requests = 429
    internal_server_error = 500
    service_unavailable = 503


codes = _Codes()
