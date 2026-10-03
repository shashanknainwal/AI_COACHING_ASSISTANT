import re

TRANSCRIPT = """FDE: Thanks for joining. Could you walk me through how a new claim gets processed today?
Marcus (Claims Ops): Sure. Claims come in by email, about 900 a week. An adjuster reads each one
and keys it into ClaimsPro by hand.
FDE: How long does that take per claim?
Marcus (Claims Ops): Around 25 minutes for a simple auto claim. Complex ones can take an hour.
Do you want the breakdown by type?
FDE: Yes please. Do you track that anywhere?
Marcus (Claims Ops): We have a spreadsheet. Honestly the bigger problem is rework. About 18% of claims
get sent back because a field was keyed wrong.
FDE: Tell me about the last claim that got sent back.
Marcus (Claims Ops): Yesterday a policy number was off by one digit. The payout was delayed 6 days
and the customer called three times.
FDE: What happens downstream when a payout is late?
Joan (VP Claims): That's my world. Late payouts drive complaints to the regulator. We had 14 last quarter.
Our target is under 5.
FDE: Is the regulator number the one you report to the board?
Joan (VP Claims): It is. That and cost per claim.
"""

OPEN_STARTERS = ("what", "how", "why", "walk me", "tell me", "describe", "who", "which", "where", "when")


def parse_transcript(text):
    """Return a list of (speaker, text) tuples."""
    turns = []
    # TODO
    return turns


def talk_ratio(turns, speaker="FDE"):
    """Share of all words spoken by `speaker`, rounded to 2 decimals."""
    # TODO
    pass


def question_counts(turns, speaker="FDE"):
    """Return {"open": n, "closed": m} for questions asked by `speaker`."""
    # TODO
    pass


def quantified_pains(turns, speaker="FDE"):
    """Sentences from everyone except `speaker` that contain a digit."""
    # TODO
    pass


# --- Try it out (not graded) ---
turns = parse_transcript(TRANSCRIPT)
for who, said in turns:
    print(f"{who:>20}: {said[:70]}")
print()
print("FDE talk ratio:", talk_ratio(turns))
print("Questions:", question_counts(turns))
print("Quantified pains:")
for p in quantified_pains(turns) or []:
    print("  -", p)
