"""A small HTTP service around the agent, for the Dockerfile and Terraform skeleton.

Standard library only, single-threaded, no framework: enough for a demo and a
container health check, not for production traffic. Replace it with your
framework of choice (FastAPI, Flask, a Next.js route) when you need to.

    GET  /healthz          -> 200 {"ok": true}
    POST /ask {"question"} -> 200 {"answer", "status", "tool_calls", "cost_usd", ...}

If SERVICE_TOKEN is set, POST /ask requires "Authorization: Bearer <token>".
Put real auth (IAM, an identity-aware proxy) in front of anything public.
"""

from __future__ import annotations

import hmac
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

from app.agent import run_agent
from app.costs import BudgetExceeded, CostMeter
from app.llm import get_client
from app.tools import LocalTools

MAX_BODY = 16_000
_client = None


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: dict) -> None:
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):  # noqa: N802 (stdlib naming)
        if self.path == "/healthz":
            return self._send(200, {"ok": True})
        return self._send(404, {"error": "not found"})

    def do_POST(self):  # noqa: N802
        global _client
        if self.path != "/ask":
            return self._send(404, {"error": "not found"})
        token = os.environ.get("SERVICE_TOKEN")
        if token and not hmac.compare_digest(self.headers.get("Authorization", ""), f"Bearer {token}"):
            return self._send(401, {"error": "unauthorized"})
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0 or length > MAX_BODY:
            return self._send(400, {"error": "body required, at most 16 KB"})
        try:
            question = str(json.loads(self.rfile.read(length))["question"])[:4000]
        except (ValueError, KeyError, TypeError):
            return self._send(400, {"error": 'send JSON like {"question": "..."}'})
        _client = _client or get_client()
        try:
            res = run_agent(question, client=_client, tools=LocalTools(), meter=CostMeter(budget_usd=0.25))
        except BudgetExceeded as exc:
            return self._send(429, {"error": str(exc)})
        return self._send(200, {"answer": res.text, "status": res.status, "tool_calls": res.tool_calls,
                                "turns": res.turns, "cost_usd": round(res.cost_usd, 6),
                                "latency_s": round(res.latency_s, 2), "request_ids": res.request_ids})

    def log_message(self, fmt, *args):  # one line per request, no bodies (they may hold customer data)
        print(f"{self.address_string()} {fmt % args}", flush=True)


def main() -> None:
    port = int(os.environ.get("PORT", "8080"))
    print(f"listening on :{port}", flush=True)
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
