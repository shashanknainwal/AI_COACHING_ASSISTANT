from anthropic import _sim

_REPLIES = {
    "wire": "International wires cost $35 to send and $15 to receive. Domestic wires are $25.",
    "domestic": "Domestic wires are $25 to send and free to receive.",
    "dispute": "To dispute a card charge, open the transaction in online banking and choose Dispute, or call 1-800-555-0100.",
    "password": "I can't help with getting into someone else's account.",
}

SIM_SUMMARY = ("The agent asked about wire fees: international wires are $35 to send and $15 to receive; "
               "domestic wires are $25 to send and free to receive.")


def _newest_text(params):
    """Text of the newest block in the newest message (ignores an injected summary block)."""
    content = params["messages"][-1]["content"]
    if isinstance(content, list):
        texts = [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
        return texts[-1] if texts else ""
    return content


def _responder(params):
    text = _newest_text(params).lower()
    if "summarize" in text:
        return _sim.message(_sim.thinking(""), _sim.text(SIM_SUMMARY))
    if "neighbor" in text:
        return _sim.refusal(category=None)
    for cue, reply in _REPLIES.items():
        if cue in text:
            return _sim.message(_sim.thinking(""), _sim.text(reply))
    return _sim.message(_sim.thinking(""), _sim.text("Could you tell me a bit more about what you need?"))


_sim.set_responder(_responder)
