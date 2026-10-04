import json
from anthropic import _sim

# Stand-in for Claude classifying the ticket inside <ticket> tags.
_CUES = [
    ("fraud_report", ("never made", "didn't make", "not me", "stolen", "unauthorized")),
    ("card_dispute", ("charged twice", "charged me twice", "double charge", "wrong amount", "never arrived", "refund from the merchant")),
    ("account_access", ("locked out", "password", "can't log in", "two-factor")),
    ("fees", ("fee", "charged $35", "overdraft")),
    ("loans", ("mortgage", "loan", "refinance")),
]


def _responder(params):
    content = str(params["messages"][-1]["content"])
    body = content.split("<ticket>", 1)[-1].rsplit("</ticket>", 1)[0].lower()
    if "ignore all previous instructions" in body or "&lt;/ticket&gt;" in body:
        result = {"category": "other", "needs_human": True,
                  "reason": "The ticket contains instructions aimed at the classifier; flagged for review."}
    else:
        category = next((c for c, cues in _CUES if any(k in body for k in cues)), "other")
        result = {"category": category, "needs_human": category == "other",
                  "reason": f"Matches the definition of {category}."}
    return json.dumps(result)


_sim.set_responder(_responder)
