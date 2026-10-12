import re
import anthropic
from anthropic import _sim
from anthropic._types import TextBlock

MODEL = "claude-sonnet-5-5"
MAX_TOKENS = 2000
MIN_UNCITED_WORDS = 6
INSUFFICIENT = "I can't find that in Tallowmere's policies. I've passed your question to the order desk."
REFUSAL_MESSAGE = "I can't help with that one. Please contact the order desk."

POLICY_DOCS = [
    {"id": "POL-RET-07", "title": "Returns policy v7",
     "text": ("Unopened stock items can be returned within 30 days of delivery. "
              "Restocking is free for unopened stock items. "
              "Cable cut to customer length is non-returnable except for manufacturing faults. "
              "Faulty goods must be reported within 14 days of delivery with photos of the fault.")},
    {"id": "POL-WAR-03", "title": "Warranty terms",
     "text": ("Power tools carry a 24-month manufacturer warranty. "
              "Consumables such as gloves, ear plugs and cable ties carry no warranty beyond the returns window. "
              "Warranty claims need the original order number.")},
    {"id": "POL-DEL-02", "title": "Delivery and freight",
     "text": ("Orders placed before 2 p.m. ship the same working day. "
              "Freight is free on orders over 400 dollars. "
              "Cut-to-length cable ships one working day later than stock items.")},
    {"id": "POL-PAY-05", "title": "Payment terms",
     "text": ("Account customers pay on Net 30 terms. "
              "Card payments are charged when the order ships.")},
]

_KEYWORDS = {
    "POL-RET-07": {"return", "returned", "returns", "restocking", "refund", "faulty", "cut", "cable", "unopened"},
    "POL-WAR-03": {"warranty", "gloves", "consumables", "tools", "claim"},
    "POL-DEL-02": {"ship", "shipping", "freight", "delivery", "cut", "cable"},
    "POL-PAY-05": {"pay", "payment", "invoice", "card", "terms"},
}


def search(question, k=3):
    """Up to k policy documents, best first. Returns [] when nothing matches."""
    words = set(re.findall(r"[a-z]+", question.lower()))
    scored = [(len(words & _KEYWORDS[d["id"]]), i, d) for i, d in enumerate(POLICY_DOCS)]
    scored = [s for s in scored if s[0] > 0]
    scored.sort(key=lambda s: (-s[0], s[1]))
    return [dict(d) for _, _, d in scored[:k]]


class Citation:
    """Shape of a char_location citation, as the real SDK returns it (attribute access)."""

    def __init__(self, cited_text, document_index, document_title, start_char_index, end_char_index):
        self.type = "char_location"
        self.cited_text = cited_text
        self.document_index = document_index
        self.document_title = document_title
        self.start_char_index = start_char_index
        self.end_char_index = end_char_index

    def __repr__(self):
        return f"Citation(doc={self.document_index}, chars={self.start_char_index}-{self.end_char_index}, {self.cited_text!r})"


class CitedTextBlock(TextBlock):
    _fields = ("type", "text", "citations")

    def __init__(self, text, citations=None):
        super().__init__(text)
        self.citations = citations


def _docs_in(params):
    out = []
    for m in params["messages"]:
        if isinstance(m.get("content"), list):
            out += [b for b in m["content"] if isinstance(b, dict) and b.get("type") == "document"]
    return out


def _cite(sent_docs, doc_id, sentence):
    for i, b in enumerate(sent_docs):
        if doc_id in str(b.get("context", "")) or b.get("title") == next(d["title"] for d in POLICY_DOCS if d["id"] == doc_id):
            text = b["source"]["data"]
            start = text.index(sentence)
            return Citation(sentence, i, b.get("title"), start, start + len(sentence))
    raise KeyError(doc_id)


def _block(sent_docs, text, *cites):
    return CitedTextBlock(text, [_cite(sent_docs, d, s) for d, s in cites] or None)


def _responder(params):
    docs = _docs_in(params)
    if not docs or not all((b.get("citations") or {}).get("enabled") for b in docs):
        return _sim.text("Cut-to-length cable can't be returned [POL-RET-07].")
    q = params["messages"][-1]["content"][-1].get("text", "").lower()
    B = lambda text, *c: _block(docs, text, *c)
    if "cut" in q:
        return [_sim.thinking(""),
                B("Cut-to-length cable "),
                B("can't be returned unless it has a manufacturing fault",
                  ("POL-RET-07", "Cable cut to customer length is non-returnable except for manufacturing faults.")),
                B(". If it is faulty, "),
                B("report it within 14 days of delivery with photos",
                  ("POL-RET-07", "Faulty goods must be reported within 14 days of delivery with photos of the fault.")),
                B(".")]
    if "restocking" in q:
        return [_sim.thinking(""),
                B("There is no restocking fee: ",),
                B("restocking is free for unopened stock items",
                  ("POL-RET-07", "Restocking is free for unopened stock items.")),
                B(", "),
                B("as long as you return them within 30 days",
                  ("POL-RET-07", "Unopened stock items can be returned within 30 days of delivery.")),
                B(". Most customers get their refund within two working days.")]
    if "gloves" in q:
        return [_sim.thinking(""),
                B("Gloves are consumables, so "),
                B("they have no warranty beyond the returns window",
                  ("POL-WAR-03", "Consumables such as gloves, ear plugs and cable ties carry no warranty beyond the returns window.")),
                B(". You can return unopened boxes "),
                B("within 30 days",
                  ("POL-RET-07", "Unopened stock items can be returned within 30 days of delivery."),
                  ("POL-RET-07", "Unopened stock items can be returned within 30 days of delivery.")),
                B(", and "),
                B("faulty ones must be reported within 14 days",
                  ("POL-RET-07", "Faulty goods must be reported within 14 days of delivery with photos of the fault."),
                  ("POL-WAR-03", "Consumables such as gloves, ear plugs and cable ties carry no warranty beyond the returns window.")),
                B(".")]
    return _sim.text("I don't know.")


_sim.set_responder(_responder)
client = anthropic.Anthropic()
