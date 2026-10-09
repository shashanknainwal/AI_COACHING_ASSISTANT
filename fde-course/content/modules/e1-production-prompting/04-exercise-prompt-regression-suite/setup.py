import json
from anthropic import _sim

# Stand-in for Claude reading Tallis Freight invoices. What it returns depends on the
# prompt version (v2 is recognised by its <vendor_rules> section) and on the invoice.
_TRUTH = {
    "BT-5521": {"vendor": "Brannock Tools", "invoice_number": "BT-5521", "total": 1200.0, "currency": "GBP", "due_date": "2026-11-01"},
    "SP-0098": {"vendor": "Sorrel & Pike", "invoice_number": "SP-0098", "total": 86.5, "currency": "EUR", "due_date": "2026-10-20"},
    "QM-77120": {"vendor": "Quillon Metals", "invoice_number": "QM-77120", "total": 15400.0, "currency": "USD", "due_date": "2026-12-15"},
    "HL-3301": {"vendor": "Harrow Logistics", "invoice_number": "HL-3301", "total": 2310.4, "currency": "CAD", "due_date": "2026-11-30"},
    "VOS-118": {"vendor": "Vantor Office Supply", "invoice_number": "VOS-118", "total": 412.99, "currency": "USD", "due_date": None},
    "EP-2290": {"vendor": "Elsted Print Co", "invoice_number": "EP-2290", "total": 980.0, "currency": "EUR", "due_date": "2026-10-31"},
    "ML-0042": {"vendor": "Marrick Labs", "invoice_number": "ML-0042", "total": 7250.0, "currency": "CHF", "due_date": "2026-11-15"},
    "PC-1187": {"vendor": "Pellow Catering", "invoice_number": "PC-1187", "total": 640.25, "currency": "GBP", "due_date": "2026-10-25"},
    "OL-5510": {"vendor": "Tamsin & Lind", "invoice_number": "OL-5510", "total": 3100.0, "currency": "USD", "due_date": "2026-11-05"},
    "RE-8812": {"vendor": "Rydal Electrical", "invoice_number": "RE-8812", "total": 1875.6, "currency": "EUR", "due_date": "2026-12-01"},
}
_V1_MISTAKES = {
    "SP-0098": {"vendor": "Sorrel and Pike"},
    "HL-3301": {"vendor": "Harrow Logistics Inc."},
    "OL-5510": {"vendor": "Tamsin & Lind LLP"},
    "EP-2290": {"due_date": "2026-10-01"},
    "ML-0042": {"total": 7.25},
}
_V2_MISTAKES = {
    "VOS-118": {"due_date": "2026-11-02"},
    "EP-2290": {"currency": "USD"},
    "PC-1187": {"currency": "USD"},
}


def _responder(params):
    content = params["messages"][-1]["content"]
    text = content if isinstance(content, str) else ""
    number = next((n for n in _TRUTH if n in text), None)
    if number is None:
        reply = {"vendor": "unknown", "invoice_number": "unknown", "total": 0, "currency": "USD", "due_date": None}
    else:
        mistakes = _V2_MISTAKES if "<vendor_rules>" in str(params.get("system", "")) else _V1_MISTAKES
        reply = dict(_TRUTH[number], **mistakes.get(number, {}))
    return [_sim.thinking(), _sim.text(json.dumps(reply))]


_sim.set_responder(_responder)
