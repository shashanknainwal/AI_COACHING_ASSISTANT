import json
import anthropic

# Loaded for you: client, MODEL, FIELDS, CASES, SHIPMENTS

SYSTEM = (
    "You extract fields from a carrier invoice for Halberd Freight Group's freight-audit team. "
    "For each field return the value and the exact line of the invoice it came from, copied verbatim. "
    "shipment_ref is Halberd's reference (it starts with HFG-), never the carrier's own reference. "
    "total_eur is the total due, not a subtotal. If a field is missing or unreadable, return null for "
    "both value and quote. Never estimate or infer a value that isn't printed on the invoice."
)

_FIELD_SCHEMA = {
    "type": "object",
    "properties": {
        "value": {"type": ["string", "null"]},
        "quote": {"type": ["string", "null"]},
    },
    "required": ["value", "quote"],
    "additionalProperties": False,
}
SCHEMA = {
    "type": "object",
    "properties": {
        "invoice_number": _FIELD_SCHEMA,
        "shipment_ref": _FIELD_SCHEMA,
        "total_eur": {
            "type": "object",
            "properties": {"value": {"type": ["number", "null"]}, "quote": {"type": ["string", "null"]}},
            "required": ["value", "quote"],
            "additionalProperties": False,
        },
    },
    "required": FIELDS,
    "additionalProperties": False,
}


def extract(client, invoice_text):
    """Endpoint 1: ask Claude for the three fields, each with a verbatim quote."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        system=SYSTEM,
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": SCHEMA}},
        messages=[{"role": "user", "content": f"Extract the fields from this invoice.\n\n<invoice>\n{invoice_text}\n</invoice>"}],
    )
    if response.stop_reason == "refusal":
        category = getattr(response.stop_details, "category", None)
        return {"status": "refused", "category": category}
    if response.stop_reason != "end_turn":
        return {"status": "error", "detail": f"stop_reason {response.stop_reason}"}
    text = "".join(b.text for b in response.content if b.type == "text")
    try:
        fields = json.loads(text)
    except ValueError:
        return {"status": "error", "detail": "response was not JSON"}
    if not isinstance(fields, dict):
        return {"status": "error", "detail": "response was not a JSON object"}
    return {"status": "ok", "fields": fields}


def ground(fields, invoice_text, shipments):
    """Endpoint 2: check every field against the invoice and Halberd's records, in code."""
    for f in FIELDS:
        item = fields.get(f) or {}
        if item.get("value") is None:
            return {"verdict": "abstain", "reason": f"missing {f}", "difference_eur": None}
    for f in FIELDS:
        quote = fields[f].get("quote")
        if not quote or quote not in invoice_text:
            return {"verdict": "abstain", "reason": f"unsupported {f}", "difference_eur": None}
    ref = fields["shipment_ref"]["value"]
    if ref not in shipments:
        return {"verdict": "abstain", "reason": f"unknown shipment {ref}", "difference_eur": None}
    agreed = shipments[ref]["agreed_eur"]
    total = float(fields["total_eur"]["value"])
    diff = round(total - agreed, 2)
    if diff > max(5.0, 0.01 * agreed):
        return {"verdict": "overcharge", "reason": f"invoiced {total:.2f} vs agreed {agreed:.2f}", "difference_eur": diff}
    return {"verdict": "match", "reason": "within tolerance", "difference_eur": diff}


def cite(fields, invoice_text):
    """Endpoint 3: where on the invoice each value came from (1-based line numbers)."""
    lines = invoice_text.splitlines()
    out = []
    for f in FIELDS:
        quote = (fields.get(f) or {}).get("quote")
        if not quote:
            continue
        line = next((i + 1 for i, l in enumerate(lines) if quote in l), None)
        out.append({"field": f, "line": line, "quote": quote})
    return out


def run_case(client, case, shipments):
    """Run one invoice through extract, ground and cite."""
    base = {"id": case["id"], "citations": []}
    try:
        got = extract(client, case["invoice_text"])
    except anthropic.APIError as exc:
        return {**base, "verdict": "error", "reason": type(exc).__name__}
    if got["status"] == "refused":
        return {**base, "verdict": "refused", "reason": f"refusal ({got.get('category')})"}
    if got["status"] != "ok":
        return {**base, "verdict": "error", "reason": got.get("detail", "error")}
    g = ground(got["fields"], case["invoice_text"], shipments)
    return {**base, "verdict": g["verdict"], "reason": g["reason"], "citations": cite(got["fields"], case["invoice_text"])}


def scoreboard(client, cases, shipments):
    """Honest metrics over every labelled case. Nothing is dropped from the denominator."""
    rows = [run_case(client, c, shipments) for c in cases]
    n = len(cases)
    labels = {c["id"]: c["label"] for c in cases}
    correct = sum(1 for r in rows if r["verdict"] == labels[r["id"]])
    answered = [r for r in rows if r["verdict"] in ("match", "overcharge")]
    answered_correct = sum(1 for r in answered if r["verdict"] == labels[r["id"]])
    abstained = [r for r in rows if r["verdict"] == "abstain"]
    refused = sum(1 for r in rows if r["verdict"] == "refused")
    errors = sum(1 for r in rows if r["verdict"] == "error")
    accuracy = round(correct / n, 3) if n else None
    board = {
        "n": n,
        "correct": correct,
        "accuracy": accuracy,
        "answered": len(answered),
        "answered_correct": answered_correct,
        "precision_answered": round(answered_correct / len(answered), 3) if answered else None,
        "abstained": len(abstained),
        "abstain_justified": sum(1 for r in abstained if labels[r["id"]] == "abstain"),
        "refused": refused,
        "errors": errors,
        "wrong": [r["id"] for r in rows if r["verdict"] != labels[r["id"]]],
        "rows": rows,
    }
    board["headline"] = (
        f"{correct}/{n} correct ({accuracy:.0%}); answered {len(answered)}, "
        f"abstained {len(abstained)}, refused {refused}, errors {errors}"
    )
    return board


# --- Try it out (not graded) ---
demo = run_case(client, CASES[1], SHIPMENTS)
if demo:
    print("Live demo case", demo["id"], "->", demo["verdict"], "|", demo["reason"])
    for c in demo["citations"]:
        print(f"   {c['field']:15} line {c['line']}: {c['quote']}")
board = scoreboard(client, CASES, SHIPMENTS)
if board:
    print("\nSCOREBOARD:", board["headline"])
    print("Precision when it answers:", board["precision_answered"])
    print("Wrong:", board["wrong"])
    for r in board["rows"]:
        if r["id"] in board["wrong"]:
            print(f"   {r['id']}: {r['verdict']:10} {r['reason']}")
