import json
import re
from anthropic import _sim

# Stand-in for Claude answering from the <documents> it was given.
# Each rule: (cue words that must all appear in the question, chunks needed, answer).
_RULES = [
    (("late", "gold"), ["KB-02#2", "KB-02#3"],
     "Gold members get a $25 store credit when an order arrives more than 5 business days late."),
    (("late",), ["KB-02#2"],
     "If your order arrives more than 5 business days late, you can request a $20 store credit."),
    (("sofa",), ["KB-01#2"],
     "Yes. Sofas can be returned within 14 days of delivery, and a $49 pickup fee applies."),
    (("gift card",), ["KB-08#1"], "Gift cards are delivered by email within an hour."),
    (("cancel", "shipped"), ["KB-06#2"],
     "Once an order has shipped it can't be cancelled, but you can return it under the returns policy."),
    (("cancel",), ["KB-06#1"], "You can change or cancel an order free of charge while it is still processing."),
    (("damaged",), ["KB-03#1"], "Send a photo of the damaged item within 7 days of delivery."),
]


def _responder(params):
    prompt = params["messages"][-1]["content"]
    question = prompt.split("<question>", 1)[-1].split("</question>", 1)[0].lower()
    doc_ids = re.findall(r'<document id="([^"]+)"', prompt)
    for cues, needed, text in _RULES:
        if all(c in question for c in cues):
            if all(n in doc_ids for n in needed):
                return json.dumps({"answer": text, "citations": needed, "answerable": True})
            break
    return json.dumps({"answer": "The documents don't cover this question.", "citations": [], "answerable": False})


_sim.set_responder(_responder)
