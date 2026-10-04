import json
from anthropic import _sim

_CUES = [("damaged_item", ("broken", "tear", "shattered", "damaged", "sparks")), ("returns", ("return", "send back")),
         ("billing", ("charged", "fee", "credit", "membership")), ("account", ("log in", "account")),
         ("order_status", ("where is", "late", "processing", "arrive"))]


def _responder(params):
    text = str(params["messages"][-1]["content"]).lower()
    category = next((c for c, cues in _CUES if any(k in text for k in cues)), "other")
    return json.dumps({"category": category, "urgency": "normal"})


_sim.set_responder(_responder)
