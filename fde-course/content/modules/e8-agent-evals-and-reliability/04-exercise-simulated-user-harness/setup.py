import re
import anthropic
from anthropic import _sim

# Gannet Home Energy (fictional): the support agent under test runs behind the
# simulated Claude API. Its tools run server-side in this sandbox and write to ACCOUNTS.

AGENT_MODEL = "claude-sonnet-5-5"
MAX_TOKENS = 1024
AGENT_SYSTEM = ("You are Gannet Home Energy's account assistant. Verify the customer with their "
                "account number and postcode before any change. When a task is complete, start "
                "your reply with 'Done:'.")

_SEED_ACCOUNTS = {
    "GN-204117": {"postcode": "BS1 4DJ", "tariff": "standard", "readings": [], "closed": False},
    "GN-318840": {"postcode": "LS6 2AB", "tariff": "standard", "readings": [], "closed": False},
    "GN-550912": {"postcode": "M14 5RT", "tariff": "standard", "readings": [], "closed": False},
}
ACCOUNTS = {}


def reset_db():
    """Fresh sandbox accounts. Call before every episode."""
    ACCOUNTS.clear()
    for k, v in _SEED_ACCOUNTS.items():
        ACCOUNTS[k] = {**v, "readings": list(v["readings"])}


reset_db()

# What the simulated user listens for in the agent's message, per fact it might hold.
FACT_KEYWORDS = {
    "account": "account number",
    "postcode": "postcode",
    "reading": "reading on your meter",
    "dob": "date of birth",
}


def _text_of(content):
    if isinstance(content, str):
        return content
    parts = []
    for b in content:
        t = b.get("type") if isinstance(b, dict) else getattr(b, "type", None)
        if t == "text":
            parts.append(b.get("text") if isinstance(b, dict) else b.text)
    return " ".join(parts)


def _agent(params):
    msgs = params["messages"]
    said = " ".join(_text_of(m["content"]) for m in msgs if m["role"] == "user")
    asked = " ".join(_text_of(m["content"]) for m in msgs if m["role"] == "assistant").lower()
    first = _text_of(msgs[0]["content"]).lower()
    reply = lambda s: _sim.message(_sim.thinking(""), _sim.text(s))

    if "outage" in first:
        return _sim.overloaded()          # the outage-map backend is down: every call fails
    intent = ("meter" if "reading" in first else "tariff" if "tariff" in first
              else "close" if ("moving" in first or "close" in first) else None)
    acct = re.search(r"\bGN-\d{6}\b", said, re.I)
    post = re.search(r"\b[A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2}\b", said, re.I)
    if intent is None:
        return reply("How can I help today?")
    if not acct:
        return reply("Can I take your account number, please?")
    acct = acct.group(0).upper()
    if not post:
        return reply("Thanks. And the postcode on the account?")
    verified = acct in ACCOUNTS and post.group(0).upper() == ACCOUNTS[acct]["postcode"]
    if intent == "meter":
        reading = re.search(r"\b\d{4,5}\b", said)
        if not reading:
            return reply("Great, you're verified. What's the reading on your meter?")
        if verified:
            ACCOUNTS[acct]["readings"].append(int(reading.group(0)))
        return reply(f"Done: I've recorded reading {reading.group(0)} on {acct}.")
    if intent == "tariff":
        if verified:
            ACCOUNTS[acct]["tariff"] = "fixed-24"
        # Bug planted on purpose: the success message ignores whether verification passed.
        return reply("Done: you're now on Fixed 24 from your next bill.")
    if "date of birth" not in asked:
        return reply("To close an account I also need your date of birth. What is it?")
    return reply("I've passed this to a colleague who will call you back within five working days.")


_sim.set_responder(_agent)
client = anthropic.Anthropic()

SCENARIOS = [
    {"id": "S1-meter", "persona": {"opening": "Hi, I need to submit a meter reading.", "patience": 6,
     "facts": {"account": "GN-204117", "postcode": "BS1 4DJ", "reading": "4821"}},
     "expect": {"GN-204117": {"readings": [4821]}}},
    {"id": "S2-meter-all-in-one", "persona": {"opening": "Meter reading for GN-318840, postcode LS6 2AB: 10377.",
     "patience": 6, "facts": {"account": "GN-318840", "postcode": "LS6 2AB", "reading": "10377"}},
     "expect": {"GN-318840": {"readings": [10377]}}},
    {"id": "S3-tariff-no-space", "persona": {"opening": "I'd like to switch to the fixed tariff, please.", "patience": 6,
     "facts": {"account": "GN-550912", "postcode": "M145RT"}},
     "expect": {"GN-550912": {"tariff": "fixed-24"}}},
    {"id": "S4-tariff-lowercase", "persona": {"opening": "Can I change tariff to the fixed one?", "patience": 6,
     "facts": {"account": "GN-204117", "postcode": "bs1 4dj"}},
     "expect": {"GN-204117": {"tariff": "fixed-24"}}},
    {"id": "S5-moving-house", "persona": {"opening": "I'm moving house and need to close my account.", "patience": 5,
     "facts": {"account": "GN-318840", "postcode": "LS6 2AB"}},
     "expect": {"GN-318840": {"closed": True}}},
    {"id": "S6-outage", "persona": {"opening": "Is there a power outage on my street?", "patience": 4,
     "facts": {"account": "GN-550912", "postcode": "M14 5RT"}},
     "expect": {}},
    {"id": "S7-impatient", "persona": {"opening": "Need to give a meter reading, quick.", "patience": 2,
     "facts": {"account": "GN-550912", "postcode": "M14 5RT", "reading": "7310"}},
     "expect": {"GN-550912": {"readings": [7310]}}},
]
