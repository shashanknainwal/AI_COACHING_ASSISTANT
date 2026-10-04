import json
from anthropic import _sim

# Stand-in for the triage model: mostly right, with the kinds of mistakes real models make.
_PREDICTIONS = {
    "T-07": ("damaged_item", "normal"),   # missed the safety signal
    "T-10": ("billing", "normal"),
    "T-13": ("billing", "high"),          # fraud read as a billing issue
    "T-16": ("damaged_item", "low"),      # "crushed" without damage
    "T-17": ("returns", "normal"),        # "return" outweighed "damaged"
}
_INFRA_ERROR = {"T-12"}
_CUES = [("damaged_item", ("broken", "tear", "shattered", "damaged", "crushed")), ("returns", ("return", "send back")),
         ("billing", ("charged", "fee", "credit", "membership", "refund")), ("account", ("log in", "account", "password")),
         ("order_status", ("where is", "late", "processing", "arrive", "order b-"))]


def _responder(params):
    from fde_datasets import brightway
    text = str(params["messages"][-1]["content"]).split("<ticket>", 1)[-1].split("</ticket>", 1)[0].strip()
    case = next((c for c in brightway.EVAL_TICKETS if c["text"] == text), None)
    if case and case["id"] in _INFRA_ERROR:
        return _sim.overloaded()
    if case and case["id"] in _PREDICTIONS:
        category, urgency = _PREDICTIONS[case["id"]]
    elif case:
        category, urgency = case["category"], case["urgency"]
    else:
        low = text.lower()
        category = next((c for c, cues in _CUES if any(k in low for k in cues)), "other")
        urgency = "high" if any(k in low for k in ("twice", "sparks", "didn't make", "!")) else "normal"
    return json.dumps({"category": category, "urgency": urgency})


_sim.set_responder(_responder)
