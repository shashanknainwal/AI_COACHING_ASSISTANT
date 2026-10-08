# Kestrel Mobile golden set (fictional). 24 support messages sampled from real traffic and
# labelled by two support leads; disagreements were settled by a third. `expected` is the intent.
GOLDEN_SET = [
    {"id": "K-01", "expected": "billing", "text": "Why is my bill $42 higher this month? I didn't change anything."},
    {"id": "K-02", "expected": "billing", "text": "I was charged twice for March, please refund one of them"},
    {"id": "K-03", "expected": "billing", "text": "can i pay my bill with a different card this time"},
    {"id": "K-04", "expected": "billing", "text": "The new plan price showed up but so did the old one. Which am I paying?"},
    {"id": "K-05", "expected": "billing", "text": "What is this 'service fee' line on my invoice?"},
    {"id": "K-06", "expected": "billing", "text": "My autopay failed and now there's a late fee. Can you waive it?"},
    {"id": "K-07", "expected": "network_outage", "text": "No signal at all in downtown Halden since this morning"},
    {"id": "K-08", "expected": "network_outage", "text": "Is there an outage? Calls keep dropping on every tower near me."},
    {"id": "K-09", "expected": "network_outage", "text": "my phone says SOS only, restarted it twice, same thing. whole street has it"},
    {"id": "K-10", "expected": "network_outage", "text": "Data has been down for 3 hours in the Riverside area"},
    {"id": "K-11", "expected": "network_outage", "text": "Is the network down?? Nothing loads and my neighbours on Kestrel have the same problem"},
    {"id": "K-12", "expected": "network_outage", "text": "5G disappeared across the whole city tonight"},
    {"id": "K-13", "expected": "plan_change", "text": "I want to move to the unlimited plan from next month"},
    {"id": "K-14", "expected": "plan_change", "text": "Can I add a second line for my daughter to my plan?"},
    {"id": "K-15", "expected": "plan_change", "text": "Downgrade me to the cheapest plan, I'm paying too much"},
    {"id": "K-16", "expected": "plan_change", "text": "How do I switch from prepaid to a monthly plan?"},
    {"id": "K-17", "expected": "device_support", "text": "My voicemail stopped working after the phone update"},
    {"id": "K-18", "expected": "device_support", "text": "How do I set up wifi calling on my phone?"},
    {"id": "K-19", "expected": "device_support", "text": "the eSIM won't activate on my new phone"},
    {"id": "K-20", "expected": "device_support", "text": "Hotspot turns on but my laptop can't connect to it"},
    {"id": "K-21", "expected": "cancel", "text": "I want to cancel my contract and keep my number"},
    {"id": "K-22", "expected": "cancel", "text": "Close my account. The last bill was the final straw."},
    {"id": "K-23", "expected": "roaming", "text": "I'm in Lisbon and my data isn't working"},
    {"id": "K-24", "expected": "roaming", "text": "Will I be charged extra for using my phone in Canada next week?"},
]

# Share of last month's production traffic per intent. sim_swap_fraud has no golden cases yet.
TRAFFIC_MIX = {
    "billing": 0.30,
    "network_outage": 0.20,
    "plan_change": 0.15,
    "device_support": 0.15,
    "cancel": 0.12,
    "roaming": 0.05,
    "sim_swap_fraud": 0.03,
}

# The system under test is a black box to the eval, as it would be in production.
_ROUTER_OUTPUT = {
    "K-01": "billing", "K-02": "Billing ", "K-03": "billing", "K-04": "plan_change", "K-05": "billing",
    "K-06": "billing", "K-07": "network_outage", "K-08": "network_outage", "K-09": "device_support",
    "K-10": "network_outage", "K-11": TimeoutError("upstream model call timed out after 30s"),
    "K-12": "network_outage", "K-13": "plan_change", "K-14": "plan_change", "K-15": "billing",
    "K-16": "PLAN_CHANGE", "K-17": "device_support", "K-18": "device_support", "K-19": "device_support",
    "K-20": "device_support", "K-21": "cancel", "K-22": "billing", "K-23": "network_outage", "K-24": "roaming",
}
_BY_TEXT = {c["text"]: _ROUTER_OUTPUT[c["id"]] for c in GOLDEN_SET}


def kestrel_router(text):
    """Kestrel's intent router (v3). Returns an intent label; can raise on upstream failures."""
    out = _BY_TEXT.get(text, "billing")
    if isinstance(out, BaseException):
        raise out
    return out
