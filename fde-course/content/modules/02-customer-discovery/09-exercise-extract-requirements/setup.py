import json
from anthropic import _sim

_RESULT = {
    "requirements": [
        {"title": "Read claim emails and PDF attachments automatically", "type": "integration", "priority": "must",
         "evidence": "Claims come in by email, about 900 a week"},
        {"title": "Pre-fill policy number, claimant and loss date in ClaimsPro", "type": "functional", "priority": "must",
         "evidence": "keys it into ClaimsPro by hand"},
        {"title": "Highlight low-confidence fields for adjuster review", "type": "functional", "priority": "should",
         "evidence": "18% of claims get sent back because a field was keyed wrong"},
        {"title": "Weekly report of rework rate", "type": "non-functional", "priority": "could",
         "evidence": "That and cost per claim"},
        {"title": "Keep claim data inside Lumen's cloud tenant", "type": "security", "priority": "must",
         "evidence": "Ravi wants data to stay in our tenant"},
        {"title": "pre-fill policy number, claimant and loss date in ClaimsPro ", "type": "functional", "priority": "should",
         "evidence": "re-key everything"},
    ],
    "open_questions": [
        "Does ClaimsPro have an API, or do we need to use its import files?",
        "Which claim types are in scope for phase 1?",
    ],
}


def _responder(params):
    return json.dumps(_RESULT)


_sim.set_responder(_responder)
