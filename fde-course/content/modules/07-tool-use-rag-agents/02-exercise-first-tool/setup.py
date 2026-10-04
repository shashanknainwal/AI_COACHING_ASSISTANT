import json
import re
from anthropic import _sim


def _responder(params):
    last = params["messages"][-1]["content"]
    if isinstance(last, str):
        m = re.search(r"\bB-\d+\b", last, re.I)
        if not m:
            return _sim.message(_sim.thinking(""), _sim.text("Happy to help. What's your order ID? It looks like B-1001."))
        return _sim.message(_sim.thinking(""), _sim.text("Let me look that up."),
                            _sim.tool_use("lookup_order", {"order_id": m.group(0)}))
    result = next(b for b in last if b.get("type") == "tool_result")
    if result.get("is_error"):
        return _sim.message(_sim.text(f"I couldn't find that order ({result['content']}) Could you double-check the number?"))
    order = json.loads(result["content"])
    items = ", ".join(order["items"])
    return _sim.message(_sim.text(
        f"Order {order['order_id']} ({items}, ${order['total']:.2f}) is currently {order['status']}."
        + (f" Its shipment ID is {order['shipment_id']}." if order["shipment_id"] else "")))


_sim.set_responder(_responder)
