import json
import re
from anthropic import _sim


def _history(params):
    """{name: (input, content, is_error)} for every tool call answered so far (last one wins)."""
    calls, out = {}, {}
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
                out[name] = (inp, b.get("content"), bool(b.get("is_error")))
    return out


def _responder(params):
    question = params["messages"][0]["content"]
    done = _history(params)
    ref = (re.search(r"\b[A-Z0-9]{6}\b", question) or [None])[0]
    if not ref:
        return _sim.message(_sim.text("Could you share your booking reference?"))
    if "get_booking" not in done:
        return _sim.message(_sim.thinking(""), _sim.tool_use("get_booking", {"booking_ref": ref}))
    inp, content, err = done["get_booking"]
    if err:
        return _sim.message(_sim.text(f"I couldn't find booking {ref}."))
    booking = json.loads(content)
    q = question.lower()
    money = re.search(r"\$(\d+(?:\.\d+)?)", question)
    wants_cancel = "cancel booking" in q or "cancel my booking" in q
    if "issue_refund" not in done and "cancel_booking" not in done:
        calls = []
        if wants_cancel:
            calls.append(_sim.tool_use("cancel_booking", {"booking_ref": ref}))
        if "full fare" in q:
            calls.append(_sim.tool_use("issue_refund", {"booking_ref": ref, "amount": booking["fare_paid"], "reason": "airline_cancellation"}))
        elif money:
            reason = "upgrade_not_provided" if "upgrade" in q else "schedule_change"
            calls.append(_sim.tool_use("issue_refund", {"booking_ref": ref, "amount": float(money.group(1)), "reason": reason}))
        if calls:
            return _sim.message(_sim.thinking(""), *calls)
    parts = []
    if "cancel_booking" in done:
        parts.append(f"Your booking {ref} is cancelled." if not done["cancel_booking"][2]
                     else "I wasn't able to cancel the booking yet; a teammate will follow up.")
    if "issue_refund" in done:
        inp, content, err = done["issue_refund"]
        if err:
            parts.append("I couldn't complete the refund automatically; a teammate will follow up within one business day.")
        else:
            r = json.loads(content)
            parts.append(f"I've refunded ${inp['amount']:.2f} to your card (refund {r['refund_id']}).")
    return _sim.message(_sim.text(" ".join(parts) or f"Booking {ref} is {booking['status']}."))


_sim.set_responder(_responder)
