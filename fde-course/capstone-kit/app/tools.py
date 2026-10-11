"""Tool definitions (what the model sees) and a dispatcher (what your code runs).

Two backends share one interface, `.definitions` and `.call(name, input)`:
- LocalTools calls the customer system in-process.
- MCPTools (app/mcp_client.py) calls the same tools through the MCP server.

Tool inputs are model output: validate them before acting, and never let a
tool result's text change what the agent is allowed to do.
"""

from __future__ import annotations

import json
from typing import Callable

from app.customer_system import CustomerSystem

# strict: true makes the API validate inputs against the schema. Strict schemas
# need additionalProperties: false. Keep this list in a fixed order: tools are
# part of the cached prefix, and reordering them invalidates the cache.
TOOL_DEFINITIONS: list[dict] = [
    {
        "name": "get_order",
        "description": "Look up one order by its order number (format QF-1234). Returns status, dates, items and days since delivery. Read-only.",
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {"type": "string", "description": "Order number, e.g. QF-1001"}},
            "required": ["order_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "search_knowledge_base",
        "description": "Search the help-centre articles (returns, shipping, damage, engraving, billing, accounts, loyalty, wholesale, product care). Returns the top passages. Read-only.",
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "A short search query in plain words"}},
            "required": ["query"],
            "additionalProperties": False,
        },
    },
    {
        "name": "create_escalation",
        "description": "Ask a human agent to take over (refund disputes, anything the policy does not cover, angry customers). Needs operator approval; may be declined.",
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "Order number, or 'none'"},
                "reason": {"type": "string", "description": "One sentence for the human agent"},
            },
            "required": ["order_id", "reason"],
            "additionalProperties": False,
        },
    },
]


def deny_all(name: str, tool_input: dict) -> bool:
    """Default approval policy: nothing that writes runs without a human."""
    return False


class LocalTools:
    def __init__(self, system: CustomerSystem | None = None,
                 approve: Callable[[str, dict], bool] = deny_all):
        self.system = system or CustomerSystem()
        self.approve = approve
        self.definitions = TOOL_DEFINITIONS

    def call(self, name: str, tool_input: dict) -> tuple[str, bool]:
        """Run one tool. Returns (result_text, is_error). Never raises."""
        try:
            if name == "get_order":
                out = self.system.get_order(str(tool_input["order_id"]))
            elif name == "search_knowledge_base":
                out = self.system.search_knowledge_base(str(tool_input["query"]))
            elif name == "create_escalation":
                approved = self.approve(name, tool_input)
                out = self.system.create_escalation(str(tool_input["order_id"]), str(tool_input["reason"]), approved)
            else:
                return json.dumps({"error": f"unknown tool {name}"}), True
        except (KeyError, TypeError, ValueError) as exc:
            return json.dumps({"error": f"bad input for {name}: {exc}"}), True
        return json.dumps(out, sort_keys=True), "error" in out
