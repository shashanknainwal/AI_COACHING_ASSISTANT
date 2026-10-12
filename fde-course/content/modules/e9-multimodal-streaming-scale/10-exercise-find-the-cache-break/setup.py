import copy
import json

# Logged request bodies from Tallowmere's order-desk agent, in pairs: request N and request N+1.
# Each pair should share its cached prefix. In most pairs something broke it.

SYSTEM_TEXT = ("You are the Tallowmere order-desk assistant. Answer staff questions about orders, stock "
               "and returns using the tools. Quote order numbers exactly. " * 6).strip()


def _tool(name, desc, props, required):
    return {"name": name, "description": desc,
            "input_schema": {"type": "object", "properties": props, "required": required}}


TOOLS = [
    _tool("check_stock", "Stock on hand for one SKU at one warehouse.",
          {"sku": {"type": "string"}, "warehouse": {"type": "string"}}, ["sku"]),
    _tool("get_order", "Header and lines for one purchase order.",
          {"po_number": {"type": "string"}}, ["po_number"]),
    _tool("create_return", "Open a return authorisation for order lines.",
          {"po_number": {"type": "string"}, "lines": {"type": "array", "items": {"type": "string"}}}, ["po_number", "lines"]),
]


def _system(extra=""):
    return [{"type": "text", "text": SYSTEM_TEXT + extra, "cache_control": {"type": "ephemeral"}}]


def _user(text, mark=False):
    block = {"type": "text", "text": text}
    if mark:
        block["cache_control"] = {"type": "ephemeral"}
    return {"role": "user", "content": [block]}


TOOL_RESULT = json.dumps({"po_number": "PO-4471", "status": "picking", "lines": [
    {"sku": "TS-HB-M8-50", "qty": 200}, {"sku": "TS-CB-3C25", "qty": 150}], "notes": "Dock 3, deliver by 2026-10-24"})

HISTORY = [
    _user("Where is PO-4471?"),
    {"role": "assistant", "content": [{"type": "tool_use", "id": "toolu_01", "name": "get_order", "input": {"po_number": "PO-4471"}}]},
    {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "toolu_01", "content": TOOL_RESULT}]},
    {"role": "assistant", "content": [{"type": "text", "text": "PO-4471 is being picked at Dock 3."}]},
]


def _body(model="claude-sonnet-5-5", tools=None, system=None, messages=None):
    return {"model": model, "max_tokens": 2000, "output_config": {"effort": "low"},
            "tools": copy.deepcopy(TOOLS if tools is None else tools),
            "system": system if system is not None else _system(),
            "messages": copy.deepcopy(messages if messages is not None else HISTORY + [_user("And the cable line?", mark=True)])}


_grown = HISTORY + [_user("And the cable line?"),
                    {"role": "assistant", "content": [{"type": "text", "text": "150 m of TS-CB-3C25, picked today."}]},
                    _user("Thanks. Can it ship on Tuesday?", mark=True)]

_reordered_schema = copy.deepcopy(TOOLS)
s = _reordered_schema[1]["input_schema"]
_reordered_schema[1]["input_schema"] = {"properties": s["properties"], "required": s["required"], "type": "object"}

_trimmed = copy.deepcopy(HISTORY) + [_user("And the cable line?"),
                                     {"role": "assistant", "content": [{"type": "text", "text": "150 m, picked today."}]},
                                     _user("Can it ship Tuesday?", mark=True)]
_trimmed[2]["content"][0]["content"] = TOOL_RESULT[:60] + "...[trimmed]"

PAIRS = {
    "growing": (_body(), _body(messages=_grown)),
    "timestamp": (_body(system=_system("\nCurrent time: 2026-10-11T09:14:03Z")),
                  _body(system=_system("\nCurrent time: 2026-10-11T09:14:41Z"))),
    "tool_order": (_body(), _body(tools=[TOOLS[1], TOOLS[0], TOOLS[2]])),
    "key_order": (_body(), _body(tools=_reordered_schema)),
    "tools_changed": (_body(), _body(tools=TOOLS[:2])),
    "history_trim": (_body(messages=HISTORY + [_user("And the cable line?"),
                                               {"role": "assistant", "content": [{"type": "text", "text": "150 m, picked today."}]},
                                               _user("Can it ship Tuesday?", mark=True)]),
                     _body(messages=_trimmed)),
    "model_switch": (_body(), _body(model="claude-haiku-5-5")),
    "marker_moved": (_body(system=[{"type": "text", "text": SYSTEM_TEXT}]), _body()),
}
