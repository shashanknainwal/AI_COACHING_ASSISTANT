# Gannet Home Energy (fictional) is launching a Home Move agent. There is no traffic
# yet, so the eval starts from 8 real messages from the existing support queue,
# rewritten as templates by the support leads (account numbers and amounts removed).

SEEDS = [
    {"id": "SD1", "intent": "final_reading", "amounts": None,
     "template": "I'm moving out on Friday. How do I give you a final meter reading for {account}?"},
    {"id": "SD2", "intent": "final_reading", "amounts": None,
     "template": "Moving house next week, account {account}. Do you need a reading from me on the day?"},
    {"id": "SD3", "intent": "close_account", "amounts": None,
     "template": "Please close account {account}, I've sold the flat and the new owners move in Monday."},
    {"id": "SD4", "intent": "close_account", "amounts": None,
     "template": "My mum has passed away and I need to close her account {account}. What do you need from me?"},
    {"id": "SD5", "intent": "refund_balance", "amounts": [12, 38, 74, 115],
     "template": "After my final bill on {account} I was ${amount} in credit. When will that be refunded?"},
    {"id": "SD6", "intent": "refund_balance", "amounts": [9, 27, 60],
     "template": "You still owe me ${amount} from my old place, account {account}. Can you send it to my new address?"},
    {"id": "SD7", "intent": "open_new", "amounts": None,
     "template": "I'm moving into a new build and want to keep Gannet. Can you move {account} to my new address?"},
    {"id": "SD8", "intent": "open_new", "amounts": None,
     "template": "Can I take my EV Night tariff with me when I move? Account {account}."},
]

TONES = {
    "neutral": "{text}",
    "angry": "This is the third time I've asked. {text} Sort it out.",
    "polite": "Hi there, sorry to bother you. {text} Thanks so much.",
    "terse": "{text}",          # terse: keep only the sentence that holds the account number
}

CHANNELS = ["chat", "email", "sms"]

# Real messages already in the frozen test set. Synthetic cases must not leak into it.
HELD_OUT = [
    "Please close account GN-771203, I've sold the flat and the new owners move in Monday.",
    "After my final bill on GN-118845 I was $38 in credit. When will that be refunded?",
]
