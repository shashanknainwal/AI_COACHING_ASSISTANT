import json
import fde_clock
from anthropic import _sim


def _responder(params):
    fde_clock.advance(0.84)   # pretend the API took 840 ms
    return json.dumps({"category": "order_status", "urgency": "normal"})


_sim.set_responder(_responder)
