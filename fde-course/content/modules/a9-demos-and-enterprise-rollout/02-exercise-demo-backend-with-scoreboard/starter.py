import json
import anthropic

# Loaded for you: client, MODEL, FIELDS, CASES, SHIPMENTS

SYSTEM = (
    "You extract fields from a carrier invoice for Halberd Freight Group's freight-audit team. "
    "For each field return the value and the exact line of the invoice it came from, copied verbatim. "
    "If a field is missing or unreadable, return null for both value and quote."
)

# TODO: a JSON schema for {"invoice_number", "shipment_ref", "total_eur"}, each {"value", "quote"}.
# Structured outputs need "additionalProperties": False on every object.
SCHEMA = None


def extract(client, invoice_text):
    """Endpoint 1: ask Claude for the three fields, each with a verbatim quote.
    Returns {"status": "ok", "fields": {...}}, {"status": "refused", "category": ...}
    or {"status": "error", "detail": ...}."""
    # TODO
    pass


def ground(fields, invoice_text, shipments):
    """Endpoint 2: check every field against the invoice and Halberd's records, in code.
    Returns {"verdict": "match" | "overcharge" | "abstain", "reason": str, "difference_eur": float | None}."""
    # TODO
    pass


def cite(fields, invoice_text):
    """Endpoint 3: [{"field", "line", "quote"}] with 1-based line numbers, in FIELDS order."""
    # TODO
    pass


def run_case(client, case, shipments):
    """Run one invoice through extract, ground and cite.
    Returns {"id", "verdict", "reason", "citations"}; verdict may also be "refused" or "error"."""
    # TODO
    pass


def scoreboard(client, cases, shipments):
    """Honest metrics over every labelled case. Nothing is dropped from the denominator."""
    # TODO
    pass


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
else:
    print("Nothing yet: implement the five functions, then press Run again.")
