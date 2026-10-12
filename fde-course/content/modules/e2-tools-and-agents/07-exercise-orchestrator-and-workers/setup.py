import json
import re
from anthropic import _sim

_REF = re.compile(r"\b[A-Z]{2}\d[A-Z]\d[A-Z]\b")


def _text(content):
    if isinstance(content, list):
        return " ".join(b.get("text", "") for b in content if isinstance(b, dict))
    return str(content)


def _results(params):
    """[(tool name, input, content, is_error)] for every answered tool call."""
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


def _report(ref, traveler, affected, status, options, rationale):
    return _sim.message(_sim.thinking(""), _sim.text(json.dumps({
        "booking_ref": ref, "traveler": traveler, "affected": affected, "status": status,
        "options": options, "rationale": rationale})))


def _worker(params):
    refs = _REF.findall(_text(params["messages"][0]["content"]))
    if not refs:
        return _sim.message(_sim.text('{"error": "no booking reference in the task"}'))
    ref = refs[0]
    if ref == "KM2B7Y":
        return _sim.overloaded()           # this worker's calls never get through
    done = _results(params)
    if ref == "BX8C3J":                     # a wandering worker: keeps re-checking the booking
        return _sim.message(_sim.thinking(""), _sim.tool_use("get_booking", {"booking_ref": ref}))
    booking = next((d for d in done if d[0] == "get_booking"), None)
    if booking is None:
        return _sim.message(_sim.thinking(""), _sim.tool_use("get_booking", {"booking_ref": ref}))
    if booking[3]:
        return _report(ref, "unknown", "unknown", "unknown", [], "The booking lookup failed.")
    b = json.loads(booking[2])
    status = next((d for d in done if d[0] == "get_flight_status"), None)
    if status is None:
        return _sim.message(_sim.thinking(""), _sim.tool_use("get_flight_status", {"flight": b["flight"], "date": b["date"]}))
    if status[3]:
        return _report(ref, b["traveler"], "unknown", "unknown", [], "The flight-status lookup failed, so the status is unknown.")
    s = json.loads(status[2])
    alts = next((d for d in done if d[0] == "find_alternatives"), None)
    if s["status"] == "cancelled" and alts is None:
        return _sim.message(_sim.thinking(""), _sim.tool_use("find_alternatives", {"flight": b["flight"], "date": b["date"]}))
    options = [f"{o['flight']} departing {o['departs'].replace('T', ' ')}" for o in json.loads(alts[2])["options"]] if alts and not alts[3] else []
    affected = "no" if s["status"] == "on_time" else "yes"
    why = {"on_time": f"{b['flight']} is on time.", "delayed": f"{b['flight']} is delayed {s['delay_minutes']} minutes.",
           "cancelled": f"{b['flight']} is cancelled."}[s["status"]]
    return _report(ref, b["traveler"], affected, s["status"], options, why)


def _lead(params):
    text = _text(params["messages"][-1]["content"])
    m = re.search(r"<reports>\s*(.*?)\s*</reports>", text, re.S)
    n = re.search(r"<not_checked>(.*?)</not_checked>", text, re.S)
    try:
        reports = json.loads(m.group(1)) if m else []
    except ValueError:
        reports = []
    lines = []
    for r in reports:
        if r.get("affected") == "yes":
            extra = f" Options: {'; '.join(r['options'])}." if r.get("options") else ""
            lines.append(f"{r['traveler']} ({r['booking_ref']}) is affected: {r['status']}.{extra}")
    fine = [r["booking_ref"] for r in reports if r.get("affected") == "no"]
    unknown = [r["booking_ref"] for r in reports if r.get("affected") == "unknown"]
    if fine:
        lines.append("Not affected: " + ", ".join(fine) + ".")
    if unknown:
        lines.append("Status unknown, check by phone: " + ", ".join(unknown) + ".")
    missing = n.group(1).strip() if n else ""
    if missing and missing != "none":
        lines.append("Not checked (researcher failed): " + missing + ".")
    return _sim.message(_sim.thinking(""), _sim.text(" ".join(lines) or "No reports received."))


def _responder(params):
    if params["model"].startswith("claude-haiku"):
        return _worker(params)
    return _lead(params)


_sim.set_responder(_responder)
