import json
from anthropic import _sim


# The demo's first three tickets arrive during a simulated API outage.
_OUTAGE = ("where is my order?", "my lamp arrived broken", "where is b-1004?")


def _responder(params):
    text = str(params["messages"][-1]["content"]).lower()
    if any(f"<ticket>\n{t}\n</ticket>" in text for t in _OUTAGE):
        return _sim.overloaded()
    category = "damaged_item" if "broken" in text else "order_status" if "where" in text else "other"
    return json.dumps({"category": category, "urgency": "normal"})


_sim.set_responder(_responder)
