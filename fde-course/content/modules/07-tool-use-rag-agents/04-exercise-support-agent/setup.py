import json
import re
from anthropic import _sim


def _history(params):
    """[(tool_name, input, result_content, is_error)] for every completed tool call so far."""
    calls, out = {}, []
    for m in params["messages"]:
        if not isinstance(m["content"], list):
            continue
        for b in m["content"]:
            t = b.get("type") if isinstance(b, dict) else b.type
            if t == "tool_use":
                bid = b["id"] if isinstance(b, dict) else b.id
                calls[bid] = (b["name"], b["input"]) if isinstance(b, dict) else (b.name, b.input)
            elif t == "tool_result":
                name, inp = calls.get(b["tool_use_id"], ("?", {}))
                out.append((name, inp, b.get("content"), b.get("is_error", False)))
    return out


def _responder(params):
    question = params["messages"][0]["content"]
    done = _history(params)
    names = [d[0] for d in done]
    order_id = (re.search(r"\bB-\d+\b", question) or [None])[0]
    if not order_id:
        return _sim.message(_sim.text("Could you share your order number? It looks like B-1001."))
    if "lookup_order" not in names:
        return _sim.message(_sim.thinking(""), _sim.tool_use("lookup_order", {"order_id": order_id}))
    order_name, _, order_raw, order_err = next(d for d in done if d[0] == "lookup_order")
    if order_err:
        return _sim.message(_sim.text(f"I couldn't find order {order_id}. Could you double-check it?"))
    order = json.loads(order_raw)
    if order["shipment_id"] and "track_shipment" not in names:
        return _sim.message(_sim.tool_use("track_shipment", {"shipment_id": order["shipment_id"]}))
    ship = next((json.loads(d[2]) for d in done if d[0] == "track_shipment" and not d[3]), None)
    wants_credit = any(w in question.lower() for w in ("make it right", "compensat", "credit"))
    if ship and ship["status"] == "exception" and wants_credit and "issue_store_credit" not in names:
        amount = 25 if order["customer_id"] == "C-100" else 20
        return _sim.message(_sim.tool_use("issue_store_credit",
                                          {"customer_id": order["customer_id"], "amount": amount, "reason": "late_delivery"}))
    credit = next((d for d in done if d[0] == "issue_store_credit"), None)
    parts = [f"Your order {order_id} is {order['status']}."]
    if ship:
        parts.append(f"The latest update: {ship['last_event']} (new estimate {ship['eta']}).")
    if credit and not credit[3]:
        parts.append(f"I've added ${credit[1]['amount']} in store credit for the delay. Your balance is now ${json.loads(credit[2])['new_balance']:.2f}.")
    elif credit:
        parts.append("I wasn't able to add store credit automatically; a teammate will follow up.")
    return _sim.message(_sim.text(" ".join(parts)))


_sim.set_responder(_responder)
