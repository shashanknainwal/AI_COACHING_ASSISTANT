from anthropic import _sim


def _responder(params):
    return _sim.message(_sim.text(f"[answered by {params['model']}]"))


_sim.set_responder(_responder)
