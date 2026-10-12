import json
import math


def route(doc):
    """Decide how a document enters the pipeline. See the routing table."""
    # TODO: check the rules in order and return the routing dict
    return {"action": "extract", "block": None, "source": None, "citable": False,
            "est_visual_tokens": None, "reason": None}


def estimate_image_tokens(width, height):
    """Visual tokens on the high-resolution tier, after downscaling."""
    # TODO: scale so the long edge fits HIRES_LONG_EDGE, then ceil(w/28) * ceil(h/28), capped
    return None


def build_request(doc, file_id=None):
    """Keyword arguments for client.messages.create(...)."""
    # TODO: document or image block first (base64 or file source), then INSTRUCTIONS
    return {}


def validate_line(line, doc, erp_lines):
    """Return (status, reason) for one extracted line."""
    # TODO: evidence first, then ERP
    return "accept", None


def process_inbox(client, inbox, erp, upload):
    """Route, extract and validate every document. Returns one dict per document."""
    results = []
    # TODO
    return results


# --- Try it out (not graded) ---
if __name__ == "__main__":
    for d in INBOX:
        print(d["filename"], route(d))
    for res in process_inbox(client, INBOX, ERP_OPEN_POS, upload):
        print(res)
