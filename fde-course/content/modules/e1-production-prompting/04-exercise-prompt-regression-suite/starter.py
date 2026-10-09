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
    """Turn a value into the form you compare on. None stays None."""
    # TODO
    pass


def score_case(expected, actual):
    """{field: bool} for every field in FIELDS. actual is None when the call failed."""
    # TODO
    pass


def invoice_message(text):
    """The user message for one invoice."""
    # TODO
    pass


def run_suite(client, system_prompt, cases):
    """Run one prompt version over the cases. One row per case: {"id", "actual", "scores", "error"}."""
    # TODO
    pass


def field_accuracy(rows):
    """Accuracy per field plus "all_fields", rounded to 3 decimals."""
    # TODO
    pass


def compare(old_rows, new_rows, critical=CRITICAL_FIELDS, tolerance=0.02):
    """{"deltas", "regressions", "fixes", "verdict", "reasons"} for a prompt change."""
    # TODO
    pass


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
