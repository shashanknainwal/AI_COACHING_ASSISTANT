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
    lowered = text.lower()
    for keyword, category in RULES.items():
        if keyword in lowered:
            return category
    return None


def chunks(items, size):
    return [items[i:i + size] for i in range(0, len(items), size)]


def build_prompt(batch):
    lines = [PROMPT_HEADER] + [f"{index}. {text}" for index, text in batch]
    return "\n".join(lines)


BATCH_SCHEMA = {
    "type": "object",
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "index": {"type": "integer"},
                    "category": {"type": "string", "enum": CATEGORIES},
                },
                "required": ["index", "category"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["results"],
    "additionalProperties": False,
}


def _label_batch(client, batch):
    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_prompt(batch)}],
        output_config={"format": {"type": "json_schema", "schema": BATCH_SCHEMA}},
    )
    wanted = {index for index, _ in batch}
    found = {}
    if response.stop_reason == "end_turn":
        text = next(b.text for b in response.content if b.type == "text")
        for item in json.loads(text)["results"]:
            if item["index"] in wanted and item["category"] in CATEGORIES:
                found[item["index"]] = item["category"]
    return {index: found.get(index, "other") for index in wanted}


def categorize(client, tickets, batch_size=10):
    labels = [rule_category(t) for t in tickets]
    pending = [(i, t) for i, t in enumerate(tickets) if labels[i] is None]
    for batch in chunks(pending, batch_size):
        for index, category in _label_batch(client, batch).items():
            labels[index] = category
    return labels


def estimate_cost(n, batch_size, tokens_per_ticket=60, overhead=400, output_per_ticket=15):
    if n == 0:
        return 0.0
    calls = math.ceil(n / batch_size)
    input_tokens = calls * overhead + n * tokens_per_ticket
    output_tokens = n * output_per_ticket
    return round(input_tokens * 4 / 1e6 + output_tokens * 20 / 1e6, 4)


# --- Try it out (not graded) ---
labels = categorize(client, TICKETS, batch_size=4)
if labels:
    for ticket, label in zip(TICKETS, labels):
        print(f"{label:<15} {ticket}")
print("\nCost for 50,000 tickets, batch size 1: ", estimate_cost(50_000, 1))
print("Cost for 50,000 tickets, batch size 25:", estimate_cost(50_000, 25))
