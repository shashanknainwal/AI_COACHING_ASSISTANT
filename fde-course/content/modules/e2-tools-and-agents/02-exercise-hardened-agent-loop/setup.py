import json
import re
from anthropic import _sim


def _history(params):
    """[(name, input, content, is_error)] for every tool call answered so far."""
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
                out.append((name, inp, b.get("content"), bool(b.get("is_error"))))
    return out


def _first(done, name):
    return next((d for d in done if d[0] == name), None)


def _responder(params):
    question = params["messages"][0]["content"]
    done = _history(params)
    ref = (re.search(r"\b[A-Z0-9]{6}\b", question) or [None])[0]
    if not ref:
        return _sim.message(_sim.text("Could you share your 6-character booking reference? It looks like FW7Q2K."))
    booking = _first(done, "get_booking")
    if booking is None:
        return _sim.message(_sim.thinking(""), _sim.tool_use("get_booking", {"booking_ref": ref}))
    if booking[3]:
        return _sim.message(_sim.text(f"I couldn't find booking {ref}. Could you double-check the reference?"))
    b = json.loads(booking[2])
    status = _first(done, "get_flight_status")
    alts = _first(done, "find_alternatives")
    wants_options = any(w in question.lower() for w in ("option", "rebook", "cancel"))
    if status is None:
        calls = [_sim.tool_use("get_flight_status", {"flight": b["flight"], "date": b["date"]})]
        if wants_options:
            # Independent lookups: Claude asks for both in one turn.
            calls.append(_sim.tool_use("find_alternatives", {"flight": b["flight"], "date": b["date"]}))
        return _sim.message(_sim.thinking(""), *calls)
    if status[3]:
        return _sim.message(_sim.text(
            f"I couldn't reach live flight status for {b['flight']} just now. "
            "Please check again in a few minutes, or I can have an agent call you."))
    s = json.loads(status[2])
    parts = [f"Your flight {b['flight']} on {b['date']} is {s['status']}."]
    if s["status"] == "delayed":
        parts.append(f"It's running about {s['delay_minutes']} minutes late, departing from gate {s['gate']}.")
    if alts and not alts[3]:
        opts = json.loads(alts[2])["options"]
        if opts:
            listed = " or ".join(f"{o['flight']} ({o['departs'].replace('T', ' ')}, {o['seats']} seats left)" for o in opts)
            parts.append(f"I can move you to {listed}.")
    return _sim.message(_sim.text(" ".join(parts)))


_sim.set_responder(_responder)
