import json
import anthropic

client = anthropic.Anthropic()
MODEL = "claude-opus-5-5"
FIELDS = ["vendor", "invoice_number", "total", "currency", "due_date"]
CRITICAL_FIELDS = ["total", "currency"]

INVOICE_SCHEMA = {
    "type": "object",
    "properties": {
        "vendor": {"type": "string"},
        "invoice_number": {"type": "string"},
        "total": {"type": "number"},
        "currency": {"type": "string", "enum": ["USD", "EUR", "GBP", "CAD", "CHF"]},
        "due_date": {"anyOf": [{"type": "string", "format": "date"}, {"type": "null"}]},
    },
    "required": ["vendor", "invoice_number", "total", "currency", "due_date"],
    "additionalProperties": False,
}

PROMPT_V1 = """You extract fields from supplier invoices for Tallis Freight's accounts-payable team. Totals and currencies feed the weekly payment run, so leave a field null rather than guess.

<rules>
- due_date is the payment due date, not the invoice date. Use null if the invoice doesn't state one.
- total is the amount payable, including tax.
</rules>"""

# A teammate's rewrite: better vendor names, plus two "helpful" defaults.
PROMPT_V2 = """You extract fields from supplier invoices for Tallis Freight's accounts-payable team. Totals and currencies feed the weekly payment run, so leave a field null rather than guess.

<rules>
- due_date is the payment due date, not the invoice date. If no due date is printed, use 30 days after the invoice date.
- total is the amount payable, including tax.
- If no currency code is printed, use USD.
</rules>

<vendor_rules>
- Use the vendor name as printed in the invoice header, without legal suffixes such as Ltd or Inc.
- Keep "&" as printed.
</vendor_rules>"""

# Golden set: real invoice layouts (anonymized), labelled by the AP team.
GOLDEN = [
    {"id": "G-01", "text": "BRANNOCK TOOLS LTD\nInvoice BT-5521  Date 2026-10-02\nTotal due: GBP 1,200.00\nPayment due 2026-11-01",
     "expected": {"vendor": "Brannock Tools", "invoice_number": "BT-5521", "total": 1200.0, "currency": "GBP", "due_date": "2026-11-01"}},
    {"id": "G-02", "text": "Sorrel & Pike\nInv. no SP-0098, issued 2026-09-20\nAmount payable EUR 86.50, due by 2026-10-20",
     "expected": {"vendor": "Sorrel & Pike", "invoice_number": "SP-0098", "total": 86.5, "currency": "EUR", "due_date": "2026-10-20"}},
    {"id": "G-03", "text": "QUILLON METALS\nInvoice QM-77120 (2026-10-01)\nTotal USD 15,400.00\nDue 2026-12-15",
     "expected": {"vendor": "Quillon Metals", "invoice_number": "QM-77120", "total": 15400.0, "currency": "USD", "due_date": "2026-12-15"}},
    {"id": "G-04", "text": "Harrow Logistics Inc.\nInvoice HL-3301 dated 2026-10-15\nCAD 2,310.40 payable by 2026-11-30",
     "expected": {"vendor": "Harrow Logistics", "invoice_number": "HL-3301", "total": 2310.4, "currency": "CAD", "due_date": "2026-11-30"}},
    {"id": "G-05", "text": "Vantor Office Supply\nReceipt-invoice VOS-118, 2026-10-03\nUSD 412.99 (paid by card, nothing further due)",
     "expected": {"vendor": "Vantor Office Supply", "invoice_number": "VOS-118", "total": 412.99, "currency": "USD", "due_date": None}},
    {"id": "G-06", "text": "Elsted Print Co\nInvoice EP-2290 of 2026-10-01\nTotal €980.00\nPlease pay by 2026-10-31",
     "expected": {"vendor": "Elsted Print Co", "invoice_number": "EP-2290", "total": 980.0, "currency": "EUR", "due_date": "2026-10-31"}},
    {"id": "G-07", "text": "Marrick Labs AG\nRechnung ML-0042, 2026-10-10\nTotal CHF 7'250.00, due 2026-11-15",
     "expected": {"vendor": "Marrick Labs", "invoice_number": "ML-0042", "total": 7250.0, "currency": "CHF", "due_date": "2026-11-15"}},
    {"id": "G-08", "text": "Pellow Catering\nInvoice PC-1187 (event 2026-10-11)\nTo pay: £640.25 by 2026-10-25",
     "expected": {"vendor": "Pellow Catering", "invoice_number": "PC-1187", "total": 640.25, "currency": "GBP", "due_date": "2026-10-25"}},
    {"id": "G-09", "text": "TAMSIN & LIND LLP\nInvoice OL-5510, 2026-10-06\nFees: USD 3,100.00, due 2026-11-05",
     "expected": {"vendor": "Tamsin & Lind", "invoice_number": "OL-5510", "total": 3100.0, "currency": "USD", "due_date": "2026-11-05"}},
    {"id": "G-10", "text": "Rydal Electrical\nInvoice RE-8812, 2026-11-01\nEUR 1,875.60 due 2026-12-01",
     "expected": {"vendor": "Rydal Electrical", "invoice_number": "RE-8812", "total": 1875.6, "currency": "EUR", "due_date": "2026-12-01"}},
]


def normalize(field, value):
    if value is None:
        return None
    if field == "total":
        return round(float(str(value).replace(",", "")), 2)
    if field == "currency":
        return str(value).strip().upper()
    return " ".join(str(value).split()).casefold()


def score_case(expected, actual):
    if actual is None:
        return {f: False for f in FIELDS}
    return {f: normalize(f, expected.get(f)) == normalize(f, actual.get(f)) for f in FIELDS}


def invoice_message(text):
    return f"<invoice>\n{text}\n</invoice>\n\nExtract the invoice fields."


def run_suite(client, system_prompt, cases):
    rows = []
    for case in cases:
        actual, error = None, None
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=4096,
                system=system_prompt,
                messages=[{"role": "user", "content": invoice_message(case["text"])}],
                output_config={"format": {"type": "json_schema", "schema": INVOICE_SCHEMA}},
            )
            if response.stop_reason == "refusal":
                error = "refused"
            elif response.stop_reason == "max_tokens":
                error = "max_tokens"
            else:
                actual = json.loads(next(b.text for b in response.content if b.type == "text"))
        except anthropic.APIError as e:
            error = type(e).__name__
        rows.append({"id": case["id"], "actual": actual, "scores": score_case(case["expected"], actual), "error": error})
    return rows


def field_accuracy(rows):
    n = len(rows)
    if n == 0:
        return {**{f: 0.0 for f in FIELDS}, "all_fields": 0.0}
    out = {f: round(sum(r["scores"][f] for r in rows) / n, 3) for f in FIELDS}
    out["all_fields"] = round(sum(all(r["scores"].values()) for r in rows) / n, 3)
    return out


def compare(old_rows, new_rows, critical=CRITICAL_FIELDS, tolerance=0.02):
    old_acc, new_acc = field_accuracy(old_rows), field_accuracy(new_rows)
    deltas = {k: round(new_acc[k] - old_acc[k], 3) for k in old_acc}
    before = {r["id"]: r["scores"] for r in old_rows}
    regressions, fixes = [], []
    for row in new_rows:
        if row["id"] not in before:
            continue
        for f in FIELDS:
            was, now = before[row["id"]][f], row["scores"][f]
            if was and not now:
                regressions.append(f"{row['id']}:{f}")
            elif now and not was:
                fixes.append(f"{row['id']}:{f}")
    reasons = []
    for f in FIELDS:
        if deltas[f] < -tolerance:
            reasons.append(f"{f} accuracy dropped from {old_acc[f]:.3f} to {new_acc[f]:.3f}")
    for item in regressions:
        case_id, f = item.split(":")
        if f in critical:
            reasons.append(f"critical field {f} regressed on {case_id}")
    return {"deltas": deltas, "regressions": regressions, "fixes": fixes,
            "verdict": "block" if reasons else "ship", "reasons": reasons}


# --- Try it out (not graded) ---
v1 = run_suite(client, PROMPT_V1, GOLDEN)
v2 = run_suite(client, PROMPT_V2, GOLDEN)
if v1 and v2:
    print("v1:", field_accuracy(v1))
    print("v2:", field_accuracy(v2))
    report = compare(v1, v2)
    if report:
        print("\nverdict:", report["verdict"])
        for reason in report["reasons"]:
            print("  -", reason)
        print("regressions:", report["regressions"])
        print("fixes:      ", report["fixes"])
