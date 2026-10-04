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
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        speaker, sep, said = line.partition(": ")
        if sep:
            turns.append((speaker.strip(), said.strip()))
        elif turns:
            turns[-1] = (turns[-1][0], turns[-1][1] + " " + line)
    return turns


def talk_ratio(turns, speaker="FDE"):
    """Share of all words spoken by `speaker`, rounded to 2 decimals."""
    total = sum(len(t.split()) for _, t in turns)
    mine = sum(len(t.split()) for s, t in turns if s == speaker)
    return round(mine / total, 2) if total else 0.0


def _is_open(question):
    q = question.lower()
    return q.startswith(OPEN_STARTERS) or "walk me through" in q or "tell me about" in q


def question_counts(turns, speaker="FDE"):
    """Return {"open": n, "closed": m} for questions asked by `speaker`."""
    counts = {"open": 0, "closed": 0}
    for s, t in turns:
        if s != speaker:
            continue
        for q in re.findall(r"[^.?!]+\?", t):
            counts["open" if _is_open(q.strip()) else "closed"] += 1
    return counts


def quantified_pains(turns, speaker="FDE"):
    """Sentences from everyone except `speaker` that contain a digit."""
    pains = []
    for s, t in turns:
        if s == speaker:
            continue
        for sentence in re.split(r"(?<=[.!?])\s+", t):
            sentence = sentence.strip()
            if any(ch.isdigit() for ch in sentence):
                pains.append(sentence)
    return pains


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
