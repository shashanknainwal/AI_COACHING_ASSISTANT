from anthropic import _sim

_REPLIES = {
    "wire": "International wires cost $35 to send and $15 to receive. Domestic wires are $25.",
    "domestic": "Domestic wires are $25 to send and free to receive.",
    "dispute": "To dispute a card charge, open the transaction in online banking and choose Dispute, or call 1-800-555-0100.",
    "password": "I can't help with getting into someone else's account.",
}


def _responder(params):
    last = params["messages"][-1]["content"]
    text = (last if isinstance(last, str) else str(last)).lower()
    if "neighbor" in text:
        return _sim.refusal(category=None)
    for cue, reply in _REPLIES.items():
        if cue in text:
            return _sim.message(_sim.thinking(""), _sim.text(reply))
    return _sim.message(_sim.thinking(""), _sim.text("Could you tell me a bit more about what you need?"))


_sim.set_responder(_responder)
