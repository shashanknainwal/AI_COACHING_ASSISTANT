"""Scripted stand-in for Claude running NorthStar's exception-triage agent (Module 10).

install() registers a responder that reads the tool history and decides the next
tool call, like a real model would, including a few realistic mistakes.
"""

import json
import re

from anthropic import _sim

CARRIERS = ["FastFreight", "BlueLine Express", "NorthPeak Carriers"]
# Realistic mistakes the eval should catch.
_WRONG_PRIORITY = {"NS-2018": "P2"}          # a platinum delay treated as routine
_FORGETS_TO_NOTIFY = {"NS-2016"}             # opens the claim but never tells the customer
_PROMISES_CREDIT_FIRST = {"NS-2005"}         # first draft promises a credit; the guardrail blocks it


def _history(params):
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


def _priority(s):
    if s["tier"] == "platinum":
        return "P1"
    if s["tier"] == "gold" or s["event_code"] in ("DAMAGE", "CUSTOMS_HOLD"):
        return "P2"
    return "P3"


def _call(name, **inp):
    return _sim.message(_sim.tool_use(name, inp))


def _responder(params):
    question = str(params["messages"][0]["content"])
    done = _history(params)
    names = [d[0] for d in done]
    ok = lambda n: any(d[0] == n and not d[3] for d in done)
    sid = (re.search(r"NS-\d+", question) or [None])[0]
    if "record_decision" in names:
        return _sim.message(_sim.text("Triage complete."))
    if sid is None:
        return _sim.message(_sim.text("Which shipment should I look at?"))
    if "get_shipment" not in names:
        return _sim.message(_sim.thinking(""), _sim.tool_use("get_shipment", {"shipment_id": sid}))
    _, _, raw, err = next(d for d in done if d[0] == "get_shipment")
    if err:
        return _call("record_decision", action="escalate", priority="P3", reason=f"No shipment found for {sid}.")
    s = json.loads(raw)
    code, prio = s["event_code"], _WRONG_PRIORITY.get(sid, _priority(s))

    def notify(text):
        if sid in _PROMISES_CREDIT_FIRST and names.count("notify_customer") == 0:
            text += " We'll credit your account for the inconvenience."
        return _call("notify_customer", shipment_id=sid, message=text)

    if code == "DELAY":
        if not ok("notify_customer"):
            return notify(f"Update on shipment {sid}: {s['event_detail']}. We're monitoring it closely and will update you.")
        if prio == "P1" and "create_ops_ticket" not in names:
            return _call("create_ops_ticket", shipment_id=sid, priority=prio, summary=f"Platinum delay: {s['event_detail']}")
        action = "notify_and_ticket" if ok("create_ops_ticket") else "notify_only"
        return _call("record_decision", action=action, priority=prio, reason=f"Delay for a {s['tier']} customer.")
    if code in ("DAMAGE", "CUSTOMS_HOLD"):
        if "create_ops_ticket" not in names:
            label = "Damage claim" if code == "DAMAGE" else "Customs hold"
            return _call("create_ops_ticket", shipment_id=sid, priority=prio, summary=f"{label}: {s['event_detail']}")
        if not ok("notify_customer") and sid not in _FORGETS_TO_NOTIFY:
            what = "damage to your freight" if code == "DAMAGE" else "a customs hold"
            return notify(f"Shipment {sid} has {what}: {s['event_detail']}. Our team is on it and will update you.")
        action = "open_claim" if code == "DAMAGE" else "escalate_customs"
        return _call("record_decision", action=action, priority=prio, reason=s["event_detail"])
    if code == "ADDRESS_ISSUE":
        if not ok("notify_customer"):
            return notify(f"We need your help with shipment {sid}: {s['event_detail']}. Please reply with the full delivery address.")
        return _call("record_decision", action="request_address", priority=prio, reason=s["event_detail"])
    if code == "PICKUP_MISSED":
        if "reroute_shipment" not in names:
            backup = next(c for c in CARRIERS if c != s["carrier"])
            return _call("reroute_shipment", shipment_id=sid, carrier=backup)
        if ok("reroute_shipment"):
            if not ok("notify_customer"):
                return notify(f"The pickup for {sid} was missed, so we've booked a backup carrier. We'll confirm the new pickup time.")
            return _call("record_decision", action="reroute", priority="P1", reason="Pickup missed; backup carrier booked.")
        if "create_ops_ticket" not in names:
            return _call("create_ops_ticket", shipment_id=sid, priority="P1", summary="Pickup missed; reroute not approved.")
        return _call("record_decision", action="escalate", priority="P1", reason="Reroute declined; a coordinator must act.")
    return _call("record_decision", action="no_action", priority="P3", reason=f"Latest event is {code}; nothing to do.")


def install():
    _sim.set_responder(_responder)
