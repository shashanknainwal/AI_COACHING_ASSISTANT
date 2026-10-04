from anthropic import _sim


def _responder(params):
    return _sim.message(_sim.thinking(""), _sim.text("Wire cutoff is 4pm Eastern on business days."))


_sim.set_responder(_responder)
