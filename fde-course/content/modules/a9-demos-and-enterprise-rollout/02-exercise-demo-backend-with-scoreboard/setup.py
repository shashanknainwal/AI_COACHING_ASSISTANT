# Halberd Freight Group (fictional freight forwarder): carrier-invoice audit demo.
# Twenty carrier invoices from Halberd's own (anonymised) audit backlog, each labelled
# by Bas Achterberg's freight-audit team (fictional) with the answer an auditor gave.
# The carriers are fictional too. The simulated Claude below answers like a real model
# would on these documents: mostly right, sometimes wrong, once refused.
import json
import anthropic
from anthropic import _sim

client = anthropic.Anthropic()
MODEL = "claude-sonnet-5-5"
FIELDS = ["invoice_number", "shipment_ref", "total_eur"]


def _invoice(carrier, inv, ref, lane, line_haul, fuel, total_line=None, extra=None):
    total = line_haul + fuel
    lines = [
        "CARRIER INVOICE",
        f"Carrier: {carrier}",
        f"Invoice no: {inv}",
        f"Shipment ref: {ref}",
    ]
    if extra:
        lines.append(extra)
    lines += [
        f"Lane: {lane}",
        f"Line haul: EUR {line_haul:,.2f}",
        f"Fuel surcharge: EUR {fuel:,.2f}",
        total_line or f"Total due: EUR {total:,.2f}",
    ]
    return "\n".join(lines), total


def _field(value, quote):
    return {"value": value, "quote": quote}


# (id, carrier, invoice no, shipment ref, lane, line haul, fuel, agreed EUR, label, options)
_SPEC = [
    ("H01", "Vossberg Transport BV", "VT-24-1187", "HFG-88213", "Rotterdam -> Duisburg", 1180, 142, 1322, "match", {}),
    ("H02", "Elbstrom Logistik GmbH", "EL-55021", "HFG-88240", "Hamburg -> Prague", 2450, 310, 2480, "overcharge", {}),
    ("H03", "Brackwater Haulage Ltd", "NG-7781", "HFG-88302", "Felixstowe -> Rotterdam", 1890, 205, 2095, "match", {}),
    ("H04", "Wisla Cargo Sp. z o.o.", "WC/2026/0412", "HFG-88317", "Poznan -> Duisburg", 1320, 160, 1480, "match", {}),
    ("H05", "Vossberg Transport BV", "VT-24-1203", "HFG-88355", "Rotterdam -> Antwerp", 640, 70, 640, "overcharge", {}),
    ("H06", "Elbstrom Logistik GmbH", "EL-55088", "HFG-88371", "Hamburg -> Munich", 1980, 240, 2220, "match", {}),
    ("H07", "Brackwater Haulage Ltd", "NG-7802", "HFG-88390", "Felixstowe -> Birmingham", 720, 88, 808, "match", {}),
    ("H08", "Wisla Cargo Sp. z o.o.", "WC/2026/0431", "HFG-88402", "Gdansk -> Berlin", 1560, 190, 1610, "overcharge", {}),
    ("H09", "Vossberg Transport BV", "VT-24-1219", "HFG-88415", "Rotterdam -> Dusseldorf", 820, 84, 900, "match", {}),
    # Scan damage: the total can't be read. The right answer is "don't know".
    ("H10", "Elbstrom Logistik GmbH", "EL-55102", "HFG-88428", "Hamburg -> Leipzig", 1050, 150, 1200, "abstain",
     {"total_line": "Total due: [illegible - scan damaged]", "reply": {"total_eur": _field(None, None)}}),
    # The total is on a separate statement. The model invents one anyway.
    ("H11", "Brackwater Haulage Ltd", "NG-7815", "HFG-88433", "Tilbury -> Zeebrugge", 1300, 200, 1500, "abstain",
     {"total_line": "Total due: see attached statement",
      "reply": {"total_eur": _field(1500.0, "Total due: EUR 1,500.00")}}),
    # A shipment reference that isn't in Halberd's records.
    ("H12", "Wisla Cargo Sp. z o.o.", "WC/2026/0449", "HFG-99999", "Katowice -> Venlo", 1400, 170, None, "abstain", {}),
    # A dangerous-goods lane. The simulated safety classifier declines (a false positive).
    ("H13", "Elbstrom Logistik GmbH", "EL-55117", "HFG-88447", "Hamburg -> Linz (ADR class 3 fuel tanks)", 2100, 260, 2200,
     "overcharge", {"refuse": True}),
    # The model picks the line-haul subtotal instead of the total. The quote is real, so grounding can't catch it.
    ("H14", "Brackwater Haulage Ltd", "NG-7840", "HFG-88460", "Felixstowe -> Leeds", 1450, 180, 1450, "overcharge",
     {"reply": {"total_eur": _field(1450.0, "Line haul: EUR 1,450.00")}}),
    # The model takes the carrier's own reference instead of Halberd's shipment reference.
    ("H15", "Wisla Cargo Sp. z o.o.", "WC/2026/0457", "HFG-88477", "Wroclaw -> Duisburg", 1290, 150, 1440, "match",
     {"extra": "Carrier ref: WC-REF-3391", "reply": {"shipment_ref": _field("WC-REF-3391", "Carrier ref: WC-REF-3391")}}),
    ("H16", "Vossberg Transport BV", "VT-24-1240", "HFG-88490", "Rotterdam -> Cologne", 930, 95, 1025, "match", {}),
    ("H17", "Elbstrom Logistik GmbH", "EL-55140", "HFG-88502", "Bremen -> Wroclaw", 1710, 205, 1700, "overcharge", {}),
    ("H18", "Brackwater Haulage Ltd", "NG-7866", "HFG-88515", "Southampton -> Rotterdam", 2240, 260, 2500, "match", {}),
    ("H19", "Wisla Cargo Sp. z o.o.", "WC/2026/0470", "HFG-88530", "Lodz -> Venlo", 1380, 165, 1530, "match", {}),
    ("H20", "Vossberg Transport BV", "VT-24-1262", "HFG-88544", "Rotterdam -> Liege", 610, 66, 676, "match", {}),
]

CASES = []
SHIPMENTS = {}
_REPLIES = {}   # invoice text -> scripted model behaviour

for cid, carrier, inv, ref, lane, lh, fuel, agreed, label, opt in _SPEC:
    text, total = _invoice(carrier, inv, ref, lane, lh, fuel, opt.get("total_line"), opt.get("extra"))
    CASES.append({"id": cid, "invoice_text": text, "label": label})
    if agreed is not None:
        SHIPMENTS[ref] = {"agreed_eur": float(agreed), "lane": lane}
    reply = {
        "invoice_number": _field(inv, f"Invoice no: {inv}"),
        "shipment_ref": _field(ref, f"Shipment ref: {ref}"),
        "total_eur": _field(float(total), f"Total due: EUR {total:,.2f}"),
    }
    reply.update(opt.get("reply", {}))
    _REPLIES[text] = "REFUSE" if opt.get("refuse") else reply


def _user_text(params):
    content = params["messages"][-1].get("content", "")
    if isinstance(content, list):
        content = "\n".join(b.get("text", "") for b in content if isinstance(b, dict))
    return str(content)


def _responder(params):
    said = _user_text(params)
    fmt = (params.get("output_config") or {}).get("format")
    for text, reply in _REPLIES.items():
        if text in said:
            if reply == "REFUSE":
                return _sim.refusal("cyber")
            if not fmt:
                # Without a schema, the model answers in prose: nothing a parser can trust.
                total = reply["total_eur"]["value"]
                return _sim.message(_sim.thinking(""), _sim.text(f"Sure! The invoice total looks like EUR {total}."))
            return _sim.message(_sim.thinking(""), _sim.text(json.dumps(reply)))
    return _sim.message(_sim.thinking(""), _sim.text(json.dumps(
        {f: _field(None, None) for f in FIELDS})))


def _install_responder():
    _sim.set_responder(_responder)


_install_responder()
