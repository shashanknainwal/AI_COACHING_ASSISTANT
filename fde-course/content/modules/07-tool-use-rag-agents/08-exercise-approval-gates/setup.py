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
    q = question.lower()
    done = _history(params)
    names = [d[0] for d in done]
    order_id = (re.search(r"\bB-\d+\b", question) or [None])[0]
    if not order_id:
        return _sim.message(_sim.text("Could you share your order number? It looks like B-1001."))
    if "lookup_order" not in names:
        return _sim.message(_sim.thinking(""), _sim.tool_use("lookup_order", {"order_id": order_id}))
    _, _, order_raw, order_err = next(d for d in done if d[0] == "lookup_order")
    if order_err:
        return _sim.message(_sim.text(f"I couldn't find order {order_id}. Could you double-check it?"))
    order = json.loads(order_raw)
    if "late" in q and order["shipment_id"] and "track_shipment" not in names:
        return _sim.message(_sim.tool_use("track_shipment", {"shipment_id": order["shipment_id"]}))
    asked = re.search(r"\$(\d+)", question)
    amount = int(asked.group(1)) if asked else (25 if order["customer_id"] == "C-100" else 20)
    reason = "damaged_item" if "damaged" in q else "late_delivery"
    if "issue_store_credit" not in names:
        return _sim.message(_sim.tool_use("issue_store_credit",
                                          {"customer_id": order["customer_id"], "amount": amount, "reason": reason}))
    _, credit_in, credit_raw, credit_err = next(d for d in done if d[0] == "issue_store_credit")
    if not credit_err:
        balance = json.loads(credit_raw)["new_balance"]
        return _sim.message(_sim.text(f"I've added ${credit_in['amount']} in store credit. Your balance is now ${balance:.2f}."))
    if str(credit_raw).startswith("Declined"):
        return _sim.message(_sim.text("I've sent your request to a teammate, who will follow up within one business day."))
    return _sim.message(_sim.text("I couldn't add that credit automatically; a teammate will follow up."))


_sim.set_responder(_responder)
