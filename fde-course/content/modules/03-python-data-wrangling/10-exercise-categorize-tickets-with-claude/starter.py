import json
import math
import anthropic

client = anthropic.Anthropic()
MODEL = "claude-opus-5-5"

CATEGORIES = ["billing", "shipping", "product defect", "account access", "other"]

# Conservative keyword rules: only words that are almost never wrong.
RULES = {
    "invoice": "billing",
    "refund": "billing",
    "tracking number": "shipping",
    "password": "account access",
    "reset my login": "account access",
}

SYSTEM_PROMPT = """You categorize customer support tickets for an industrial parts distributor.
Categories:
- billing: invoices, charges, payments, credits, pricing
- shipping: delivery timing, damaged or missing shipments, carriers
- product defect: parts that are faulty, leak, crack, or don't fit
- account access: logins, portal access, permissions
- other: anything else
Return one result per ticket, using the ticket's number as its index."""

PROMPT_HEADER = "Categorize each ticket into exactly one category."

TICKETS = [
    "Please resend invoice 4471, our AP team can't find it",
    "The relief valve we got last week hisses under pressure",
    "Where is the tracking number for PO 8812?",
    "I was charged twice for the March order",
    "Box arrived soaked and two gauges were cracked",
    "Need a password reset for the ordering portal",
    "Can someone call me about our contract renewal?",
    "Pallet was supposed to arrive Tuesday, still nothing",
    "Requesting a refund for the returned fittings",
    "Locked out of the portal after 2FA change",
    "Hose clamps are the wrong size for 2-inch lines",
    "Do you sponsor the regional trade show this year?",
]


def rule_category(text):
    """Category from the first matching keyword rule, or None."""
    # TODO
    pass


def chunks(items, size):
    """Split items into consecutive lists of at most `size`."""
    # TODO
    pass


def build_prompt(batch):
    """PROMPT_HEADER followed by '<index>. <text>' lines."""
    # TODO
    pass


# TODO: {"results": [{"index": int, "category": one of CATEGORIES}, ...]}
BATCH_SCHEMA = {}


def categorize(client, tickets, batch_size=10):
    """Return one category per ticket: rules first, then Claude in batches."""
    # TODO
    pass


def estimate_cost(n, batch_size, tokens_per_ticket=60, overhead=400, output_per_ticket=15):
    """Estimated USD cost for n tickets on Claude Opus 5.5 ($4 / $20 per million tokens)."""
    # TODO
    pass


# --- Try it out (not graded) ---
labels = categorize(client, TICKETS, batch_size=4)
if labels:
    for ticket, label in zip(TICKETS, labels):
        print(f"{label:<15} {ticket}")
print("\nCost for 50,000 tickets, batch size 1: ", estimate_cost(50_000, 1))
print("Cost for 50,000 tickets, batch size 25:", estimate_cost(50_000, 25))
