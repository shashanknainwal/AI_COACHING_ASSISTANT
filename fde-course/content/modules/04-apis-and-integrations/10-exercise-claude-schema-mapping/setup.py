import json
from anthropic import _sim

# What Claude suggested for Polar Express (including two realistic mistakes).
_SUGGESTIONS = {"mappings": [
    {"source": "trk_no", "target": "external_id", "transform": "none", "confidence": 0.97},
    {"source": "state", "target": "status", "transform": "lookup", "confidence": 0.9},
    {"source": "wt_kg", "target": "weight_kg", "transform": "none", "confidence": 0.95},
    {"source": "amount", "target": "charge", "transform": "type_cast", "confidence": 0.86},
    {"source": "recipient", "target": "customer_name", "transform": "none", "confidence": 0.92},
    {"source": "dest_city", "target": "city", "transform": "none", "confidence": 0.74},
    {"source": "last_event_ts", "target": "source_updated_at", "transform": "date_format", "confidence": 0.83},
    {"source": "svc_level", "target": "status", "transform": "lookup", "confidence": 0.41},
]}


def _responder(params):
    return json.dumps(_SUGGESTIONS)


_sim.set_responder(_responder)
