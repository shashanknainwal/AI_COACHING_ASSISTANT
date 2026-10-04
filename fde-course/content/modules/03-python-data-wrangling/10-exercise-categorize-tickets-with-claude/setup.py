import json
import re
from anthropic import _sim

# A stand-in for Claude's judgment on Cobalt's tickets: reads each numbered line
# of the prompt and returns a category for it.
_CUES = [
    ("product defect", ("hiss", "crack", "leak", "seal", "defect", "doesn't fit", "wrong size", "snapped")),
    ("shipping", ("arrive", "late", "delivery", "courier", "box", "pallet", "shipped")),
    ("billing", ("charged", "credit", "payment", "price", "po number")),
    ("account access", ("locked out", "portal", "sign in", "2fa")),
]


def _categorize(text):
    t = text.lower()
    for category, cues in _CUES:
        if any(c in t for c in cues):
            return category
    return "other"


def _responder(params):
    prompt = params["messages"][-1]["content"]
    results = []
    for line in str(prompt).splitlines():
        m = re.match(r"^(\d+)\. (.*)$", line.strip())
        if m:
            results.append({"index": int(m.group(1)), "category": _categorize(m.group(2))})
    return json.dumps({"results": results})


_sim.set_responder(_responder)
