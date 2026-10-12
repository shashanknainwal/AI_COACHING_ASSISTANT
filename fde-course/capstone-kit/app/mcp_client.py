"""A minimal stdio MCP client so the agent can use tools through the MCP server.

HAND-WRITTEN, NOT THE OFFICIAL SDK (see app/mcp_server.py for why). It
spawns the server as a subprocess, does the initialize handshake, lists the
tools, and exposes them with the same interface as LocalTools, so
`run_agent(..., tools=MCPTools())` drives the agent through MCP.

The Anthropic Python SDK also ships MCP conversion helpers for the tool
runner (`pip install anthropic[mcp]`); check the SDK docs if you prefer those.
"""

from __future__ import annotations

import json
import subprocess
import sys
from itertools import count


class MCPTools:
    def __init__(self, command: list[str] | None = None, env: dict | None = None):
        self.command = command or [sys.executable, "-m", "app.mcp_server"]
        self.proc = subprocess.Popen(self.command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     text=True, env=env, bufsize=1)
        self._ids = count(1)
        init = self._request("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                            "clientInfo": {"name": "capstone-agent", "version": "0.1.0"}})
        self.server_info = init.get("serverInfo", {})
        self._notify("notifications/initialized")
        listed = self._request("tools/list", {})
        # MCP descriptors -> Anthropic tool definitions
        self.definitions = [{"name": t["name"], "description": t.get("description", ""),
                             "input_schema": t["inputSchema"]} for t in listed["tools"]]

    def _send(self, msg: dict) -> None:
        assert self.proc.stdin is not None
        self.proc.stdin.write(json.dumps(msg) + "\n")
        self.proc.stdin.flush()

    def _notify(self, method: str, params: dict | None = None) -> None:
        self._send({"jsonrpc": "2.0", "method": method, **({"params": params} if params else {})})

    def _request(self, method: str, params: dict) -> dict:
        id_ = next(self._ids)
        self._send({"jsonrpc": "2.0", "id": id_, "method": method, "params": params})
        assert self.proc.stdout is not None
        while True:
            line = self.proc.stdout.readline()
            if not line:
                raise RuntimeError(f"MCP server exited during {method}")
            msg = json.loads(line)
            if msg.get("id") == id_:
                if "error" in msg:
                    raise RuntimeError(f"MCP error {msg['error'].get('code')}: {msg['error'].get('message')}")
                return msg["result"]

    def call(self, name: str, tool_input: dict) -> tuple[str, bool]:
        try:
            result = self._request("tools/call", {"name": name, "arguments": tool_input})
        except RuntimeError as exc:
            return json.dumps({"error": str(exc)}), True
        text = "".join(c.get("text", "") for c in result.get("content", []) if c.get("type") == "text")
        return text, bool(result.get("isError"))

    def close(self) -> None:
        if self.proc.poll() is None:
            if self.proc.stdin:
                self.proc.stdin.close()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        if self.proc.stdout:
            self.proc.stdout.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
